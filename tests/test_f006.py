"""F006 preregistered behavior, all-rows oracle, and adversarial evidence tests."""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from soma.f005 import Config, provenance
from experiments.F006.diagnostics import (
    DTS, REFERENCES, audit_suite, sha,
)
from experiments.F006.run_suite import build_settings, identical_files, run, run_pair
from experiments.F006 import run_suite as runner


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
            self.assertEqual(diag["classification_scope"], "fixed_preregistered_controls_only")
            self.assertIsNone(diag["causal_attribution"])
            self.assertEqual(comparison[0]["expected_classification"], "integration")
            self.assertEqual(comparison[0]["signature_matches_reference"], "True")
            self.assertNotIn("classification", comparison[0])

    def test_byte_replay_all_artifacts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            # Fix metadata once, just like the public CLI, to exclude host drift.
            identity = provenance()
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

    def test_suite_metadata_and_reference_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "run"
            run(root)
            manifest_path = root / "manifest.json"
            original = manifest_path.read_bytes()
            for key, value in {"source_model": "wrong", "sweep_id": "wrong", "seed": 42,
                               "git_commit": "0"*40, "git_dirty": 0,
                               "f005_sha256": "0"*64}.items():
                with self.subTest(key=key):
                    m = json.loads(original)
                    m[key] = value
                    manifest_path.write_text(json.dumps(m))
                    with self.assertRaises(ValueError):
                        audit_suite(root, build_settings())
            manifest_path.write_bytes(original)
            sweep_path = root / "sweep.json"
            sweep_original = sweep_path.read_bytes()
            for key in ("reference_id", "sweep_id"):
                with self.subTest(key=key):
                    sweep = json.loads(sweep_original)
                    sweep[key] = "wrong"
                    sweep_path.write_text(json.dumps(sweep))
                    m = json.loads(original)
                    m["artifacts"]["sweep.json"] = sha(sweep_path)
                    manifest_path.write_text(json.dumps(m))
                    with self.assertRaises(ValueError):
                        audit_suite(root, build_settings())

    def test_dependency_hash_tampering_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "run"
            run(root)
            path = root / "manifest.json"
            original = path.read_bytes()
            for source in ("experiments/F006/diagnostics.py", "experiments/F005/run_suite.py"):
                with self.subTest(source=source):
                    m = json.loads(original)
                    m["source_hashes"][source] = "0"*64
                    path.write_text(json.dumps(m))
                    with self.assertRaises(ValueError):
                        audit_suite(root, build_settings())

    def test_run_provenance_cannot_be_hidden_by_resigning_summaries(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "run"
            run(root)
            path = root / "A-dt-00" / "manifest.json"
            run_original = path.read_bytes()
            for key, value in {"git_commit": "0"*40, "suite_sha256": "0"*64,
                               "f001_sha256": "0"*64, "model": "wrong"}.items():
                with self.subTest(key=key):
                    m = json.loads(run_original)
                    m[key] = value
                    path.write_text(json.dumps(m))
                    dp = root / "diagnostics.json"
                    diagnosis = json.loads(dp.read_text())
                    diagnosis["runs"][0]["artifacts"]["manifest.json"] = sha(path)
                    dp.write_text(json.dumps(diagnosis))
                    mp = root / "manifest.json"
                    suite_manifest = json.loads(mp.read_text())
                    suite_manifest["artifacts"]["diagnostics.json"] = sha(dp)
                    mp.write_text(json.dumps(suite_manifest))
                    with self.assertRaises(ValueError):
                        audit_suite(root, build_settings())

    def test_external_identity_must_be_explicitly_trusted(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "run"
            external = {**provenance(), "git_commit": "a"*40, "git_dirty": False}
            # Synthetic external anchor tests the audit API, not execution attestation.
            run(root, identity=external)
            with self.assertRaises(ValueError):
                audit_suite(root, build_settings())
            result = audit_suite(root, build_settings(), expected_identity=external)
            self.assertTrue(result["identity_matches_trusted_expectation"])
            self.assertFalse(result["historical_execution_attested"])

    def test_existing_replay_rejects_before_primary_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            replay = root / "replay"
            replay.mkdir()
            sentinel = replay / "sentinel"
            sentinel.write_text("keep")
            with self.assertRaises(FileExistsError):
                run_pair(root / "primary", replay)
            self.assertFalse((root / "primary").exists())
            self.assertEqual(sentinel.read_text(), "keep")
            self.assertEqual(sorted(p.name for p in root.iterdir()), ["replay"])

    def test_resolved_paths_and_dangling_symlinks_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "alias").symlink_to(root, target_is_directory=True)
            primary = root / "primary"
            for replay in (root/"alias"/"primary", root/"alias"/"primary"/"child"):
                with self.subTest(replay=replay), self.assertRaises(ValueError):
                    run_pair(primary, replay)
                self.assertFalse(primary.exists())
            (root / "dangling").symlink_to(root / "absent")
            with self.assertRaises(FileExistsError):
                run(root / "dangling")
            self.assertTrue((root / "dangling").is_symlink())
            self.assertFalse((root / "absent").exists())

    def test_simulation_and_audit_exceptions_leave_no_published_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for failing in ("save_run", "audit_suite"):
                with self.subTest(failing=failing):
                    with patch.object(runner, failing, side_effect=ValueError("injected")):
                        with self.assertRaises(ValueError):
                            run_pair(root / "first", root / "second")
                    self.assertEqual(list(root.iterdir()), [])
            original = runner.recompute
            count = 0
            def fail_second(*args):
                nonlocal count
                count += 1
                if count == 2:
                    raise ValueError("injected replay calculation failure")
                return original(*args)
            with patch.object(runner, "recompute", side_effect=fail_second):
                with self.assertRaises(ValueError):
                    run_pair(root / "first", root / "second")
            self.assertEqual(list(root.iterdir()), [])

    def test_replay_mismatch_leaves_no_published_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with patch.object(runner, "identical_files", return_value=False):
                with self.assertRaises(ValueError):
                    run_pair(root / "first", root / "second")
            self.assertEqual(list(root.iterdir()), [])

    def test_publication_collision_preserves_other_writer_and_rolls_back_primary(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first, second = root/"first", root/"second"
            publish = runner._publish
            def race(stage, target):
                if target == second:
                    target.mkdir()
                    (target / "sentinel").write_text("other writer")
                publish(stage, target)
            with patch.object(runner, "_publish", side_effect=race):
                with self.assertRaises(FileExistsError):
                    run_pair(first, second)
            self.assertFalse(first.exists())
            self.assertEqual((second / "sentinel").read_text(), "other writer")
            self.assertEqual(sorted(p.name for p in root.iterdir()), ["second"])

    def test_no_replace_publication_preserves_even_an_empty_target(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            stage, target = root/"stage", root/"target"
            stage.mkdir()
            (stage/"evidence").write_text("new")
            target.mkdir()
            original_inode = target.stat().st_ino
            with self.assertRaises(FileExistsError):
                runner._publish(stage, target)
            self.assertEqual(target.stat().st_ino, original_inode)
            self.assertEqual(list(target.iterdir()), [])
            self.assertEqual((stage/"evidence").read_text(), "new")


if __name__ == "__main__":
    unittest.main()
