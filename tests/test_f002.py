"""F002 controlled contrasts, invariants, invalid atomicity and deterministic replay."""
import csv
import json
from pathlib import Path
import random
import tempfile
import unittest
from xml.etree import ElementTree as ET

from soma.f002 import Cell, Event, LedgerState, apply_event, new_ledger, parse_config, plot_svg, save_run


def base(*, a=10_000_000, b=2_000_000):
    return new_ledger([Cell("A", 20_000_000, a), Cell("B", 20_000_000, b)])


def make_config(experiment_id, events):
    return {"schema_version": "f002.v1", "experiment_id": experiment_id, "seed": 1,
            "cells": [{"cell_id": "A", "capacity_uj": 20_000_000, "balance_uj": 10_000_000},
                      {"cell_id": "B", "capacity_uj": 20_000_000, "balance_uj": 2_000_000}],
            "events": events}


class F002Tests(unittest.TestCase):
    def test_a_rest(self):
        state = base()
        self.assertEqual(state.event_index, 0)
        self.assertEqual(state.residual_uj, 0)
        self.assertEqual((state.cell("A").balance_uj, state.cell("B").balance_uj), (10_000_000, 2_000_000))

    def test_b_acquire(self):
        original = base()
        new, entry = apply_event(original, Event("acquire", 5_000_000, target_id="A"))
        self.assertEqual(new.cell("A").balance_uj, 15_000_000)
        self.assertEqual(new.acquired_uj, 5_000_000)
        self.assertEqual(entry.external_in_uj, 5_000_000)
        self.assertEqual(new.residual_uj, 0)
        self.assertEqual(original.cell("A").balance_uj, 10_000_000)

    def test_c_spend(self):
        new, entry = apply_event(base(), Event("spend", 3_000_000, source_id="A"))
        self.assertEqual(new.cell("A").balance_uj, 7_000_000)
        self.assertEqual(new.spent_uj, 3_000_000)
        self.assertEqual(entry.external_out_uj, 3_000_000)
        self.assertEqual(new.residual_uj, 0)

    def test_d_transfer(self):
        old = base()
        new, entry = apply_event(old, Event("transfer", 3_000_000, "A", "B", 8000))
        self.assertEqual((new.cell("A").balance_uj, new.cell("B").balance_uj), (7_000_000, 4_400_000))
        self.assertEqual((entry.received_uj, entry.loss_uj, entry.residual_uj), (2_400_000, 600_000, 0))
        self.assertEqual(new.acquired_uj, 0)
        self.assertEqual(new.spent_uj, 0)
        self.assertEqual(old.event_index, 0)

    def test_e_invalid_events_cannot_mutate_old_state(self):
        old = base()
        bad = [
            Event("spend", 10_000_001, source_id="A"),
            Event("acquire", 11_000_000, target_id="A"),
            Event("transfer", 3_000_000, "A", "A", 8000),
            Event("transfer", 3_000_000, "A", "B", -1),
            Event("transfer", 3_000_000, "A", "B", 10_001),
            Event("transfer", 3_000_000, "A", "B", 80.0),
            Event("transfer", 3_000_000, "A", "absent", 8000),
            Event("transfer", 3_000_000, "absent", "B", 8000),
            Event("spend", -5, source_id="A"),
            Event("spend", 0, source_id="A"),
            Event("spend", True, source_id="A"),
            Event("spend", 1.5, source_id="A"),
            Event("spend", 10**15 + 1, source_id="A"),
            Event("spend", 1, source_id="A", target_id="B"),
            Event("acquire", 1, source_id="A", target_id="B"),
            Event("acquire", 1, target_id="B", eta_bps=10000),
            Event("unknown", 1, target_id="B"),
        ]
        original_repr = repr(old)
        for bad_event in bad:
            with self.subTest(bad_event=bad_event), self.assertRaises(ValueError):
                apply_event(old, bad_event)
            self.assertEqual(repr(old), original_repr)
            self.assertEqual(old.event_index, 0)

    def test_receiver_capacity_overflow_is_atomic(self):
        state = base(b=19_000_000)
        with self.assertRaises(ValueError):
            apply_event(state, Event("transfer", 3_000_000, "A", "B", 8000))
        self.assertEqual(state.cell("A").balance_uj, 10_000_000)
        self.assertEqual(state.cell("B").balance_uj, 19_000_000)
        self.assertEqual(state.residual_uj, 0)

    def test_zero_full_and_quantization(self):
        state = base()
        after, entry = apply_event(state, Event("transfer", 3, "A", "B", 5000))
        self.assertEqual((entry.received_uj, entry.loss_uj), (1, 2))
        split = state
        for _ in range(3):
            split, each = apply_event(split, Event("transfer", 1, "A", "B", 5000))
            self.assertEqual((each.received_uj, each.loss_uj), (0, 1))
        self.assertEqual(after.cell("B").balance_uj - state.cell("B").balance_uj, 1)
        self.assertEqual(split.cell("B").balance_uj - state.cell("B").balance_uj, 0)
        self.assertEqual((after.residual_uj, split.residual_uj), (0, 0))
        state_0, e0 = apply_event(state, Event("transfer", 1, "A", "B", 0))
        self.assertEqual((e0.received_uj, e0.loss_uj, state_0.residual_uj), (0, 1, 0))
        state_100, e100 = apply_event(state, Event("transfer", 1, "A", "B", 10_000))
        self.assertEqual((e100.received_uj, e100.loss_uj, state_100.residual_uj), (1, 0, 0))

    def test_valid_boundary_balances(self):
        state = new_ledger([Cell("A", 2, 2), Cell("B", 2, 0)])
        state, _ = apply_event(state, Event("transfer", 2, "A", "B", 10000))
        self.assertEqual((state.cell("A").balance_uj, state.cell("B").balance_uj), (0, 2))
        self.assertEqual(state.residual_uj, 0)

    def test_malformed_state_and_config(self):
        with self.assertRaises(ValueError):
            new_ledger([Cell("A", 1, 1), Cell("A", 1, 1)])
        with self.assertRaises(ValueError):
            Cell("A", 10, 11)
        with self.assertRaises(ValueError):
            Cell("A", 10, -1)
        with self.assertRaises(ValueError):
            Cell("A", True, 0)
        with self.assertRaises(ValueError):
            LedgerState((Cell("A", 10, 5),), initial_total_uj=6)
        config = make_config("bad", [{"kind": "transfer", "source_id": "A", "target_id": "B", "amount_uj": 1, "eta_bps": 8000}])
        for extra in ({"unexpected": 1}, {"seed": 1.0}, {"schema_version": "f001.v1"}, {"events": "bad"}):
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                parse_config({**config, **extra})
        for bad_cell in ({"cell_id": "A", "capacity_uj": 20, "balance_uj": 2.5},
                         {"cell_id": "A", "capacity_uj": 20, "balance_uj": 2, "oops": 1}):
            with self.assertRaises(ValueError):
                parse_config({**config, "cells": [bad_cell]})

    def test_f_deterministic_replay_and_random_valid_transactions(self):
        rng = random.Random(20261014)
        state = new_ledger([Cell(str(i), 10**10, 10**9) for i in range(8)])
        operations = []
        for _ in range(500):
            index = rng.randrange(8)
            source = str(index)
            kind = rng.choice(("acquire", "spend", "transfer"))
            if kind == "acquire":
                event = Event(kind, rng.randint(1, 100_000), target_id=source)
            elif kind == "spend":
                event = Event(kind, rng.randint(1, 100_000), source_id=source)
            else:
                target = str((index + rng.randint(1, 7)) % 8)
                event = Event(kind, rng.randint(1, 100_000), source, target, rng.randint(0, 10000))
            state, entry = apply_event(state, event)
            self.assertEqual(state.residual_uj, 0)
            self.assertTrue(all(0 <= c.balance_uj <= c.capacity_uj for c in state.cells))
            operations.append((event, entry))
        replay = new_ledger([Cell(str(i), 10**10, 10**9) for i in range(8)])
        for event, expected_entry in operations:
            replay, entry = apply_event(replay, event)
            self.assertEqual(entry, expected_entry)
        self.assertEqual(state, replay)

    def test_preregistered_controls_reject_corruption_under_python_optimized(self):
        # A passing -O run alone is insufficient: inject incorrect observations
        # and require the suite's acceptance checks to raise at runtime.
        import subprocess
        import sys
        script = """
from copy import deepcopy
from experiments.F002.run_suite import validate_expected_results

if __debug__:
    raise RuntimeError("expected Python optimized mode")
good = {
    "A-rest": {
        "final_balances_uj": {"A": 10_000_000},
        "acquired_uj": 0, "spent_uj": 0, "loss_uj": 0,
        "residual_uj": 0, "event_count": 0,
    },
    "B-acquire": {
        "final_balances_uj": {"A": 15_000_000},
        "acquired_uj": 5_000_000, "spent_uj": 0, "loss_uj": 0,
        "residual_uj": 0, "event_count": 1,
    },
    "C-spend": {
        "final_balances_uj": {"A": 7_000_000},
        "acquired_uj": 0, "spent_uj": 3_000_000, "loss_uj": 0,
        "residual_uj": 0, "event_count": 1,
    },
    "D-transfer": {
        "final_balances_uj": {"A": 7_000_000, "B": 4_400_000},
        "acquired_uj": 0, "spent_uj": 0, "loss_uj": 600_000,
        "residual_uj": 0, "event_count": 1,
    },
    "F-bulk": {
        "final_balances_uj": {"A": 9_999_997, "B": 2_000_001},
        "acquired_uj": 0, "spent_uj": 0, "loss_uj": 2,
        "residual_uj": 0, "event_count": 1,
    },
    "F-split": {
        "final_balances_uj": {"A": 9_999_997, "B": 2_000_000},
        "acquired_uj": 0, "spent_uj": 0, "loss_uj": 3,
        "residual_uj": 0, "event_count": 3,
    },
}
validate_expected_results(good)
bad_cases = []
for name in ("A-rest", "B-acquire", "C-spend"):
    bad = deepcopy(good)
    bad[name]["final_balances_uj"]["A"] += 1
    bad_cases.append((name, bad))
bad = deepcopy(good)
bad["D-transfer"]["final_balances_uj"]["B"] += 1
bad_cases.append(("D", bad))
bad = deepcopy(good)
bad["F-bulk"]["final_balances_uj"]["B"] -= 1
bad_cases.append(("F", bad))
bad = deepcopy(good)
bad["D-transfer"]["residual_uj"] = 1
bad_cases.append(("residual", bad))

# These mutations keep the original bulk-minus-split B delta at 1 µJ.
# The earlier delta-only validator incorrectly accepted them.
bad = deepcopy(good)
for name in ("F-bulk", "F-split"):
    bad[name]["final_balances_uj"]["B"] += 1
bad_cases.append(("F-paired-B-shift", bad))
bad = deepcopy(good)
for name in ("F-bulk", "F-split"):
    bad[name]["final_balances_uj"]["A"] += 1
bad_cases.append(("F-paired-A-shift", bad))
bad = deepcopy(good)
bad["F-bulk"]["loss_uj"] += 1
bad_cases.append(("F-bulk-loss", bad))
bad = deepcopy(good)
bad["F-split"]["loss_uj"] += 1
bad_cases.append(("F-split-loss", bad))

# Probe every reported A-F manifest measurement in optimized mode,
# including unchanged-zero counters and both cells' absolute balances.
for name, outcome in good.items():
    for field in ("acquired_uj", "spent_uj", "loss_uj", "residual_uj", "event_count"):
        bad = deepcopy(good)
        bad[name][field] += 1
        bad_cases.append((f"{name}-{field}", bad))
    for cell_id in outcome["final_balances_uj"]:
        bad = deepcopy(good)
        bad[name]["final_balances_uj"][cell_id] += 1
        bad_cases.append((f"{name}-balance-{cell_id}", bad))

for name, bad in bad_cases:
    try:
        validate_expected_results(bad)
    except AssertionError:
        continue
    raise RuntimeError(f"{name} invalid result accepted under -O")
"""
        completed = subprocess.run(
            [sys.executable, "-O", "-c", script],
            capture_output=True, text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_suite_evidence_matches_registered_conditions(self):
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "suite"
            completed = subprocess.run(
                [sys.executable, "-m", "experiments.F002.run_suite", "--output-dir", str(folder)],
                capture_output=True, text=True, check=True,
            )
            summary = json.loads(completed.stdout)
            self.assertEqual(summary["invalid_control_count"], 13)
            for name, expected in (("A-rest", 10_000_000),
                                   ("B-acquire", 15_000_000),
                                   ("C-spend", 7_000_000)):
                conf = json.loads((folder / name / "config.json").read_text())
                self.assertEqual(len(conf["cells"]), 1)
                self.assertEqual(conf["cells"][0]["cell_id"], "A")
                self.assertEqual(summary["runs"][name]["final_balances_uj"], {"A": expected})
            for name, expected_b, expected_loss in (("F-bulk", 2_000_001, 2),
                                                    ("F-split", 2_000_000, 3)):
                observation = summary["runs"][name]
                self.assertEqual(observation["final_balances_uj"],
                                 {"A": 9_999_997, "B": expected_b})
                self.assertEqual(observation["loss_uj"], expected_loss)
                self.assertEqual(observation["residual_uj"], 0)
            self.assertEqual(summary["runs"]["B-acquire"]["acquired_uj"], 5_000_000)
            self.assertEqual(summary["runs"]["C-spend"]["spent_uj"], 3_000_000)
            self.assertEqual(summary["runs"]["D-transfer"]["loss_uj"], 600_000)
            self.assertEqual(summary["runs"]["F-split"]["event_count"], 3)
            for observation in summary["runs"].values():
                self.assertEqual(observation["residual_uj"], 0)
                self.assertEqual(
                    set(observation),
                    {"final_balances_uj", "acquired_uj", "spent_uj",
                     "loss_uj", "residual_uj", "event_count"},
                )
            cases = json.loads((folder / "E-invalid-events.json").read_text())["cases"]
            self.assertIn("fractional_amount", {case["case"] for case in cases})
            self.assertIn("fractional_efficiency", {case["case"] for case in cases})
            self.assertIn("nonfinite_amount", {case["case"] for case in cases})
            self.assertTrue(all(c["rejected"] and c["state_unchanged"] for c in cases))
            svg = (folder / "F-split" / "energy.svg").read_text()
            self.assertIn("<polyline", svg)
            self.assertIn("event 3:", svg)
            self.assertIn("transfer loss: 3", svg)
            manifest = json.loads((folder / "D-transfer" / "manifest.json").read_text())
            self.assertEqual(type(manifest["python_code_git_dirty"]) in (bool, type(None)), True)
            self.assertEqual(len(manifest["python_code_sha256"]), 64)

    def test_svg_experiment_id_xml10_character_contract(self):
        # Valid XML 1.0 content must remain loadable by an independent XML parser.
        valid_ids = ("F002-検証", 'F002-"&<>', "F002-🐙",
                     "tab" + chr(9) + "line" + chr(10) + "next")
        for experiment_id in valid_ids:
            with self.subTest(valid=repr(experiment_id)):
                conf = make_config(experiment_id, [])
                state, events = parse_config(conf)
                self.assertEqual(events, [])
                ET.fromstring(plot_svg([state], experiment_id))
                with tempfile.TemporaryDirectory() as tmp:
                    path = Path(tmp) / "valid"
                    save_run(conf, path)
                    self.assertEqual(ET.parse(path / "energy.svg").getroot().tag,
                                     "{http://www.w3.org/2000/svg}svg")
                    self.assertEqual(json.loads((path / "manifest.json").read_text())["experiment_id"],
                                     experiment_id)

        # XML escaping does NOT remove forbidden characters. Reject before
        # creating even a partial artifact directory.
        invalid_ids = ("bad" + chr(0) + "id", "bad" + chr(1) + "id",
                       "bad" + chr(11) + "id", "bad" + chr(0xD800) + "id",
                       "bad" + chr(0xDFFF) + "id", "bad" + chr(0xFFFE),
                       "bad" + chr(0xFFFF))
        for experiment_id in invalid_ids:
            with self.subTest(invalid=ascii(experiment_id)):
                conf = make_config(experiment_id, [])
                with self.assertRaisesRegex(ValueError, "experiment_id"):
                    parse_config(conf)
                with tempfile.TemporaryDirectory() as tmp:
                    path = Path(tmp) / "must-not-exist"
                    with self.assertRaises(ValueError):
                        save_run(conf, path)
                    self.assertFalse(path.exists())

    def test_suite_f_replay_raw_artifacts_are_identical(self):
        import subprocess
        import sys
        import hashlib
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "suite"
            completed = subprocess.run(
                [sys.executable, "-m", "experiments.F002.run_suite",
                 "--output-dir", str(folder)],
                capture_output=True, text=True, check=True,
            )
            report = json.loads((folder / "comparison.json").read_text())
            self.assertEqual(json.loads(completed.stdout), report)
            for name in ("F-bulk", "F-split"):
                proof = report["f_replay_checks"][name]
                self.assertTrue(proof["same_config"])
                self.assertTrue(proof["byte_identical"])
                self.assertEqual(proof["replay_run"], name + "-replay")
                expected = {"config.json", "events.csv", "balances.csv",
                            "energy.svg", "manifest.json"}
                self.assertEqual(set(proof["matching_artifact_sha256"]), expected)
                for filename in expected:
                    a = (folder / name / filename).read_bytes()
                    b = (folder / proof["replay_run"] / filename).read_bytes()
                    self.assertEqual(a, b)
                    self.assertEqual(
                        proof["matching_artifact_sha256"][filename],
                        hashlib.sha256(a).hexdigest(),
                    )
                original = json.loads((folder / name / "manifest.json").read_text())
                replay = json.loads(
                    (folder / proof["replay_run"] / "manifest.json").read_text()
                )
                self.assertEqual(original, replay)
                self.assertEqual(original["residual_uj"], 0)
                self.assertEqual(original["event_count"], 1 if name == "F-bulk" else 3)

    def test_save_manifest_csv_and_no_overwrite(self):
        conf = make_config("D-transfer", [{"kind": "transfer", "source_id": "A", "target_id": "B", "amount_uj": 3_000_000, "eta_bps": 8000}])
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "D"
            manifest = save_run(conf, folder)
            self.assertEqual(manifest["final_balances_uj"], {"A": 7_000_000, "B": 4_400_000})
            self.assertEqual(manifest["residual_uj"], 0)
            self.assertEqual(len(manifest["python_code_sha256"]), 64)
            self.assertIn("python_code_git_dirty", manifest)
            self.assertEqual(set(manifest["artifacts"]), {"config.json", "events.csv", "balances.csv", "energy.svg"})
            with (folder / "events.csv").open() as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(len(rows), 1)
            self.assertEqual(int(rows[0]["loss_uj"]), 600_000)
            with (folder / "balances.csv").open() as f:
                self.assertEqual(len(list(csv.DictReader(f))), 4)
            self.assertIn("D-transfer", (folder / "energy.svg").read_text())
            with self.assertRaises(FileExistsError):
                save_run(conf, folder)
            self.assertEqual(json.loads((folder / "manifest.json").read_text())["seed"], 1)


if __name__ == "__main__":
    unittest.main()
