"""F002 controlled contrasts, invariants, invalid atomicity and deterministic replay."""
import csv
import json
from pathlib import Path
import random
import tempfile
import unittest

from soma.f002 import Cell, Event, LedgerState, apply_event, new_ledger, parse_config, save_run


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

    def test_save_manifest_csv_and_no_overwrite(self):
        conf = make_config("D-transfer", [{"kind": "transfer", "source_id": "A", "target_id": "B", "amount_uj": 3_000_000, "eta_bps": 8000}])
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "D"
            manifest = save_run(conf, folder)
            self.assertEqual(manifest["final_balances_uj"], {"A": 7_000_000, "B": 4_400_000})
            self.assertEqual(manifest["residual_uj"], 0)
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
