"""F021 new capability: exact zero-input, energy and frozen model controls."""
import unittest

from soma.f021 import scene_for, grid, simulate, motor_gate, _motion


class F021FrozenTests(unittest.TestCase):
    def test_grid_full_and_unique(self):
        items = list(grid())
        self.assertEqual(len(items), 9216)
        self.assertEqual(len({x["world_id"] for x in items}), 4608)

    def test_both_80k_ambiguous(self):
        gate = motor_gate([0.,.1], [0.,0.], "YY",
                          {"A":2.,"B":2.}, {"A":80_000,"B":80_000})
        self.assertEqual(gate["reason"], "ambiguous_maximal")
        self.assertEqual(gate["selected_subset"], [])
        self.assertEqual(gate["maximal_feasible"], [["A"],["B"]])
        self.assertEqual(gate["candidates"][-1]["charge_uj"],
                         {"A":125_000,"B":125_000})
        self.assertEqual(gate["candidates"][1]["charge_uj"]["A"],62_500)
        self.assertEqual(gate["candidates"][2]["charge_uj"]["B"],62_500)

    def test_high_budget_both(self):
        gate = motor_gate([0.,.1],[0.,0.],"YY",
                          {"A":2.,"B":2.},{"A":4_000_000,"B":4_000_000})
        self.assertEqual(gate["selected_subset"], ["A","B"])
        self.assertEqual(gate["next_v_m_s"],[.5,.5])
        self.assertEqual(gate["charge_uj"],{"A":125_000,"B":125_000})

    def test_opposition_internal_force_and_free_ideal_work(self):
        gate = motor_gate([0.,.1],[0.,0.],"YY",
                          {"A":2.,"B":-2.},{"A":80_000,"B":80_000})
        self.assertEqual(gate["selected_subset"], ["A","B"])
        self.assertEqual(gate["next_v_m_s"],[0.,0.])
        self.assertEqual(gate["link_force_n"],{"A":-2.,"B":2.})
        self.assertEqual(gate["charge_uj"],{"A":0,"B":0})

    def test_nonlinked_both_move_independently(self):
        x,v,link = _motion([0.,.1],[0.,0.],"NN",2.,-2.)
        self.assertEqual(v,[.5,-.5])
        self.assertAlmostEqual(x[0], .125)\n        self.assertAlmostEqual(x[1], -.025)
        self.assertEqual(link,[0.,0.])

    def test_no_b_motor_no_charge_b(self):
        world = simulate(scene_for(0,1,0,"YY",250_000,0,2,.02))
        self.assertEqual(world["totals"]["B"]["motor_spent_uj"],0)
        self.assertTrue(all(s["decision"]["applied_n"]["B"]==0.
                            for s in world["steps"]))
        self.assertEqual(world["net_uj"]["B"],
                         world["totals"]["B"]["acquired_uj"])

    def test_previous_artifacts_immutable_through_new_version(self):
        from soma.f020 import SCHEMA as F020_SCHEMA
        from soma.f019 import SCHEMA as F019_SCHEMA
        self.assertEqual(F020_SCHEMA,"f020.v1")
        self.assertEqual(F019_SCHEMA,"f019.v1")

    def test_outside_protocol_rejected(self):
        with self.assertRaises(ValueError):
            scene_for(32,1,1,"YY",250_000,0,2,.02)
        with self.assertRaises(ValueError):
            motor_gate([0.,.1],[0.,0.],"YY",
                       {"A":2.,"B":2.},{"A":-1,"B":80_000})


if __name__ == "__main__":
    unittest.main()
