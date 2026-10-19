"""F009 closed-system force balance, ground reaction, F007 baseline and tamper tests."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from soma.f009 import CASES, config_for, simulate, save_run, validate
from experiments.F009.run_suite import generate, run_pair
from experiments.F009.verify import verify_run, verify_suite, oracle

class F009Tests(unittest.TestCase):
    def test_fixed_references_every_step(self):
        for case in CASES:
            with self.subTest(case=case):
                rows=simulate(config_for(case))
                expected=oracle(case)
                self.assertEqual(len(rows),len(expected))
                for actual,want in zip(rows,expected):
                    for field,reference in want.items():
                        self.assertAlmostEqual(actual[field],float(reference),places=12,
                                               msg=f"{case} step{actual['step_index']} {field}")
                    self.assertAlmostEqual(actual["link_force_a_n"]+
                                           actual["link_force_b_n"],0.0,places=12)
                    self.assertAlmostEqual(actual["momentum_residual_ns"],0.0,places=12)

    def test_legacy_f007_is_unchanged(self):
        from experiments.F007.run_suite import baseline
        from soma.f007 import Config,simulate as legacy_simulate
        raw=baseline("B-linked")
        rows,events,link,ledger=legacy_simulate(Config.from_dict(raw))
        new=simulate(config_for("A"))
        self.assertEqual(
            (rows[-1]["x_a_m"],rows[-1]["x_b_m"],rows[-1]["v_a_m_s"],rows[-1]["v_b_m_s"]),
            (new[-1]["x_a_m"],new[-1]["x_b_m"],new[-1]["v_a_m_s"],new[-1]["v_b_m_s"]))
        self.assertEqual(ledger.spent_uj,1_000_000)
        self.assertEqual(ledger.cell("B").balance_uj,0)

    def test_closed_internal_and_ground_impulses(self):
        b=simulate(config_for("B"))
        c=simulate(config_for("C"))
        d=simulate(config_for("D"))
        f=simulate(config_for("F"))
        self.assertEqual(b[-1]["p_after_kg_m_s"],0)
        self.assertEqual(d[-1]["p_after_kg_m_s"],0)
        self.assertEqual(sum(x["ground_reaction_n"]*.25 for x in c[1:]),-2)
        self.assertEqual(sum(x["ground_reaction_n"]*.25 for x in f[1:]),-1)
        self.assertEqual(f[-1]["v_a_m_s"],.5)
        self.assertEqual(simulate(config_for("A"))[-1]["x_a_m"],c[-1]["x_a_m"])

    def test_fixed_contract_rejects_mutations(self):
        for label,field,value in [
            ("A","dt_s",.3),("C","traction_limit_n",-1.0),
            ("C","contact_enabled",False),("F","drive_command_n",float("nan")),
            ("B","mass_a_kg",0.0),("A","mass_a_kg",True),
            ("D","force_origin","legacy_effective"),
            ("E","attached",True),("A","x_b0_m",.6),
        ]:
            cfg=config_for(label)
            cfg[field]=value
            with self.subTest(field=field,label=label):
                with self.assertRaises(ValueError):
                    validate(cfg)
        with self.assertRaises(ValueError):
            config_for("G")

    def test_saved_origin_semantics_and_replay(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d)
            result=run_pair(base/"run",base/"replay")
            self.assertEqual([c["case"] for c in result["cases"]],list(CASES))
            self.assertEqual(verify_suite(base/"run"),verify_suite(base/"replay"))
            with self.assertRaises(FileExistsError):
                run_pair(base/"run",base/"new")
            with self.assertRaises(ValueError):
                run_pair(base/"a",base/"a"/"nested")

    def test_rehashed_csv_forgery_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/"case"
            save_run(config_for("C"),target)
            self.assertEqual(verify_run(target)["case"],"C")
            csv=target/"steps.csv"
            original=csv.read_text(encoding="utf-8")
            csv.write_text(original.replace("0.0625","0.125",1),encoding="utf-8")
            manifest=target/"manifest.json"
            m=json.loads(manifest.read_text(encoding="utf-8"))
            m["artifacts"]["steps.csv"]=hashlib.sha256(csv.read_bytes()).hexdigest()
            manifest.write_text(json.dumps(m,sort_keys=True,indent=2)+"\n",encoding="utf-8")
            with self.assertRaises(ValueError):
                verify_run(target)

    def test_forged_interpretation_and_source(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"evidence"
            generate(root)
            self.assertEqual(len(verify_suite(root)["cases"]),6)
            report=root/"comparison.json"
            x=json.loads(report.read_text(encoding="utf-8"))
            x["science_status"]="formally_adopted"
            report.write_text(json.dumps(x,sort_keys=True,indent=2)+"\n",encoding="utf-8")
            outer=root/"suite_manifest.json"
            m=json.loads(outer.read_text(encoding="utf-8"))
            m["artifacts"]["comparison.json"]=hashlib.sha256(report.read_bytes()).hexdigest()
            outer.write_text(json.dumps(m,sort_keys=True,indent=2)+"\n",encoding="utf-8")
            with self.assertRaises(ValueError):
                verify_suite(root)

if __name__=="__main__":
    unittest.main()
