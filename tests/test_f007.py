"""F007 tests: frozen Wolfram references, battery ownership, adverse inputs and saved-file oracle."""
from __future__ import annotations

import copy
from pathlib import Path
import tempfile
import unittest

from soma.f007 import Config, simulate, save_run
from experiments.F007.run_suite import baseline, scenarios, suite, compare_full
from experiments.F007.verify import audit_run


class F007Tests(unittest.TestCase):
    def test_wolfram_reference_all_cases(self):
        expected={
            "A-free":(1.25,0.5,2.,0.,2_000_000,0),
            "B-linked":(.625,1.125,1.,1.,1_000_000,0),
            "C-zero":(0.,.5,0.,0.,0,0),
            "D-external":(.625,1.125,1.,1.,0,0),
            "E-cut":(.8125,.9375,1.5,.5,1_250_000,0),
            "F-01":(.25,.75,.25,.25,62_500,0),
            "F-02":(0.,.5,0.,0.,0,0),
            "F-03":(.625,1.125,1.,1.,0,0),
            "F-04":(-.75,-.25,-.75,-.75,562_500,0),
        }
        for key,raw in scenarios().items():
            with self.subTest(key=key):
                rows,events,link,ledger=simulate(Config.from_dict(raw))
                z=rows[-1]
                self.assertEqual(
                    (z["x_a_m"],z["x_b_m"],z["v_a_m_s"],z["v_b_m_s"],
                     ledger.spent_uj,ledger.cell("B").balance_uj),
                    expected[key])
                self.assertEqual(ledger.residual_uj,0)
                self.assertEqual(sum(e["amount_uj"] for e in events),ledger.spent_uj)
                self.assertTrue(all(e["source_id"]=="A" and
                                    e["target_id"] is None for e in events))
                self.assertTrue(all(abs(r["link_force_a_n"]+
                                        r["link_force_b_n"])<1e-12 for r in rows))

    def test_midrun_battery_refusal_preserves_link(self):
        rows,entries,link,ledger=simulate(Config.from_dict(scenarios()["F-01"]))
        self.assertEqual(len(entries),1)
        self.assertEqual([r["motor_applied_n"] for r in rows[1:]],[2.,0.,0.,0.])
        self.assertEqual([r["decision_reason"] for r in rows[1:]],
                         ["accepted_positive_work"]+["zero_balance"]*3)
        self.assertEqual([r["candidate_motor_positive_work_j"] for r in rows[2:]],
                         [None]*3)
        self.assertTrue(all(r["attached"] for r in rows))
        self.assertEqual(ledger.cell("A").balance_uj,0)

    def test_no_false_transfer_and_external_only(self):
        for label in ("D-external","F-03"):
            rows,events,links,ledger=simulate(Config.from_dict(scenarios()[label]))
            self.assertFalse(events)
            self.assertEqual(ledger.spent_uj,0)
            self.assertEqual(rows[-1]["link_force_b_n"],-1.)
            self.assertEqual(rows[-1]["v_a_m_s"],1.)
            self.assertEqual(ledger.cell("B").balance_uj,0)

    def test_no_free_static_hold_claim(self):
        rows,events,_,_=simulate(Config.from_dict(scenarios()["F-02"]))
        self.assertFalse(events)
        self.assertTrue(all(r["motor_applied_n"]==2 and r["spent_a_uj"]==0
                            and r["decision_reason"]=="accepted_nonpositive_work"
                            for r in rows[1:]))

    def test_detach_continuity(self):
        rows,_,links,_=simulate(Config.from_dict(scenarios()["E-cut"]))
        self.assertEqual(links[-1]["kind"],"detach")
        self.assertEqual(links[-1]["time_s"],.5)
        for name in ("x_a","x_b","v_a","v_b"):
            suffix="m_s" if name.startswith("v") else "m"
            key=f"{name}_before_{suffix}"
            after=f"{name}_after_{suffix}"
            self.assertEqual(links[-1][key],links[-1][after])
        self.assertFalse(rows[2]["attached"])
        self.assertEqual(rows[2]["link_force_b_n"],0.)

    def test_validation_pathologies(self):
        changes=[
            lambda c:c.update(dt_s=0),
            lambda c:c.update(duration_s=.3),
            lambda c:c.update(motor_force_n=float("nan")),
            lambda c:c.update(motor_force_n=True),
            lambda c:c["cells"][0].update(capacity_uj=0),
            lambda c:c["cells"][1].update(initial_balance_uj=-1),
            lambda c:c["cells"][0].update(mass_kg=0),
            lambda c:c["cells"][1].update(initial_x_m=.6),
            lambda c:c["cells"][1].update(initial_v_m_s=.1),
            lambda c:c["link"].update(detach_time_s=.3),
            lambda c:c.update(seed=1),
            lambda c:c.update(schema_version="f003.v1"),
            lambda c:c.update(extra_field=10),
        ]
        for fn in changes:
            c=baseline("bad");fn(c)
            with self.subTest(fn=fn),self.assertRaises((ValueError,TypeError)):
                Config.from_dict(c)

    def test_saved_evidence_and_tamper(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"F007"
            c=Config.from_dict(scenarios()["B-linked"])
            m=save_run(c,p,identity={"git_commit":"synthetic-local-test","git_dirty":False,"source_hashes":{}})
            outcome=audit_run(p)
            self.assertEqual(outcome["saved_rows_checked"],5)
            self.assertEqual(m["spent_uj"],1_000_000)
            csv=p/"states.csv"
            csv.write_text(csv.read_text().replace("0.625","0.626",1))
            with self.assertRaises(AssertionError):
                audit_run(p)
            with self.assertRaises(FileExistsError):
                save_run(c,p)

    def test_suite_byte_replay(self):
        with tempfile.TemporaryDirectory() as temp:
            a,b=Path(temp)/"one",Path(temp)/"two"
            r=suite(a);suite(b)
            count=compare_full(a,b)
            self.assertEqual(r["number_of_runs"],9)
            self.assertEqual(len(r["test_negative_cases"]),12)
            self.assertTrue(r["tampering_detected"])
            self.assertGreaterEqual(count,55)


if __name__=="__main__":
    unittest.main()
