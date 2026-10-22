"""F019 first-entry, causal ownership and strict frozen design boundary tests."""
from __future__ import annotations
import unittest

from soma.f019 import (field_for, scenario_for, scenario_grid,
                       first_entry, harvests_from_states, simulate_world,
                       summarize, validate_scene)

class F019Test(unittest.TestCase):
    def test_frozen_field_independent_of_sign_and_fee(self):
        x = scenario_for(7, 1, 0, 5, .02)
        y = scenario_for(7, -1, 100000, 5, .02)
        self.assertEqual(x["field"], y["field"])
        self.assertEqual(x["field"], field_for(7, 5, .02))
        self.assertEqual(len(scenario_grid()), 512)
        self.assertTrue(all(abs(p["center_m"]) > .02 and
                            abs(p["center_m"]-.1) > .02
                            for p in x["field"]["patches"]))

    def test_forged_field_and_bool_seed_rejected(self):
        with self.assertRaises(ValueError):
            field_for(True, 2, .02)
        s = scenario_for(0, 1, 0, 2, .06)
        s["field"]["patches"][0]["center_m"] = 0.625
        with self.assertRaises(ValueError):
            validate_scene(s)

    def test_path_segment_not_just_terminal(self):
        self.assertAlmostEqual(first_entry(0., .3, .2, .01), 19/30)
        self.assertAlmostEqual(first_entry(.3, 0., .2, .01), .3)
        self.assertEqual(first_entry(.2, .2, .2, .01), 0.)
        self.assertIsNone(first_entry(0., 0., .2, .01))
        self.assertEqual(first_entry(0., .2, .2, 0.), 1.)
        with self.assertRaises(ValueError):
            first_entry(float("nan"), 1., .2, .01)

    def test_tie_break_and_unique_depletion(self):
        field = {"field_id": "synthetic", "patches": [
            {"patch_id": "P0", "center_m": .2, "radius_m": .01,
             "initial_available_uj": 1000000}]}
        states = [{"x_a_m": .0, "x_b_m": .0},
                  {"x_a_m": .3, "x_b_m": .3},
                  {"x_a_m": .0, "x_b_m": .0}]
        hits = harvests_from_states(field, states)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["winner_cell_id"], "A")
        self.assertEqual(hits[0]["available_after_uj"], 0)

    def test_b_first_when_linked_and_a_first_when_free(self):
        s = scenario_for(0, 1, 100000, 2, .02)
        # Unit-level geometry calibration independent from the frozen main generator.
        field = {"field_id": "calibration", "patches": [
            {"patch_id": "P0", "center_m": .2, "radius_m": 0.,
             "initial_available_uj": 1000000}]}
        a = simulate_world(s, "YY")
        b = simulate_world(s, "NN")
        self.assertTrue(a["attached"])
        self.assertFalse(b["attached"])
        self.assertEqual({h["patch_id"] for h in a["harvests"]},
                         {h["patch_id"] for h in a["harvests"]})
        self.assertEqual(harvests_from_states(field, a["states"])[0]["winner_cell_id"], "B")
        self.assertEqual(harvests_from_states(field, b["states"])[0]["winner_cell_id"], "A")

    def test_refused_attachment_and_ledger(self):
        s = scenario_for(0, -1, 100000, 2, .06)
        y = simulate_world(s, "YY")
        r = simulate_world(s, "YN")
        self.assertTrue(y["attached"])
        self.assertFalse(r["attached"])
        self.assertEqual(r["join_spent_uj"], {"A": 0, "B": 0})
        for x in (y, r):
            self.assertEqual(x["ledger"]["residual_uj"], 0)
            self.assertEqual(set(x["net_uj"]), {"A", "B"})

    def test_outside_never_becomes_policy_input(self):
        s = scenario_for(1, 1, 0, 2, .02)
        main = {a: simulate_world(s, a) for a in ("YY", "YN", "NY", "NN")}
        outside = {u: simulate_world(s, "NN", u) for u in (-2., 0., 2.)}
        score = summarize(s, main, outside)
        self.assertEqual(len(score["patch_comparison"]), 2)
        self.assertIn("delta_outside_uj", score)
        self.assertNotIn("delta_outside_uj", main["YY"])

if __name__ == "__main__":
    unittest.main()
