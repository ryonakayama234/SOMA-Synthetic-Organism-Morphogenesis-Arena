"""F004 unit, numeric, security, provenance and saved-evidence invariants."""
from __future__ import annotations

import csv
from dataclasses import replace
from decimal import localcontext
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from soma.f001 import step as f001_step
from soma.f002 import Event, apply_event
from soma.f004 import Config, Motion, advance, initial, save_run, simulate
from experiments.F004.run_suite import base, suite, verify_saved_run


class TestF004(unittest.TestCase):
    def cfg(self, **changes):
        return Config.from_dict(base("test", **changes))

    def test_A_external_work_is_not_battery_spend(self):
        cfg = self.cfg(motor=0., external=1.)
        rows, events, ledger = simulate(cfg)
        self.assertEqual(len(events), 0)
        self.assertEqual(ledger.residual_uj, 0)
        self.assertEqual(rows[-1]["balance_uj"], 1_000_000)
        self.assertAlmostEqual(rows[-1]["x_m"], .55, delta=1e-12)
        self.assertTrue(all(row["motor_applied_n"] == 0 for row in rows))

    def test_B_motor_matches_F001_oracle_with_sufficient_battery(self):
        cfg = self.cfg()
        rows, events, ledger = simulate(cfg)
        x, v = 0., 0.
        for k in range(1, cfg.steps+1):
            x, v = f001_step(x, v, mass_kg=1., drag_per_s=0.,
                            force_n=1., dt_s=.1)
            self.assertEqual(rows[k]["x_m"], x)
            self.assertEqual(rows[k]["v_m_s"], v)
        self.assertEqual(len(events), 10)
        self.assertEqual(rows[-1]["balance_uj"], 499_995)
        self.assertEqual(ledger.spent_uj, 500_005)
        self.assertEqual(ledger.residual_uj, 0)

    def test_C_empty_battery_freezes_internal_force(self):
        rows, events, _ = simulate(self.cfg(battery=0))
        self.assertTrue(all(r["motor_applied_n"] == 0 for r in rows))
        self.assertTrue(all(r["v_m_s"] == 0 for r in rows))
        self.assertEqual(events, [])

    def test_D_insufficient_battery_preserves_inertia(self):
        rows, events, _ = simulate(self.cfg(battery=300_000))
        self.assertEqual(len(events), 7)
        self.assertEqual(rows[7]["motor_applied_n"], 1.)
        self.assertEqual(rows[8]["motor_applied_n"], 0.)
        self.assertEqual(rows[8]["decision_reason"], "insufficient_balance")
        self.assertAlmostEqual(rows[-1]["x_m"], .49, delta=1e-12)
        self.assertAlmostEqual(rows[-1]["v_m_s"], .7, delta=1e-12)
        self.assertEqual(rows[-1]["balance_uj"], 54_996)

    def test_E_brake_no_regen(self):
        rows, events, _ = simulate(self.cfg(motor=-1., velocity=1.))
        self.assertEqual(len(events), 0)
        self.assertAlmostEqual(rows[-1]["x_m"], .45, delta=1e-12)
        self.assertAlmostEqual(rows[-1]["v_m_s"], 0., delta=1e-12)
        self.assertEqual(rows[-1]["balance_uj"], 1_000_000)

    def test_zero_battery_cancelled_work_loophole_closed(self):
        cfg = self.cfg(battery=0, motor=1., external=-1.)
        rows, events, _ = simulate(cfg)
        self.assertEqual(rows[1]["motor_applied_n"], 0.)
        self.assertEqual(rows[1]["decision_reason"], "zero_balance")
        self.assertIsNone(rows[1]["candidate_motor_work_j"])
        self.assertAlmostEqual(rows[1]["x_m"], -.01, delta=1e-15)
        self.assertEqual(events, [])

    def test_positive_battery_zero_work_is_free_idealization(self):
        rows, events, _ = simulate(self.cfg(battery=1, motor=1., external=-1.))
        self.assertEqual(rows[1]["motor_applied_n"], 1.)
        self.assertEqual(rows[1]["decision_reason"], "accepted_nonpositive_work")
        self.assertEqual(rows[1]["balance_uj"], 1)
        self.assertEqual(events, [])

    def test_submicro_work_rounded_up(self):
        rows, events, _ = simulate(self.cfg(motor=.001, battery=1,
                                           dt=.01, duration=.02))
        self.assertEqual(rows[1]["spent_uj"], 1)
        self.assertEqual(rows[2]["decision_reason"], "zero_balance")
        self.assertEqual(len(events), 1)

    def test_no_hidden_cell_observation_state_and_atomic_on_failure(self):
        cfg = self.cfg()
        motion, ledger = initial(cfg)
        old = (motion, ledger)
        with patch("soma.f004.apply_event", side_effect=ValueError("ledger error")):
            with self.assertRaisesRegex(ValueError, "ledger error"):
                advance(cfg, motion, ledger, 1)
        self.assertEqual((motion, ledger), old)
        self.assertEqual(ledger.cell("A").balance_uj, 1_000_000)
        self.assertFalse(hasattr(motion, "battery_uj"))

    def test_invalid_runtime_derivatives_do_not_change_state(self):
        cfg = self.cfg(mass=1e-300, motor=1e300)
        motion, ledger = initial(cfg)
        with self.assertRaises(ValueError):
            advance(cfg, motion, ledger, 1)
        self.assertEqual(motion, Motion(0., 0.))
        self.assertEqual(ledger.residual_uj, 0)

    def test_config_validation_and_xml(self):
        for raw in (
            base("b", mass=0), base("b", dt=.03), base("b", battery=-1),
            base("b", battery=True), base("b", capacity=0),
            base("b", motor=float("nan")), base("b", external=float("inf")),
            dict(base("b"), unexpected=1), dict(base("b"), experiment_id="a\u0000b"),
            dict(base("b"), experiment_id="a\ud800b"),
            dict(base("b"), seed=0),
        ):
            with self.subTest(raw=str(raw)[:100]), self.assertRaises(ValueError):
                Config.from_dict(raw)

    def test_decimal_grid_ignores_decimal_precision(self):
        for precision in (3, 28, 60):
            with localcontext() as ctx:
                ctx.prec = precision
                self.assertEqual(self.cfg().steps, 10)
                with self.assertRaises(ValueError):
                    self.cfg(dt=.03)

    def test_integer_time_grid_cannot_change_during_float_normalization(self):
        # Raw ratio is exactly 6; converting the duration to float changes its
        # decimal spelling and previously made Config.steps silently return 5.
        raw = base("integer-grid", motor=0, dt=2**53, duration=6 * 2**53)
        with self.assertRaisesRegex(ValueError, "normalization"):
            Config.from_dict(raw)
        # Normalization must not turn an invalid raw grid into a valid one.
        with self.assertRaises(ValueError):
            Config.from_dict(base("offgrid", dt=2**53, duration=2 * 2**53 + 1))
        cfg = Config.from_dict(base("integer-grid", motor=0, dt=2, duration=6))
        self.assertEqual(cfg.steps, 3)
        self.assertEqual(Config.from_dict(cfg.to_dict()), cfg)
        self.assertEqual(simulate(cfg)[0][-1]["time_s"], cfg.duration_s)

    def test_direct_config_and_replace_enforce_input_contract(self):
        for changes in (
            {"dt_s": .3}, {"mass_kg": 0}, {"motor_force_n": float("nan")},
            {"initial_balance_uj": True}, {"seed": 1},
            {"schema_version": "unknown"}, {"experiment_id": "bad\u0000id"},
        ):
            with self.subTest(changes=changes):
                raw = {**base("direct"), **changes}
                with self.assertRaises(ValueError):
                    Config(**raw)
                with self.assertRaises(ValueError):
                    replace(self.cfg(), **changes)
        cfg = Config(**base("direct", motor=0, dt=1, duration=3))
        self.assertEqual(cfg.steps, 3)
        self.assertIs(type(cfg.dt_s), float)

    def test_large_finite_motion_has_finite_bounded_svg_coordinates(self):
        cfg = Config.from_dict(dict(base("large-plot", motor=0, velocity=2,
                                        dt=4e307, duration=1.2e308),
                                    initial_x_m=-1e308))
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)/"run"
            save_run(cfg, folder)
            self.assertTrue(verify_saved_run(cfg, folder)["independent_all_steps"])
            root = ET.parse(folder/"motion_energy.svg").getroot()
            lines = root.findall("{http://www.w3.org/2000/svg}polyline")
            self.assertEqual(len(lines), 3)
            for line in lines:
                for point in line.attrib["points"].split():
                    x, y = map(float, point.split(","))
                    self.assertTrue(math.isfinite(x) and math.isfinite(y))
                    self.assertTrue(90 <= x <= 770 and 78 <= y <= 442)

    def test_derived_mechanical_identity(self):
        rows, _, ledger = simulate(self.cfg(drag=.2, external=.25, dt=.05))
        self.assertEqual(ledger.residual_uj, 0)
        for row in rows:
            self.assertLessEqual(abs(row["mechanical_residual_j"]), 1e-10)

    def test_outputs_are_byte_identical_with_frozen_provenance(self):
        cfg = self.cfg()
        frozen = {"git_commit": "test", "git_dirty": False,
                  "f004_sha256": "test", "f001_sha256": "test", "f002_sha256": "test"}
        with tempfile.TemporaryDirectory() as tmp:
            first, second = Path(tmp)/"a", Path(tmp)/"b"
            save_run(cfg, first, identity=frozen, suite_sha256="suite")
            save_run(cfg, second, identity=frozen, suite_sha256="suite")
            for path in ("config.json", "states.csv", "ledger/events.csv",
                         "motion_energy.svg", "manifest.json"):
                self.assertEqual((first/path).read_bytes(), (second/path).read_bytes())
            self.assertTrue(verify_saved_run(cfg, first)["independent_all_steps"])

    def test_invalid_run_does_not_write_partial_evidence(self):
        cfg = self.cfg(mass=1e-300, motor=1e300)
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)/"not-created"
            with self.assertRaises(ValueError):
                save_run(cfg, dest)
            self.assertFalse(dest.exists())

    def test_saved_csv_tampering_is_detected(self):
        cfg = self.cfg()
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)/"run"
            save_run(cfg, dest)
            path = dest/"states.csv"
            raw = path.read_text()
            path.write_text(raw.replace("B-full", "tampered", 1) + "tamper\n")
            with self.assertRaises((AssertionError, ValueError)):
                verify_saved_run(cfg, dest)

    def test_manifest_cannot_disable_artifact_integrity_checks(self):
        cfg = self.cfg()
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)/"run"
            save_run(cfg, dest)
            manifest_path = dest/"manifest.json"
            manifest = json.loads(manifest_path.read_text())
            valid = manifest["artifacts"]
            inventories = [{}, None, {**valid, "extra.svg": "unused"}]
            inventories += [{k: v for k, v in valid.items() if k != removed}
                            for removed in valid]
            for inventory in inventories:
                with self.subTest(inventory=inventory):
                    manifest["artifacts"] = inventory
                    manifest_path.write_text(json.dumps(manifest))
                    with self.assertRaises(AssertionError):
                        verify_saved_run(cfg, dest)

    def test_independent_oracle_checks_initial_energy_even_with_updated_hash(self):
        cfg = self.cfg()
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)/"run"
            save_run(cfg, dest)
            path = dest/"states.csv"
            with path.open(newline="") as fp:
                reader = csv.DictReader(fp)
                fields, original = reader.fieldnames, list(reader)
            manifest_path = dest/"manifest.json"
            manifest = json.loads(manifest_path.read_text())
            for field in ("motor_work_j", "external_work_j", "drag_work_j",
                          "kinetic_delta_j", "mechanical_residual_j"):
                with self.subTest(field=field):
                    rows = [dict(row) for row in original]
                    rows[0][field] = "123"
                    with path.open("w", newline="") as fp:
                        writer = csv.DictWriter(fp, fieldnames=fields)
                        writer.writeheader()
                        writer.writerows(rows)
                    manifest["artifacts"]["states.csv"] = hashlib.sha256(path.read_bytes()).hexdigest()
                    manifest_path.write_text(json.dumps(manifest))
                    with self.assertRaisesRegex(AssertionError, "initial row"):
                        verify_saved_run(cfg, dest)

    def test_suite_runs_preregistered_controls_and_refuses_invalid_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = suite(Path(tmp)/"suite")
            self.assertEqual(len(result["cases"]), 10)
            self.assertEqual(result["cases"]["B-full"]["final_balance_uj"], 499_995)
            self.assertEqual(result["cases"]["D-low"]["final_balance_uj"], 54_996)
            self.assertEqual(len(result["rejections"]), 17)
            self.assertTrue(all(record["pass"] for record in result["rejections"]))
            self.assertTrue(result["checks"]["tamper_rejection"])

    def test_optimized_python_does_not_skip_oracle(self):
        code = """
from pathlib import Path
import tempfile
from experiments.F004.run_suite import suite,verify_saved_run,base
from soma.f004 import Config
with tempfile.TemporaryDirectory() as temp:
  out=Path(temp)/'suite'
  suite(out)
  target=out/'B-full'/'states.csv'
  target.write_text(target.read_text()+'tamper\\n')
  try: verify_saved_run(Config.from_dict(base('B-full')),out/'B-full')
  except (AssertionError, ValueError): pass
  else: raise RuntimeError('optimized mode skipped tamper check')
"""
        process = subprocess.run([sys.executable, "-O", "-c", code],
                                 cwd=Path(__file__).resolve().parents[1],
                                 capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stderr + process.stdout)


if __name__ == "__main__":
    unittest.main()
