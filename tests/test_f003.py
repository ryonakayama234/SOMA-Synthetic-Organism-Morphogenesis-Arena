"""F003 pre-registered invariants. Pure stdlib test suite."""
from __future__ import annotations
import math
from pathlib import Path
import tempfile
import unittest
from soma.f003 import Config,link_forces,simulate,save_run

def config(attached=True, **changes):
    d={"schema_version":"f003.v1","experiment_id":"F003-test","seed":None,
       "dt_s":0.01,"duration_s":10.0,"drag_per_s":0.2,
       "cells":[{"id":"A","mass_kg":1.0,"initial_x_m":0.0,"initial_v_m_s":0.0,"force_n":1.0},
                {"id":"B","mass_kg":1.0,"initial_x_m":0.5,"initial_v_m_s":0.0,"force_n":0.0}],
       "link":{"initially_attached":attached,"length_m":0.5,"detach_time_s":None}}
    for key,val in changes.items():
        if key.startswith("a_"): d["cells"][0][key[2:]]=val
        elif key.startswith("b_"): d["cells"][1][key[2:]]=val
        elif key.startswith("link_"): d["link"][key[5:]]=val
        else: d[key]=val
    return d

class TestF003(unittest.TestCase):
    def test_a_independent_f001_discrete_oracle(self):
        rows,events=simulate(Config.from_dict(config(False)))
        self.assertEqual(events,[])
        x,v=0.,0.
        for row in rows:
            self.assertAlmostEqual(row["x_a_m"],x,delta=1e-9)
            self.assertAlmostEqual(row["v_a_m_s"],v,delta=1e-9)
            self.assertEqual(row["x_b_m"],.5)
            self.assertEqual(row["v_b_m_s"],0.)
            self.assertEqual(row["link_force_b_n"],0.)
            v=v+.01*(1.-.2*v)
            x=x+.01*v

    def test_b_link_force_and_constraints(self):
        rows,events=simulate(Config.from_dict(config()))
        self.assertEqual(len(events),1)
        x,v=0.,0.
        for row in rows:
            self.assertLessEqual(abs(row["x_a_m"]-x),1e-9)
            self.assertLessEqual(abs(row["v_a_m_s"]-v),1e-9)
            self.assertLessEqual(abs(row["distance_constraint_error_m"]),1e-10)
            self.assertLessEqual(abs(row["velocity_constraint_error_m_s"]),1e-12)
            self.assertAlmostEqual(row["link_force_b_n"],.5,delta=1e-12)
            self.assertEqual(row["link_force_a_n"]+row["link_force_b_n"],0.)
            v=v+.01*(.5-.2*v)
            x=x+.01*v
        self.assertAlmostEqual(rows[-1]["x_a_m"],14.209929917522378,delta=1e-9)
        self.assertAlmostEqual(rows[-1]["v_a_m_s"],2.162338693883291,delta=1e-9)

    def test_c_symmetric_drive_zero_link_force(self):
        rows,_=simulate(Config.from_dict(config(b_force_n=1.)))
        self.assertTrue(all(r["link_force_b_n"]==0. for r in rows))

    def test_d_detach_without_impulse_and_next_interval_free(self):
        rows,events=simulate(Config.from_dict(config(link_detach_time_s=5.)))
        det=events[1]
        self.assertEqual(det["kind"],"detach")
        self.assertEqual(det["time_s"],5.)
        for variable,unit in (("x_a","m"),("x_b","m"),("v_a","m_s"),("v_b","m_s")):
            self.assertEqual(det[f"{variable}_before_{unit}"],det[f"{variable}_after_{unit}"])
        self.assertFalse(rows[500]["attached"])
        self.assertEqual(rows[500]["link_force_b_n"],0.)
        self.assertIsNone(rows[500]["distance_constraint_error_m"])
        self.assertAlmostEqual(rows[501]["v_a_m_s"],
          rows[500]["v_a_m_s"]+.01*(1.-.2*rows[500]["v_a_m_s"]),delta=1e-12)
        self.assertAlmostEqual(rows[501]["v_b_m_s"],
          rows[500]["v_b_m_s"]-.01*.2*rows[500]["v_b_m_s"],delta=1e-12)

    def test_e_force_reflection(self):
        pos,_=simulate(Config.from_dict(config()))
        neg,_=simulate(Config.from_dict(config(a_force_n=-1.)))
        for a,b in zip(pos,neg):
            self.assertLessEqual(abs(a["x_a_m"]+b["x_a_m"]),1e-9)
            self.assertLessEqual(abs(a["v_a_m_s"]+b["v_a_m_s"]),1e-9)

    def test_f_dt_convergence_against_continuous_solution(self):
        exact=2.5*(10-(1-math.exp(-2))/.2)
        errors=[]
        for dt in (.01,.005,.0025):
            rows,_=simulate(Config.from_dict(config(dt_s=dt)))
            errors.append(abs(rows[-1]["x_a_m"]-exact))
        self.assertTrue(errors[0]>errors[1]>errors[2])
        self.assertTrue(all(1.8<a/b<2.2 for a,b in zip(errors,errors[1:])))

    def test_asymmetric_masses_not_hardcoded_half_newton(self):
        cfg=Config.from_dict(config(a_mass_kg=2.))
        ta,tb=link_forces(cfg)
        self.assertAlmostEqual(tb,1./3.,delta=1e-15)
        self.assertEqual(ta+tb,0.)
        rows,_=simulate(cfg)
        self.assertAlmostEqual(rows[1]["v_a_m_s"],.01/3.,delta=1e-12)

    def test_invalid_configs_are_rejected_before_output(self):
        values=[config(a_mass_kg=0),config(a_force_n=float("nan")),
                config(b_initial_x_m=.6),config(b_initial_v_m_s=.1),
                config(link_detach_time_s=.005),config(link_detach_time_s=10.),
                config(dt_s=.03),config(link_initially_attached=False,link_detach_time_s=5.),
                config(a_mass_kg=True),config(experiment_id="bad\u0000"),
                config(experiment_id="bad\ud800")]
        with tempfile.TemporaryDirectory() as tmp:
            for i,data in enumerate(values):
                dest=Path(tmp)/f"rejected-{i}"
                with self.subTest(index=i),self.assertRaises(ValueError):
                    save_run(Config.from_dict(data),dest)
                self.assertFalse(dest.exists())

    def test_same_inputs_byte_identical_outputs(self):
        cfg=Config.from_dict(config())
        identity=dict(git_commit="test",git_dirty=False,module_sha256="test")
        with tempfile.TemporaryDirectory() as tmp:
            a,b=Path(tmp)/"run",Path(tmp)/"replay"
            save_run(cfg,a,provenance_data=identity,suite_sha256="test")
            save_run(cfg,b,provenance_data=identity,suite_sha256="test")
            for name in ("config.json","states.csv","events.csv","motion.svg","manifest.json"):
                self.assertEqual((a/name).read_bytes(),(b/name).read_bytes())


    def test_c_equal_drive_matches_independent_mass_oracle(self):
        rows,_=simulate(Config.from_dict(config(b_force_n=1.)))
        v,x=0.,0.
        for row in rows:
            self.assertAlmostEqual(row["x_a_m"],x,delta=1e-9)
            self.assertAlmostEqual(row["v_a_m_s"],v,delta=1e-9)
            self.assertAlmostEqual(row["x_b_m"]-row["x_a_m"],.5,delta=1e-10)
            v=v+.01*(1.-.2*v)
            x=x+.01*v

    def test_d_every_post_cut_state_matches_independent_oracle(self):
        rows,events=simulate(Config.from_dict(config(link_detach_time_s=5.)))
        self.assertEqual(len(events),2)
        r=rows[500]
        xa,xb,va,vb=r["x_a_m"],r["x_b_m"],r["v_a_m_s"],r["v_b_m_s"]
        for state in rows[501:]:
            va=va+.01*(1.-.2*va)
            xa=xa+.01*va
            vb=vb+.01*(-.2*vb)
            xb=xb+.01*vb
            self.assertAlmostEqual(state["x_a_m"],xa,delta=1e-9)
            self.assertAlmostEqual(state["x_b_m"],xb,delta=1e-9)
            self.assertAlmostEqual(state["v_a_m_s"],va,delta=1e-9)
            self.assertAlmostEqual(state["v_b_m_s"],vb,delta=1e-9)
            self.assertFalse(state["attached"])
            self.assertEqual(state["link_force_a_n"],0.)
            self.assertEqual(state["link_force_b_n"],0.)

if __name__=="__main__":
    unittest.main()
