"""F023 frozen hypotheses: controlled 2D contact, private motor fee, audit."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from soma.f023 import FREEZE_COMMIT, grid, simulate, validate, _work_and_charge
from experiments.F023.run_suite import produce, invalid_probes
from experiments.F023.verify import (verify, reference_roster, strictly_same,
                                    check_action_inputs_exact, expected_scene, gate_saved_conservation)
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

    def test_frozen_inputs_have_no_numeric_tolerance(self):
        original=reference_roster()
        scen={"schema_version":"f023.archive.v1", "worlds":original}
        strictly_same(scen,{"schema_version":"f023.archive.v1",
                            "worlds":reference_roster()})
        for field,value in (("command_ay_ns",.0200000001),
                            ("vy_a_mps",1e-10),
                            ("x_b_m",1.0000000001),
                            ("initial_balance_a_uj",201)):
            altered={"schema_version":"f023.archive.v1",
                     "worlds":[dict(x) for x in original]}
            altered["worlds"][1][field]=value
            with self.subTest(field=field), self.assertRaises(AssertionError):
                strictly_same(altered,scen)
        # Numerics may never silently turn bool into integer.
        with self.assertRaises(AssertionError):
            strictly_same(True,1)

    def test_own_action_billing_inputs_exact_even_when_close(self):
        _,actions,_,_,_=expected_scene(reference_roster()[1])
        for field in ("command_y_ns", "applied_y_ns", "ground_y_ns",
                      "pre_vy_mps"):
            altered=[dict(r) for r in actions]
            altered[0][field] += 1e-10
            with self.subTest(field=field),self.assertRaises(AssertionError):
                check_action_inputs_exact(altered,actions)
        check_action_inputs_exact(actions,actions)

    def test_saved_conservation_gates_each_frame_not_oracle_only(self):
        scenes=reference_roster()
        frames=[];actions=[];events=[];audits=[]
        for scene in scenes:
            f,a,e,_,audit=expected_scene(scene)
            frames.extend(f);actions.extend(a);events.extend(e);audits.append(audit)
        audit={"world_results":audits,
               "momentum_residual_kg_mps":max(x["momentum_residual_kg_mps"] for x in audits),
               "energy_residual_j":max(abs(x["energy_residual_j"]) for x in audits),
               "overlap_bound_m":max(x["overlap_bound_m"] for x in audits)}
        gate_saved_conservation(scenes,frames,actions,events,audit)
        for sample in (-1,-3):
            tampered=[dict(f) for f in frames]
            row=tampered[sample]
            row["vx_a_mps"]+=5e-8
            row["total_ke_j"]=.5*sum(row[f"v{axis}_{c}_mps"]**2
                                       for c in ("a","b") for axis in ("x","y"))
            with self.subTest(sample=sample),self.assertRaisesRegex(
                AssertionError,"saved physical conservation broken"
            ):
                gate_saved_conservation(scenes,tampered,actions,events,audit)

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
            self.assertEqual(attack(a)["rehash_semantic_attacks_rejected"],16)
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
