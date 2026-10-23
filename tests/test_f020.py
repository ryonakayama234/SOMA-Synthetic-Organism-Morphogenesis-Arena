"""F020 causal model and preregistered exact-rational technical control tests."""
from __future__ import annotations

from copy import deepcopy
import unittest

from soma.f007 import simulate as f007_simulate
from soma.f020 import (
    BALANCES, ARMS, MODES, calibration_scene, config_for, scene_for,
    scenario_grid, simulate_world, validate_scene,
)


class F020Test(unittest.TestCase):
    def test_frozen_grid_and_tampering(self):
        scenes = scenario_grid()
        self.assertEqual(len(scenes), 1536)
        self.assertEqual(len({s["scenario_id"] for s in scenes}), 1536)
        self.assertEqual(BALANCES, (75_000, 250_000, 4_000_000))
        for s in (scenes[0], scenes[1023], scenes[-1]):
            validate_scene(s)
        forged = deepcopy(scenes[0])
        forged["field"]["patches"][0]["center_m"] = .625
        with self.assertRaises(ValueError):
            validate_scene(forged)
        with self.assertRaises(ValueError):
            scene_for(True, 1, 2, .02, 75_000, 0)
        with self.assertRaises(ValueError):
            calibration_scene("tuned")

    def test_wolfram_exact_trajectory_fixture(self):
        scene = calibration_scene()
        expected = {
            ("YY", "feedback"): ([0., 1/16, 3/16, 3/8, 5/8],
                                  [0., 2., 2., 2., 2.]),
            ("YY", "deferred_credit"): ([0., 1/16, 1/8, 3/16, 1/4],
                                         [0., 2., 0., 0., 0.]),
            ("NN", "feedback"): ([0.]*5, [0.]*5),
            ("NN", "deferred_credit"): ([0.]*5, [0.]*5),
        }
        for key, (positions, motors) in expected.items():
            with self.subTest(key=key):
                world = simulate_world(scene, *key)
                self.assertEqual([s["x_a_m"] for s in world["states"]], positions)
                self.assertEqual([s["motor_applied_n"] for s in world["states"]], motors)
                self.assertEqual(world["ledger"]["residual_uj"], 0)
                if key[0] == "YY":
                    self.assertEqual(len(world["harvests"]), 1)
                    self.assertEqual(world["harvests"][0]["winner_cell_id"], "A")
                    self.assertEqual(world["harvests"][0]["step_index"], 1)
        feedback = simulate_world(scene, "YY", "feedback")
        delayed = simulate_world(scene, "YY", "deferred_credit")
        self.assertEqual(feedback["states"][1]["balance_a_uj"], 1_012_500)
        self.assertEqual(delayed["states"][1]["balance_a_uj"], 12_500)
        self.assertEqual(delayed["states"][1]["pending_a_uj"], 1_000_000)
        self.assertEqual(delayed["states"][2]["v_a_m_s"], .25)
        self.assertEqual(delayed["states"][4]["pending_a_uj"], 1_000_000)
        self.assertEqual(delayed["ledger"]["balance_a_uj"], 1_012_500)

    def test_b_claim_never_electrifies_a(self):
        scene = calibration_scene("b_only")
        for mode in MODES:
            world = simulate_world(scene, "YY", mode)
            self.assertEqual(world["harvests"][0]["winner_cell_id"], "B")
            self.assertEqual(world["states"][2]["motor_applied_n"], 0.)
            self.assertEqual(world["states"][2]["balance_a_uj"], 12_500)
            self.assertEqual(world["acquired_uj"]["A"], 0)
            self.assertEqual(world["acquired_uj"]["B"], 1_000_000)

    def test_no_field_and_no_motor(self):
        scene = calibration_scene("empty")
        for arm in ARMS:
            for mode in MODES:
                world = simulate_world(scene, arm, mode)
                self.assertEqual(world["harvests"], [])
                self.assertEqual(world["acquired_uj"], {"A": 0, "B": 0})
                self.assertEqual(world["ledger"]["residual_uj"], 0)
        off = simulate_world(scene, "YY", "feedback", 0.)
        self.assertTrue(all(x["motor_applied_n"] == 0. for x in off["states"]))
        self.assertTrue(all(x["x_a_m"] == 0. for x in off["states"]))

    def test_high_balance_reproduces_f007_no_field_physics(self):
        # At 4J any patch receipt is irrelevant to A's 4-step motor gate.
        for arm in ARMS:
            s = scene_for(0, 1, 2, .02, 4_000_000, 25_000)
            for mode in MODES:
                world = simulate_world(s, arm, mode)
                cfg = config_for(s, arm == "YY", 2.)
                reference, _, _, _ = f007_simulate(cfg)
                for got, ref in zip(world["states"], reference):
                    for key in ("x_a_m", "x_b_m", "v_a_m_s", "v_b_m_s",
                                "motor_applied_n"):
                        self.assertEqual(got[key], ref[key])
                self.assertEqual([x["motor_applied_n"] for x in
                                  world["states"][1:]], [2.]*4)

    def test_reflection_and_fee_and_deferred_settlement(self):
        for sign in (-1, 1):
            s = scene_for(7, sign, 5, .06, 250_000, 25_000)
            y = simulate_world(s, "YY", "deferred_credit")
            n = simulate_world(s, "NN", "feedback")
            self.assertEqual(y["spent_fee_uj"], {"A": 25_000, "B": 25_000})
            self.assertEqual(n["spent_fee_uj"], {"A": 0, "B": 0})
            self.assertEqual(y["ledger"]["residual_uj"], 0)
            self.assertEqual(y["ledger"]["event_count"], len(y["events"]))
            self.assertEqual(sum(x["acquired_uj"] for x in y["harvests"]),
                             y["ledger"]["acquired_uj"])
            self.assertEqual(y["states"][0]["balance_a_uj"], 225_000)
            self.assertEqual(y["states"][0]["balance_b_uj"], 225_000)


if __name__ == "__main__":
    unittest.main()
