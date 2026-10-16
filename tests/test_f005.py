"""F005 regression, analytic references, saved evidence, and boundary checks."""
from __future__ import annotations

import csv
from dataclasses import replace
import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from soma.f005 import Config, Motion, advance, initial, positive_motor_work, save_run, simulate
from experiments.F005.run_suite import base, suite, verify_saved_run


class TestF005(unittest.TestCase):
    def cfg(self, label="test", **kw):
        return Config.from_dict(base(label, **kw))

    def test_A_reversal_requires_positive_work(self):
        rows, events, ledger = simulate(self.cfg(motor=-2., velocity=1., dt=1.,
                                                  battery=500_000))
        self.assertEqual(len(rows), 2)
        self.assertEqual((rows[1]["x_m"], rows[1]["v_m_s"]), (-1., -1.))
        self.assertEqual(rows[1]["motor_work_j"], 0.)
        self.assertEqual(rows[1]["motor_positive_work_j"], .5)
        self.assertEqual(rows[1]["spent_uj"], 500_000)
        self.assertEqual(rows[1]["balance_uj"], 0)
        self.assertEqual(len(events), 1)
        self.assertEqual(ledger.residual_uj, 0)

    def test_B_insufficient_preserves_motion_inertia(self):
        rows, events, _ = simulate(self.cfg(motor=-2., velocity=1., dt=1.,
                                             battery=1))
        self.assertEqual((rows[1]["x_m"], rows[1]["v_m_s"]), (1., 1.))
        self.assertEqual(rows[1]["candidate_motor_positive_work_j"], .5)
        self.assertEqual(rows[1]["motor_positive_work_j"], 0.)
        self.assertEqual(rows[1]["decision_reason"], "insufficient_balance")
        self.assertEqual(rows[1]["balance_uj"], 1)
        self.assertEqual(events, [])

    def test_C_acceleration_matches_F004(self):
        from soma.f004 import Config as OldConfig, simulate as old_simulate
        cfg = self.cfg(motor=1., dt=1.)
        new, _, _ = simulate(cfg)
        old, _, _ = old_simulate(OldConfig.from_dict(
            {**cfg.to_dict(), "schema_version": "f004.v1"}))
        self.assertEqual((new[1]["x_m"], new[1]["v_m_s"], new[1]["spent_uj"]),
                         (old[1]["x_m"], old[1]["v_m_s"], old[1]["spent_uj"]))
        self.assertEqual(new[1]["motor_positive_work_j"], .5)

    def test_D_braking_without_regeneration(self):
        rows, events, _ = simulate(self.cfg(motor=-1., velocity=1., dt=1.))
        self.assertEqual(rows[1]["motor_work_j"], -.5)
        self.assertEqual(rows[1]["motor_positive_work_j"], 0.)
        self.assertEqual(rows[1]["balance_uj"], 1_000_000)
        self.assertEqual(events, [])

    def test_E_external_force_not_charged(self):
        rows, events, _ = simulate(self.cfg(motor=0., external=1., dt=1.))
        self.assertEqual(rows[1]["x_m"], 1.)
        self.assertEqual(rows[1]["v_m_s"], 1.)
        self.assertEqual(rows[1]["spent_uj"], 0)
        self.assertEqual(events, [])

    def test_F_split_matches_positive_work_not_position(self):
        coarse, _, _ = simulate(self.cfg(motor=-2., velocity=1., dt=1.,
                                          battery=500_000))
        split, _, _ = simulate(self.cfg(motor=-2., velocity=1., dt=.5,
                                         battery=500_000))
        self.assertEqual(split[1]["motor_positive_work_j"], 0.)
        self.assertEqual(split[2]["motor_positive_work_j"], .5)
        self.assertEqual(split[-1]["balance_uj"], coarse[-1]["balance_uj"])
        self.assertNotEqual(split[-1]["x_m"], coarse[-1]["x_m"])

    def test_asymmetric_reversal(self):
        self.assertEqual(positive_motor_work(-4., 1., -3., 1.), 4.5)
        rows, _, _ = simulate(self.cfg(motor=-4., velocity=1., dt=1.,
                                       battery=5_000_000, capacity=5_000_000))
        self.assertEqual(rows[1]["motor_work_j"], 4.)
        self.assertEqual(rows[1]["motor_positive_work_j"], 4.5)
        self.assertEqual(rows[1]["balance_uj"], 500_000)

    def test_zero_balance_blocks_free_motion(self):
        rows, _, _ = simulate(self.cfg(motor=1., external=-1., battery=0))
        self.assertEqual(rows[1]["motor_applied_n"], 0.)
        self.assertIsNone(rows[1]["candidate_motor_positive_work_j"])

    def test_submicro_rounds_to_1_uj(self):
        rows, events, _ = simulate(self.cfg(motor=.001, dt=.01, duration=.02,
                                             battery=1))
        self.assertEqual(rows[1]["spent_uj"], 1)
        self.assertEqual(rows[2]["motor_applied_n"], 0.)
        self.assertEqual(len(events), 1)

    def test_direct_config_and_replace_reject_invalid(self):
        for kw in ({"mass_kg": 0}, {"dt_s": .3},
                   {"initial_balance_uj": True}, {"seed": 1},
                   {"motor_force_n": float("nan")},
                   {"schema_version": "bad"}):
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                replace(self.cfg(), **kw)

    def test_positive_work_property_nonnegative_and_signed_bound(self):
        for u in (-3., -1., 0., 1., 4.):
            for va in (-2., -.5, 0., .5, 2.):
                for vb in (-2., -.5, 0., .5, 2.):
                    w = positive_motor_work(u, va, vb, .5)
                    signed = (u*.5)*((va+vb)/2)
                    self.assertGreaterEqual(w, 0.)
                    self.assertGreaterEqual(w+1e-12, max(0., signed))

    def test_subnormal_endpoint_power_must_not_make_positive_work_free(self):
        # Direct u*v underflows to zero, but u*h*v is representable and positive.
        u, v, h = 1e-200, 1e-200, 1e300
        self.assertEqual(u*v, 0.)
        self.assertAlmostEqual(positive_motor_work(u, v, v, h), 1e-100, delta=1e-110)
        cfg = self.cfg(motor=u, external=-u, velocity=v, dt=h, duration=h,
                       battery=1)
        rows, events, ledger = simulate(cfg)
        self.assertEqual(rows[1]["motor_positive_work_j"], 1e-100)
        self.assertEqual(rows[1]["spent_uj"], 1)
        self.assertEqual(len(events), 1)
        self.assertEqual(ledger.residual_uj, 0)

    def test_nonfinite_intermediates_rejected_atomically(self):
        cfg = self.cfg(motor=1e308, velocity=1e308, dt=1.)
        motion, ledger = initial(cfg)
        with self.assertRaises(ValueError):
            advance(cfg, motion, ledger, 1)
        self.assertEqual((motion, ledger), initial(cfg))

    def test_saved_evidence_verifier_and_bytes(self):
        cfg = self.cfg(motor=-2., velocity=1., dt=1., battery=500_000)
        identity = {"git_commit": "unit-test", "git_dirty": False,
                    "f005_sha256": "test", "f001_sha256": "test",
                    "f002_sha256": "test"}
        with tempfile.TemporaryDirectory() as root:
            a, b = Path(root)/"first", Path(root)/"second"
            save_run(cfg, a, identity=identity, suite_sha256="frozen")
            save_run(cfg, b, identity=identity, suite_sha256="frozen")
            self.assertTrue(verify_saved_run(cfg, a)["independent_all_steps"])
            for name in ("states.csv", "ledger/events.csv", "config.json",
                         "manifest.json", "motion_energy.svg"):
                self.assertEqual((a/name).read_bytes(), (b/name).read_bytes())

    def test_edited_hash_cannot_hide_modified_positive_work(self):
        cfg = self.cfg(motor=-2., velocity=1., dt=1., battery=500_000)
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)/"run"
            save_run(cfg, folder)
            file = folder/"states.csv"
            with file.open(newline="", encoding="utf-8") as inp:
                reader = csv.DictReader(inp)
                headers, data = reader.fieldnames, list(reader)
            data[1]["motor_positive_work_j"] = "0"
            with file.open("w", newline="", encoding="utf-8") as out:
                writer = csv.DictWriter(out, fieldnames=headers)
                writer.writeheader()
                writer.writerows(data)
            manifest_path = folder/"manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["artifacts"]["states.csv"] = hashlib.sha256(file.read_bytes()).hexdigest()
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(AssertionError, "motor_positive_work"):
                verify_saved_run(cfg, folder)

    def test_invalid_run_writes_no_artifacts(self):
        cfg = self.cfg(motor=1e308, velocity=1e308, dt=1.)
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)/"run"
            with self.assertRaises(ValueError):
                save_run(cfg, output)
            self.assertFalse(output.exists())

    def test_suite_A_to_F_and_invalid_rejections(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = suite(Path(tmp)/"F005")
            self.assertEqual(len(result["cases"]), 10)
            self.assertEqual(len(result["rejections"]), 17)
            self.assertEqual(result["cases"]["A-reversal"]["final_balance_uj"], 0)
            self.assertEqual(result["cases"]["B-low"]["final_balance_uj"], 1)
            self.assertTrue(result["checks"]["independent_csv_oracle"])
            self.assertTrue(result["checks"]["tamper_rejection"])


if __name__ == "__main__":
    unittest.main()
