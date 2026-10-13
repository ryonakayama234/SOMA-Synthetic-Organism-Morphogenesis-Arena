"""F001 invariants and convergence tests (stdlib-only)."""

from dataclasses import replace
import math
from pathlib import Path
import tempfile
import unittest

from soma.f001 import RunConfig, analytic_state, save_run, simulate


DEFAULT = RunConfig(
    schema_version="f001.v1", experiment_id="F001-test", seed=1,
    model="1d_linear_drag", mass_kg=1.0, drag_per_s=0.2,
    force_n=1.0, dt_s=0.01, duration_s=10.0,
)


class TestF001(unittest.TestCase):
    def test_a_rest_without_force(self):
        for s in simulate(replace(DEFAULT, force_n=0.0)):
            self.assertEqual(s.x_m, 0.0)
            self.assertEqual(s.v_m_s, 0.0)

    def test_b_positive_force(self):
        states = simulate(DEFAULT)
        self.assertGreater(states[-1].x_m, 0)
        self.assertGreater(states[-1].v_m_s, 0)
        self.assertTrue(all(b.x_m >= a.x_m for a, b in zip(states, states[1:])))

    def test_c_reflection_symmetry(self):
        pos = simulate(DEFAULT)
        neg = simulate(replace(DEFAULT, force_n=-1.0))
        for a, b in zip(pos, neg):
            self.assertAlmostEqual(a.x_m, -b.x_m, delta=1e-9)
            self.assertAlmostEqual(a.v_m_s, -b.v_m_s, delta=1e-9)

    def test_d_drag_monotonic(self):
        states = simulate(replace(DEFAULT, force_n=0.0, initial_v_m_s=1.0))
        self.assertTrue(all(0.0 <= b.v_m_s <= a.v_m_s for a, b in zip(states, states[1:])))

    def test_e_halved_step_converges_against_exact(self):
        dt_values = [0.01, 0.005, 0.0025]
        runs = [simulate(replace(DEFAULT, dt_s=h))[-1] for h in dt_values]
        x_exact, v_exact = analytic_state(DEFAULT, DEFAULT.duration_s)
        errors = [abs(r.x_m-x_exact) for r in runs]
        v_errors = [abs(r.v_m_s-v_exact) for r in runs]
        self.assertTrue(errors[2] < errors[1] < errors[0])
        self.assertTrue(v_errors[2] < v_errors[1] < v_errors[0])
        self.assertTrue(1.8 < errors[0]/errors[1] < 2.2)
        self.assertTrue(1.8 < errors[1]/errors[2] < 2.2)
        self.assertGreater(abs(runs[0].x_m-runs[1].x_m), 0.0)

    def test_analytic_no_drag(self):
        c = replace(DEFAULT, drag_per_s=0, force_n=2, duration_s=2, dt_s=0.01)
        self.assertEqual(analytic_state(c, 2), (4.0, 4.0))

    def test_initial_position_and_velocity_are_respected(self):
        c = replace(DEFAULT, force_n=0, drag_per_s=0, initial_x_m=-4.0, initial_v_m_s=2.0)
        states = simulate(c)
        self.assertEqual(states[0].x_m, -4.0)
        self.assertAlmostEqual(states[-1].x_m, 16.0)

    def test_parameters_rejected(self):
        for change in (
            {"mass_kg":0}, {"dt_s":0}, {"duration_s":-1},
            {"drag_per_s":-1}, {"force_n":float("nan")},
            {"dt_s":0.03}, {"drag_per_s":200}, {"schema_version":"wrong"},
            {"model":"wrong"},
        ):
            with self.subTest(change=change), self.assertRaises(ValueError):
                replace(DEFAULT, **change)

    def test_output_files_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "run"
            result = save_run(DEFAULT, folder)
            self.assertEqual(result["sample_count"], 1001)
            for name in ("config.json", "states.csv", "motion.svg", "manifest.json"):
                self.assertTrue((folder/name).is_file())
            self.assertEqual((folder/"states.csv").read_text().splitlines()[0], "time_s,x_m,v_m_s,force_n")
            with self.assertRaises(FileExistsError):
                save_run(DEFAULT, folder)


if __name__ == "__main__":
    unittest.main()
