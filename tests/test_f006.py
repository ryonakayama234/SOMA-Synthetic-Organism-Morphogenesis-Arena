"""F006 preregistered behavior, all-rows oracle, and adversarial evidence tests."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest

from soma.f005 import Config
from experiments.F006.diagnostics import (
    DTS, REFERENCES, audit_suite, sha,
)
from experiments.F006.run_suite import build_settings, identical_files, run


class F006Tests(unittest.TestCase):
    def test_frozen_plan_changes_only_dt_within_each_case(self):
        settings = build_settings()
        self.assertEqual(len(settings), 15)
        for case, dts in DTS.items():
            keys = ["%s-dt-%02d" % (case, i) for i in range(len(dts))]
            raws = [dict(settings[key]) for key in keys]
            self.assertEqual([r["dt_s"] for r in raws], list(dts))
            for raw in raws:
                Config.from_dict(raw)
                raw.pop("experiment_id")
                raw.pop("dt_s")
            self.assertTrue(all(raw == raws[0] for raw in raws))
        self.assertEqual(REFERENCES["B"][2][2], 281250)

    def test_all_preregistered_A_E_and_independent_audit(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / "evidence"
            manifest = run(folder)
            self.assertEqual(manifest["runs"], 15)
            self.assertEqual(manifest["verdict"], "supported")
            audit = audit_suite(folder, build_settings())
            self.assertEqual(audit["integer_residual_uj"], 0)
            with (folder / "comparison.csv").open(encoding="utf-8", newline="") as fp:
                comparison = list(csv.DictReader(fp))
            self.assertEqual(len(comparison), 15)
            self.assertEqual([int(r["spent_uj"]) for r in comparison
                              if r["case_id"] == "C"], [1, 10, 100])
            self.assertEqual([int(r["accepted_steps"]) for r in comparison
                              if r["case_id"] == "B"], [0, 1, 3])
            self.assertEqual([float(r["final_x_m"]) for r in comparison
                              if r["case_id"] == "A"], [1., .75, .625])
            diag = json.loads((folder / "diagnostics.json").read_text())
            self.assertEqual(diag["verdict"], "supported")
            self.assertEqual(diag["comparisons"]["A"]["observed_error_ratios"],
                             [2., 2.])
            self.assertTrue(all(d["integer_balance_residual_uj"] == 0
                                for d in diag["runs"]))

    def test_byte_replay_all_artifacts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            # Fix metadata once, just like the public CLI, to exclude host drift.
            identity = {"git_commit": None, "git_dirty": None,
                        "f005_sha256": "snapshot", "f001_sha256": "snapshot",
                        "f002_sha256": "snapshot"}
            run(root / "first", identity=identity)
            run(root / "second", identity=identity)
            self.assertTrue(identical_files(root / "first", root / "second"))

    def test_invalid_config_does_not_create_evidence(self):
        valid = next(iter(build_settings().values()))
        invalids = [
            {"dt_s": 0.}, {"dt_s": -1.}, {"dt_s": 1. / 3.},
            {"dt_s": float("nan")}, {"dt_s": float("inf")},
            {"dt_s": True}, {"mass_kg": 0.},
            {"initial_balance_uj": -1}, {"capacity_uj": 0},
            {"duration_s": .3, "dt_s": .2},
        ]
        for changes in invalids:
            with self.subTest(changes=changes):
                with self.assertRaises((ValueError, TypeError)):
                    Config.from_dict({**valid, **changes})
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "evidence"
            output.mkdir()
            sentinel = output / "sentinel"
            sentinel.write_bytes(b"unchanged")
            with self.assertRaises(FileExistsError):
                run(output)
            self.assertEqual(sentinel.read_bytes(), b"unchanged")

    def test_raw_motion_tampering_even_with_recomputed_sha(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "run"
            run(root)
            victim = root / "B-dt-01"
            state = victim / "states.csv"
            original = state.read_text(encoding="utf-8")
            # Alter one physical observation, then fake a matching F005 digest.
            lines = original.splitlines(keepends=True)
            fields = lines[-1].split(",")
            fields[2] = "123456"
            lines[-1] = ",".join(fields)
            state.write_text("".join(lines), encoding="utf-8")
            manifest_path = victim / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["artifacts"]["states.csv"] = sha(state)
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises((AssertionError, ValueError)):
                audit_suite(root, build_settings())

    def test_comparison_tampering_even_with_recomputed_sha(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "run"
            run(root)
            target = root / "comparison.csv"
            raw = target.read_text(encoding="utf-8")
            target.write_text(raw.replace("integration", "undetermined", 1),
                              encoding="utf-8")
            manifest_path = root / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["artifacts"]["comparison.csv"] = sha(target)
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises((AssertionError, ValueError)):
                audit_suite(root, build_settings())

    def test_suite_source_provenance_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "run"
            run(root)
            source = root / "suite_source.py"
            source.write_bytes(source.read_bytes() + b"\n# forged\n")
            manifest_path = root / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["suite_sha256"] = sha(source)
            manifest["artifacts"]["suite_source.py"] = sha(source)
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises((AssertionError, ValueError)):
                audit_suite(root, build_settings())

    def test_sweep_condition_mix_even_after_manifest_resigning(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "run"
            run(root)
            sweep_path = root / "sweep.json"
            sweep = json.loads(sweep_path.read_text(encoding="utf-8"))
            sweep["runs"]["A-dt-00"]["mass_kg"] = 2.
            sweep_path.write_text(json.dumps(sweep), encoding="utf-8")
            manifest_path = root / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["artifacts"]["sweep.json"] = sha(sweep_path)
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises((AssertionError, ValueError)):
                audit_suite(root, build_settings())

    def test_full_byte_replay_detects_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run(root / "first")
            run(root / "second")
            self.assertTrue(identical_files(root / "first", root / "second"))
            target = root / "second" / "A-dt-00" / "states.csv"
            target.write_bytes(target.read_bytes() + b"\n")
            self.assertFalse(identical_files(root / "first", root / "second"))


if __name__ == "__main__":
    unittest.main()
