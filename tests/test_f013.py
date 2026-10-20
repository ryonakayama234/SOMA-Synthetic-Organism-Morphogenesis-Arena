"""F013 numerical invariants, frozen cases, tamper and independent audit."""
from __future__ import annotations
import csv
import json
from pathlib import Path
import tempfile
import unittest

from soma.f013 import Config, passive_contact, simulate, EPSILONS, DTS, CASES, StrokeLimitError
from experiments.F013.run_suite import build
from experiments.F013.verify import verify


class TestF013(unittest.TestCase):
    def test_strict_frozen_configuration(self):
        for args in (("A-no-contact",.02,.01),("C-directional",.012,.01),
                     ("C-directional",.02,.003),("C-directional",.02,1)):
            with self.assertRaises(ValueError):
                Config(*args)

    def test_implicit_ground_passive_and_equality(self):
        import math
        for vs in (-.5,-.01,0,.01,.5):
            for eps in EPSILONS:
                v,f=passive_contact(vs,.01,.02,.08,eps)
                self.assertLessEqual(f*v,1e-11)
                mu=.02 if v>0 else .08
                self.assertAlmostEqual(v-vs+.01*9.81*mu*math.tanh(v/eps),0,delta=3e-12)
        with self.assertRaises(ValueError):
            passive_contact(float("nan"),.01,.02,.08,.02)

    def test_mirror_symmetric_negative_controls(self):
        h,eps=.01,.02
        b=simulate(Config("B-isotropic",eps,h))
        c=simulate(Config("C-directional",eps,h))
        d=simulate(Config("D-mirror",eps,h))
        e=simulate(Config("E-no-drive",eps,h))
        self.assertEqual(len(b),961)
        for x in b:
            self.assertAlmostEqual(x["x_cm_m"],0,delta=1e-10)
        for x in e:
            self.assertAlmostEqual(x["x_cm_m"],0,delta=1e-10)
        self.assertEqual(len(c),len(d))
        for x,y in zip(c,d):
            self.assertAlmostEqual(x["x_a_m"],-y["x_b_m"],delta=2e-9)
            self.assertAlmostEqual(x["r_m"],y["r_m"],delta=2e-9)
            self.assertAlmostEqual(x["x_cm_m"],-y["x_cm_m"],delta=2e-9)

    def test_wolfram_independent_first_step_reference(self):
        """Post-preregistration Wolfram high-precision independent arithmetic check."""
        z=simulate(Config("C-directional", .02, .01))[1]
        self.assertAlmostEqual(z["v_a_m_s"], .009159421988891862, delta=5e-12)
        self.assertAlmostEqual(z["v_b_m_s"], -.007267468045899013, delta=5e-12)
        self.assertAlmostEqual(z["x_cm_m"], .000009459769714964243, delta=5e-13)
        self.assertAlmostEqual(z["ground_work_j"], -.000027557797379149775, delta=5e-13)

    def test_complete_36_case_independent_raw_audit_and_forgery(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"dataset"
            build(path)
            observations=verify(path)
            self.assertEqual(len(observations["h13b"]),12)
            self.assertEqual(len(observations["eps_results"]),3)
            report=path/"comparison.json"
            manifest=path/"manifest.json"
            data=json.loads(report.read_text())
            data["results"]["C-directional/eps-0.001/dt-0.0025"]["center_final_m"]+=.125
            report.write_text(json.dumps(data,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
            import hashlib
            man=json.loads(manifest.read_text())
            man["files_sha256"]["comparison.json"]=hashlib.sha256(report.read_bytes()).hexdigest()
            manifest.write_text(json.dumps(man,indent=2,sort_keys=True,ensure_ascii=False)+"\n")
            with self.assertRaises(AssertionError):
                verify(path)

    def test_reproduction_without_tampering_or_hidden_states(self):
        from soma.f013 import COLUMNS, SCHEMA
        self.assertEqual(SCHEMA,"f013.states.v1")
        self.assertNotIn("topology",COLUMNS)
        self.assertNotIn("cell_local",COLUMNS)


if __name__ == "__main__":
    unittest.main()
