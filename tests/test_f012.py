"""F012 fixed-model and counterfactual regression. No emergent intelligence claim."""
import math
import unittest
from unittest.mock import patch

from soma.f012 import Config, simulate, measurements, StrokeLimitError


class F012Tests(unittest.TestCase):
    def test_first_step_wolfram_reference(self):
        rows = simulate(Config("C-directional", 1_000_000, .01))
        r = rows[1]
        self.assertAlmostEqual(r["x_cm_m"], .00002943, places=11)
        self.assertAlmostEqual(r["motor_candidate_positive_j"], .00005095, places=11)
        self.assertEqual(r["spent_uj"], 51)
        self.assertAlmostEqual(r["ground_a_n"], -.1962, places=9)
        self.assertAlmostEqual(r["ground_b_n"], .7848, places=9)

    def test_zero_budget_is_static_and_rejects_motor(self):
        for case in ("B-isotropic", "C-directional", "D-mirror", "E-no-drive"):
            for h in (.01, .005, .0025):
                rows = simulate(Config(case, 0, h))
                self.assertEqual(rows[-1]["x_cm_m"], 0.0)
                self.assertEqual(rows[-1]["balance_uj"], 0)
                self.assertTrue(all(row["spent_uj"] == 0 for row in rows[1:]))
                self.assertTrue(all(row["motor_applied_n"] == 0 for row in rows[1:]))

    def test_mirror_and_budget(self):
        for budget in (1_000_000, 3_000_000, 10_000_000):
            c = simulate(Config("C-directional", budget, .01))
            d = simulate(Config("D-mirror", budget, .01))
            self.assertEqual(len(c), len(d))
            for a, b in zip(c, d):
                self.assertAlmostEqual(a["x_cm_m"], -b["x_cm_m"], places=9)
                self.assertAlmostEqual(a["r_m"], b["r_m"], places=9)
                self.assertEqual(a["balance_uj"], b["balance_uj"])
                self.assertEqual(a["spent_uj"], b["spent_uj"])
                self.assertEqual(a["decision"], b["decision"])

    def test_isotropic_and_no_drive(self):
        for budget in (0, 1_000_000, 3_000_000, 10_000_000):
            b = simulate(Config("B-isotropic", budget, .01))
            e = simulate(Config("E-no-drive", budget, .01))
            self.assertAlmostEqual(b[-1]["x_cm_m"], 0, places=10)
            self.assertTrue(all(x["v_a_m_s"] == 0 and x["v_b_m_s"] == 0 for x in e))
            self.assertEqual(e[-1]["balance_uj"], budget)

    def test_positive_work_and_exact_ledger(self):
        for budget in (1_000_000, 3_000_000, 10_000_000):
            rows = simulate(Config("C-directional", budget, .005))
            m = measurements(rows)
            self.assertEqual(m["spent_uj"] + m["balance_uj"], budget)
            self.assertGreaterEqual(m["quantization_excess_j"], -1e-10)
            self.assertLess(m["quantization_excess_j"], len(rows) / 1_000_000 + 1e-10)
            self.assertTrue(all(x["ground_work_j"] <= 1e-11 for x in rows[1:]))

    def test_motor_refusal_does_not_freeze_passive_mechanics(self):
        rows = simulate(Config("C-directional", 1_000_000, .005))
        moving_with_motor_off = [
            (prev, now) for prev, now in zip(rows, rows[1:])
            if now["motor_command_n"] != 0 and now["motor_applied_n"] == 0
            and abs(now["x_a_m"] - prev["x_a_m"]) +
                abs(now["x_b_m"] - prev["x_b_m"]) > 1e-9
        ]
        self.assertTrue(moving_with_motor_off, "rejected drive must retain passive motion")

    def test_stroke_guard_reports_valid_prefix_without_clipping(self):
        cfg = Config("C-directional", 0, .01)
        with patch("soma.f012._step", return_value=(-.9, .9, 0., 0., 0., 0.)):
            with self.assertRaises(StrokeLimitError) as caught:
                simulate(cfg)
        self.assertEqual(caught.exception.step, 1)
        self.assertAlmostEqual(caught.exception.attempted_r, 1.8)
        self.assertEqual(len(caught.exception.valid_rows), 1)
        self.assertEqual(caught.exception.valid_rows[0]["step"], 0)

    def test_invalid_contract(self):
        for args in (("C-directional", 3.0, .01),
                     ("C-directional", True, .01),
                     ("C-directional", 123, .01),
                     ("A-no-contact", 0, .01),
                     ("B-isotropic", 0, .001),
                     ("B-isotropic", 0, float("nan"))):
            with self.assertRaises(ValueError):
                Config(*args)
        with self.assertRaises(TypeError):
            simulate(object())


if __name__ == "__main__":
    unittest.main()
