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

    def test_analytic_near_zero_nonzero_drag(self):
        # Regression for Codex review on PR #4: previously (-2048, 0).
        for drag in (1e-18, 1e-100, 5e-324):
            with self.subTest(drag=drag):
                c = replace(DEFAULT, drag_per_s=drag)
                x, v = analytic_state(c, c.duration_s)
                self.assertTrue(math.isfinite(x) and math.isfinite(v))
                self.assertAlmostEqual(x, 50.0, delta=1e-11)
                self.assertAlmostEqual(v, 10.0, delta=1e-11)

    def test_analytic_near_zero_drag_with_initial_state(self):
        c = replace(DEFAULT, drag_per_s=1e-18, force_n=2.0,
                    initial_x_m=7.0, initial_v_m_s=-3.0)
        x, v = analytic_state(c, c.duration_s)
        self.assertAlmostEqual(x, 77.0, delta=1e-11)
        self.assertAlmostEqual(v, 17.0, delta=1e-11)
        self.assertEqual(analytic_state(c, 0.0), (7.0, -3.0))

    def test_analytic_small_drag_series_boundary(self):
        # Exercise both sides of the series / expm1 switch at gamma*t=0.01.
        for drag in (0.000999, 0.001, 0.001001):
            with self.subTest(drag=drag):
                c = replace(DEFAULT, drag_per_s=drag,
                            initial_x_m=3.0, initial_v_m_s=-2.0)
                t = c.duration_s
                terminal_speed = c.force_n / (c.mass_kg * drag)
                decay = math.exp(-drag * t)
                x_expected = (c.initial_x_m + terminal_speed*t
                              + (c.initial_v_m_s-terminal_speed)
                              * (-math.expm1(-drag*t)) / drag)
                v_expected = terminal_speed + (c.initial_v_m_s-terminal_speed)*decay
                x, v = analytic_state(c, t)
                self.assertAlmostEqual(x, x_expected, delta=1e-9)
                self.assertAlmostEqual(v, v_expected, delta=1e-11)

    def test_near_zero_drag_manifest_is_finite(self):
        c = replace(DEFAULT, drag_per_s=1e-18)
        with tempfile.TemporaryDirectory() as tmp:
            result = save_run(c, Path(tmp) / "tiny-drag")
        self.assertAlmostEqual(result["analytic_x_m"], 50.0, delta=1e-11)
        self.assertAlmostEqual(result["analytic_v_m_s"], 10.0, delta=1e-11)
        self.assertTrue(math.isfinite(result["absolute_x_error_m"]))
        self.assertTrue(math.isfinite(result["absolute_v_error_m_s"]))

    def test_analytic_large_force_outputs_remain_finite(self):
        # Original review: a*t*t overflows, even though x is ~1.98e306.
        for force in (2e304, -2e304):
            with self.subTest(force=force):
                c = replace(DEFAULT, mass_kg=1.0, force_n=force,
                            drag_per_s=1.0, dt_s=1.0, duration_s=100.0)
                x, v = analytic_state(c, c.duration_s)
                self.assertTrue(math.isfinite(x) and math.isfinite(v))
                x_expected = force * (99.0 + math.exp(-100))
                v_expected = force * (-math.expm1(-100))
                self.assertAlmostEqual(x / x_expected, 1.0, delta=1e-13)
                self.assertAlmostEqual(v / v_expected, 1.0, delta=1e-13)
                self.assertTrue(math.isfinite(simulate(c)[-1].x_m))

        # Additional velocity failure: a*t overflows before phi1 is applied.
        c = replace(DEFAULT, mass_kg=1.0, force_n=2e307,
                    drag_per_s=1000.0, dt_s=0.001, duration_s=10.0)
        x, v = analytic_state(c, c.duration_s)
        self.assertTrue(math.isfinite(x) and math.isfinite(v))
        self.assertAlmostEqual(x / 1.9998e305, 1.0, delta=1e-13)
        self.assertAlmostEqual(v / 2e304, 1.0, delta=1e-13)

    def test_analytic_large_time_small_force_product(self):
        # t*t overflows, while a*t*t*phi2 is finite.
        c = replace(DEFAULT, mass_kg=1.0, force_n=1e-300,
                    drag_per_s=1e-200, dt_s=1e200, duration_s=1e200)
        x, v = analytic_state(c, c.duration_s)
        self.assertTrue(math.isfinite(x) and math.isfinite(v))
        self.assertAlmostEqual(x / (1e100 / math.e), 1.0, delta=1e-13)
        self.assertAlmostEqual(v / (1e-100 * (1 - 1 / math.e)), 1.0, delta=1e-13)

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
