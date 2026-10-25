"""F023 frozen hypotheses: controlled 2D contact, private motor fee, audit."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from soma.f023 import FREEZE_COMMIT, grid, simulate, validate, _work_and_charge
from experiments.F023.run_suite import produce, invalid_probes
from experiments.F023.verify import verify, reference_roster
from experiments.F023.attack_test import attack

SOURCE = "a"*40


class F023BoundedActiveEncounter(unittest.TestCase):
    def test_exact_scene_roster_and_frozen_anchor(self):
        scenes = grid()
        self.assertEqual(FREEZE_COMMIT,"76dcc1db7ae12737705da06c155933d0a8251853")
        self.assertEqual([s["world_id"] for s in scenes],[f"Q{i:02d}" for i in range(1,16)])
        self.assertEqual(scenes, reference_roster())
        self.assertTrue(all(len(simulate(s)[0])==9 for s in scenes))

    def test_analytic_controllability_and_null_controls(self):
        results={s["world_id"]:simulate(s) for s in grid()}
        self.assertEqual(sum(len(x[2]) for x in results.values()),9)
        self.assertFalse(results["Q01"][2])
        self.assertTrue(results["Q02"][2])
        self.assertFalse(results["Q03"][2])
        self.assertFalse(results["Q04"][2])
        self.assertEqual(results["Q04"][1][0]["decision"],"insufficient_private_budget")
        self.assertEqual(results["Q04"][1][0]["charge_uj"],0)
        self.assertEqual(results["Q02"][1][0]["charge_uj"],200)
        self.assertEqual(results["Q03"][1][0]["charge_uj"],200)
        self.assertEqual(results["Q02"][1][1]["charge_uj"],0)
        self.assertEqual(results["Q05"][1][1]["charge_uj"],0)
        self.assertEqual(results["Q06"][1][1]["charge_uj"],200)
        self.assertEqual(results["Q10"][1][1]["charge_uj"],200)
        self.assertAlmostEqual(results["Q02"][2][0]["time_s"],.9342458972916169,delta=1e-9)
        self.assertAlmostEqual(results["Q15"][2][0]["time_s"],.095,delta=1e-9)
        self.assertTrue(all(not results[f"Q{i:02d}"][2] for i in (11,12,13)))
        self.assertEqual(results["Q13"][1][0]["decision"],"applied")
        self.assertAlmostEqual(results["Q13"][1][0]["applied_work_j"],-.18)
        self.assertEqual(results["Q13"][1][0]["charge_uj"],0)
        self.assertGreater(results["Q07"][4]["collision_loss_j"],0.)

    def test_exact_private_positive_work_integer_boundary(self):
        self.assertEqual(_work_and_charge(1,0,0,.02)[1],200)
        self.assertEqual(_work_and_charge(1,0,0,-.02)[1],200)
        self.assertEqual(_work_and_charge(1,0,-.2,0)[1],0)
        self.assertEqual(_work_and_charge(0,0,0,.02)[1],200)
        self.assertEqual(_work_and_charge(0,0,0,.0200001)[1],201)

    def test_bad_initial_conditions_and_private_balance(self):
        base=grid()[0]
        for patch in (
            {"x_a_m":-.2,"y_a_m":0.,"x_b_m":.2,"y_b_m":0.},
            {"x_a_m":-.5,"y_a_m":0.,"x_b_m":.5,"y_b_m":0.},
            {"x_a_m":float("nan")},
            {"command_ax_ns":.26},
            {"initial_balance_a_uj":-1},
            {"initial_balance_b_uj":True},
            {"mass_a_kg":2.},
            {"duration_s":3.},
            {"vx_a_mps":101.},
        ):
            with self.subTest(patch=patch),self.assertRaises(ValueError):
                validate(dict(base,**patch))
        self.assertEqual(len(invalid_probes()),5)

    def test_source_bound_archive_oracle_tamper_and_two_root_replay(self):
        with tempfile.TemporaryDirectory(prefix="f023-validation-") as tmp:
            a=Path(tmp)/"a";b=Path(tmp)/"b"
            output=produce(a,source_sha=SOURCE)
            self.assertEqual(output["worlds"],15)
            self.assertEqual(output["frames"],135)
            self.assertEqual(output["actions"],30)
            self.assertEqual(output["ledgers"],30)
            self.assertEqual(output["contacts"],9)
            self.assertEqual(verify(a,expected_source_sha=SOURCE)["contacts"],9)
            self.assertEqual(attack(a)["rehash_semantic_attacks_rejected"],10)
            produce(b,source_sha=SOURCE)
            self.assertEqual({p.name:p.read_bytes() for p in a.iterdir()},
                             {p.name:p.read_bytes() for p in b.iterdir()})
            with self.assertRaises(FileExistsError):
                produce(a,source_sha=SOURCE)
            with self.assertRaises(AssertionError):
                verify(a,expected_source_sha="b"*40)
            self.assertEqual(json.loads((a/"scenario.json").read_text())["schema_version"],
                             "f023.archive.v1")


if __name__=="__main__":
    unittest.main()
