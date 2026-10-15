"""F003 pre-registered invariants. Pure stdlib test suite."""
from __future__ import annotations
import math
import csv
import json
from decimal import localcontext
import subprocess
import sys
from unittest.mock import patch
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


    def test_time_grid_is_independent_of_decimal_context(self):
        for precision in (3,28,60):
            with self.subTest(precision=precision),localcontext() as ctx:
                ctx.prec=precision
                with self.assertRaises(ValueError):
                    Config.from_dict(config(dt_s=.03))
                with self.assertRaises(ValueError):
                    Config.from_dict(config(link_detach_time_s=5.005))
                self.assertEqual(Config.from_dict(config()).steps,1000)

    def test_finite_inputs_do_not_save_nonfinite_derived_values(self):
        cfg=Config.from_dict(config(a_mass_kg=1e200,b_mass_kg=1e200,a_force_n=1e200))
        self.assertAlmostEqual(link_forces(cfg)[1]/1e200,.5,delta=1e-15)
        rows,_=simulate(cfg)
        self.assertAlmostEqual(rows[-1]["v_a_m_s"],2.162338693883291,delta=1e-9)
        self.assertTrue(all(value is None or math.isfinite(value)
                            for row in rows for value in row.values()))
        # Weighted center of mass must not overflow a mass*position product.
        rows,_=simulate(Config.from_dict(config(False,a_mass_kg=2.,b_mass_kg=2.,
              a_initial_x_m=1e308,b_initial_x_m=1e308,a_force_n=0.)))
        self.assertEqual(rows[0]["center_of_mass_m"],1e308)

    def test_unrepresentable_aggregates_and_dynamic_state_rejected_before_files(self):
        invalid=[config(a_mass_kg=1e308,b_mass_kg=1e308),
                 config(a_force_n=1e308,b_force_n=1e308),
                 config(a_mass_kg=10**1000),
                 config(False,a_mass_kg=1e-300,a_force_n=1e300)]
        with tempfile.TemporaryDirectory() as tmp:
            for i,raw in enumerate(invalid):
                dest=Path(tmp)/str(i)
                with self.subTest(index=i),self.assertRaises(ValueError):
                    save_run(Config.from_dict(raw),dest)
                self.assertFalse(dest.exists())

    def test_full_suite_evidence_and_comparison_replay(self):
        from experiments.F003.run_suite import suite,checksum
        with tempfile.TemporaryDirectory() as tmp:
            first,second=Path(tmp)/"first",Path(tmp)/"second"
            result=suite(first)
            suite(second)
            self.assertEqual(result["rejections_sha256"],checksum(first/"rejections.json"))
            self.assertTrue(all(result["gate_checks"].values()))
            for name,case in result["cases"].items():
                if name=="theory": continue
                self.assertLessEqual(case["gates"]["max_oracle_x_error_m"],1e-9)
                self.assertLessEqual(case["gates"]["max_internal_force_sum_n"],1e-12)
            for case in result["rejections"]:
                self.assertIn("input",case)
                self.assertTrue(case["pass"])
            paths=sorted(p.relative_to(first) for p in first.rglob("*") if p.is_file())
            self.assertEqual(paths,sorted(p.relative_to(second) for p in second.rglob("*") if p.is_file()))
            for path in paths:
                self.assertEqual((first/path).read_bytes(),(second/path).read_bytes(),str(path))

    def test_suite_rejects_corrupted_saved_evidence(self):
        import experiments.F003.run_suite as runner
        real=runner.save_run
        cases=[("A-free","states.csv",100,"x_a_m",3.,"discrete position"),
               ("B-pull","states.csv",0,"link_force_a_n",8.,"internal forces"),
               ("C-both","states.csv",100,"v_b_m_s",.01,"velocity error log"),
               ("D-cut","states.csv",501,"x_b_m",3.,"discrete position"),
               ("D-cut","events.csv",1,"x_b_before_m",3.,"event/CSV continuity"),
               ("E-minus","states.csv",100,"x_b_m",3.,"distance error log"),
               ("B-pull","states.csv",10,"center_of_mass_m",3.,"center of mass"),
               ("B-pull","states.csv",10,"v_a_m_s",float("inf"),"non-finite")]
        with tempfile.TemporaryDirectory() as tmp:
            for i,(case,filename,index,field,delta,message) in enumerate(cases):
                def corrupt(cfg,dest,**kwargs):
                    manifest=real(cfg,dest,**kwargs)
                    if cfg.experiment_id=="F003-"+case:
                        with (dest/filename).open(newline="") as stream:
                            reader=csv.DictReader(stream)
                            fields=reader.fieldnames
                            rows=list(reader)
                        rows[index][field]=str(float(rows[index][field])+delta)
                        # A copied lie within events.csv must still fail the CSV cross-check.
                        if filename=="events.csv":
                            rows[index][field.replace("before","after")]=rows[index][field]
                        with (dest/filename).open("w",newline="") as stream:
                            writer=csv.DictWriter(stream,fieldnames=fields)
                            writer.writeheader(); writer.writerows(rows)
                    return manifest
                with self.subTest(case=case,field=field),patch.object(runner,"save_run",corrupt):
                    with self.assertRaisesRegex(AssertionError,message):
                        runner.suite(Path(tmp)/str(i))

    def test_optimized_python_keeps_suite_semantic_gates(self):
        code = r"""
from pathlib import Path
from unittest.mock import patch
import csv, tempfile
import experiments.F003.run_suite as runner
real=runner.save_run
def corrupt(cfg,dest,**kwargs):
    manifest=real(cfg,dest,**kwargs)
    if cfg.experiment_id=='F003-D-cut':
        with (dest/'events.csv').open(newline='') as stream:
            reader=csv.DictReader(stream); fields=reader.fieldnames; rows=list(reader)
        rows[1]['x_a_before_m']=rows[1]['x_a_after_m']='99'
        with (dest/'events.csv').open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    return manifest
with tempfile.TemporaryDirectory() as tmp, patch.object(runner,'save_run',corrupt):
    try: runner.suite(Path(tmp)/'corrupt')
    except AssertionError as exc:
        if 'event/CSV continuity' not in str(exc): raise
    else: raise RuntimeError('optimized Python accepted corrupted evidence')
"""
        result=subprocess.run([sys.executable,"-O","-c",code],cwd=Path(__file__).resolve().parents[1],
                              text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

if __name__=="__main__":
    unittest.main()
