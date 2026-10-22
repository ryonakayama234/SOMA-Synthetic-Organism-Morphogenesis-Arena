"""F018 isolated consent mechanics and pre-run Wolfram exact oracle examples."""
from __future__ import annotations
import unittest
from dataclasses import replace

from soma.f007 import Config as MotionConfig
from soma.f018 import (AttachmentIntent, resolve_attachment, scenario_grid,
                        simulate_world, summarize)


def select(layout: str, sign: int = 1, radius: float = 0.01,
           fee: int = 100000) -> dict:
    return next(s for s in scenario_grid() if
                (s["layout"],s["motor_sign"],s["terminal_radius_m"],
                 s["join_fee_uj"]) == (layout,sign,radius,fee))


def paired(scene: dict) -> dict:
    pri = {a:simulate_world(scene,a) for a in ("YY","YN","NY","NN")}
    outs = {float(u):simulate_world(scene,"NN",float(u))
            for u in (-2,0,2)}
    return summarize(pri,outs)


class TestF018(unittest.TestCase):
    def test_strict_intents(self):
        for bad in ("yes",1,0,None):
            with self.assertRaises(ValueError):
                AttachmentIntent("A",0,bad)
        with self.assertRaises(ValueError):
            AttachmentIntent("A",True,True)
        with self.assertRaises(ValueError):
            AttachmentIntent("C",0,True)

    def test_all_four_consent_conditions_and_fees(self):
        scene=select("DUAL_LINK")
        a={arm:simulate_world(scene,arm) for arm in ("YY","YN","NY","NN")}
        self.assertTrue(a["YY"]["attached"])
        for arm in ("YN","NY","NN"):
            self.assertFalse(a[arm]["attached"])
            self.assertEqual(a[arm]["net_uj"],a["NN"]["net_uj"])
            self.assertEqual(a[arm]["join_spent_uj"],{"A":0,"B":0})
            self.assertEqual(a[arm]["link_events"],[])
        self.assertEqual(a["YY"]["join_spent_uj"],{"A":100000,"B":100000})
        self.assertEqual(a["YY"]["ledger"]["residual_uj"],0)

    def test_misaligned_position_and_speed_rejected_without_snap(self):
        scene=select("NONE")
        base = {
            "schema_version":"f007.v1", "experiment_id":"invalid-link-fixture",
            "seed":None, "dt_s":0.25, "duration_s":1., "drag_per_s":0.,
            "cells":[
                {"id":"A","mass_kg":1., "initial_x_m":0.,
                 "initial_v_m_s":0., "external_force_n":0.,
                 "capacity_uj":20000000,"initial_balance_uj":10000000},
                {"id":"B","mass_kg":1., "initial_x_m":0.2,
                 "initial_v_m_s":0., "external_force_n":0.,
                 "capacity_uj":20000000,"initial_balance_uj":10000000}],
            "motor_force_n":2.,
            "link":{"initially_attached":False,"length_m":0.1,"detach_time_s":None},
        }
        intents=(AttachmentIntent("A",0,True),AttachmentIntent("B",0,True))
        cfg=MotionConfig.from_dict(base)
        with self.assertRaises(ValueError):
            resolve_attachment(*intents,cfg)
        base["cells"][1]["initial_x_m"]=.1
        base["cells"][1]["initial_v_m_s"]=.5
        cfg=MotionConfig.from_dict(base)
        with self.assertRaises(ValueError):
            resolve_attachment(*intents,cfg)
        self.assertFalse(resolve_attachment(
            AttachmentIntent("A",0,False),intents[1],cfg))

    def test_exact_two_patch_wolfram_precheck(self):
        data=paired(select("DUAL_LINK"))
        self.assertEqual(data["primary_net_uj"]["YY"],
                         {"A":1900000,"B":2900000})
        self.assertEqual(data["outside_best_uj"],{"A":0,"B":0})
        self.assertEqual(data["delta_outside_uj"],
                         {"A":1900000,"B":2900000})
        self.assertTrue(data["pareto_outside"])

    def test_b_only_forced_movement_is_not_voluntary(self):
        data=paired(select("B_LINK"))
        self.assertEqual(data["primary_net_uj"]["YY"],
                         {"A":-1100000,"B":2900000})
        self.assertEqual(data["delta_fixed_uj"],
                         {"A":900000,"B":2900000})
        self.assertEqual(data["delta_outside_uj"]["A"],-1100000)
        self.assertFalse(data["pareto_outside"])

    def test_direction_mirror_and_no_resources(self):
        plus=simulate_world(select("DUAL_LINK",1),"YY")
        minus=simulate_world(select("DUAL_LINK",-1),"YY")
        self.assertAlmostEqual(plus["states"][-1]["x_a_m"],.625)
        self.assertAlmostEqual(minus["states"][-1]["x_a_m"],-.625)
        self.assertEqual(plus["net_uj"],minus["net_uj"])
        none=simulate_world(select("NONE"),"YY")
        self.assertEqual(none["acquired_uj"],{"A":0,"B":0})
        self.assertEqual(none["net_uj"],{"A":-1100000,"B":-100000})


if __name__ == "__main__":
    unittest.main()
