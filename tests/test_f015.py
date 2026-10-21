"""F015: frozen controls, strict local boundary, tamper and replay."""
import csv
import hashlib
import json
from dataclasses import replace
from pathlib import Path
import shutil
import tempfile
import unittest

from soma.f007 import Config, simulate
from soma.f008 import project_local
from soma.f014 import PeerPacket
from soma.f015 import ProbeTrial, analyze_probe, SAME, CHANGED, UNKNOWN
from experiments.F015.run_suite import configuration, origin_snapshot, suite
from experiments.F015.verify import verify_suite


def episode(group, u):
    rows,_,_,_=simulate(Config.from_dict(configuration(group,u)))
    local=tuple(project_local(p,q) for p,q in zip(rows,rows[1:]))
    bits=tuple(PeerPacket("B",q["step_index"],q["time_s"],
             abs(q["v_b_m_s"]-p["v_b_m_s"])>1e-10)
             for p,q in zip(rows,rows[1:]))
    return ProbeTrial(local,bits)


def probe(group):
    return tuple(episode(group,u) for u in (2.,1.,0.))


def rehash(root: Path, relative: str) -> None:
    m=root/"manifest.json"
    manifest=json.loads(m.read_text(encoding="utf-8"))
    manifest["artifacts"][relative]=hashlib.sha256((root/relative).read_bytes()).hexdigest()
    m.write_text(json.dumps(manifest,sort_keys=True,indent=2)+"\n",encoding="utf-8")


class F015Tests(unittest.TestCase):
    def test_fixed_interventions_and_tracking_counterexample(self):
        data={g:probe(g) for g in ("L-linked","F-fixed","T-tracking",
                                   "N-free","E-disabled")}
        self.assertEqual(data["L-linked"][0],data["F-fixed"][0])
        self.assertEqual(data["L-linked"],data["T-tracking"])
        self.assertNotEqual(data["L-linked"][1],data["F-fixed"][1])
        outcomes={g:analyze_probe(p) for g,p in data.items()}
        self.assertEqual(outcomes["L-linked"]["a_only_status"],SAME)
        self.assertEqual(outcomes["T-tracking"]["a_plus_peer_status"],SAME)
        for g in ("F-fixed","N-free"):
            self.assertEqual(outcomes[g]["a_only_status"],CHANGED)
            self.assertEqual(outcomes[g]["a_plus_peer_status"],CHANGED)
        self.assertEqual(outcomes["E-disabled"]["a_only_status"],UNKNOWN)
        self.assertEqual(outcomes["F-fixed"]["peer_mismatch_steps"],4)
        self.assertTrue(all(not v["peer_incremental_discrimination"]
                            for v in outcomes.values()))
        for v in outcomes.values():
            for forbidden in ("connected","attached","topology_verified","case_id"):
                self.assertNotIn(forbidden,v)

    def test_frozen_world_case_configurations(self):
        for group in ("L-linked","F-fixed","T-tracking","N-free","E-disabled"):
            for u in (2.,1.,0.):
                with self.subTest(group=group,u=u):
                    config=configuration(group,u)
                    self.assertEqual(config["motor_force_n"],u)
                    self.assertEqual(config["cells"][0]["initial_v_m_s"],0.)
                    self.assertEqual(config["cells"][1]["initial_v_m_s"],0.)
        self.assertEqual(configuration("F-fixed",2.)["cells"][0]["external_force_n"],-1.)
        self.assertEqual(configuration("F-fixed",0.)["cells"][1]["external_force_n"],1.)
        with self.assertRaises(ValueError):
            configuration("G-ghost",2.)
        with self.assertRaises(ValueError):
            configuration("F-fixed",.5)

    def test_missing_peer_and_off_are_not_detachment(self):
        trials=list(probe("L-linked"))
        original=trials[2]
        trials[2]=ProbeTrial(original.a_local,
                     (original.b_packets[0],None,*original.b_packets[2:]))
        result=analyze_probe(tuple(trials))
        self.assertEqual(result["a_only_status"],SAME)
        self.assertEqual(result["a_plus_peer_status"],UNKNOWN)
        self.assertEqual(analyze_probe(probe("E-disabled"))["a_plus_peer_status"],UNKNOWN)

    def test_invalid_packet_clock_reset_and_truth_contamination(self):
        base=list(probe("L-linked"))
        t=base[0]
        problems=[
            replace(t.b_packets[0],source="A"),
            replace(t.b_packets[0],time_s=9.),
            replace(t.b_packets[0],moved=1),
            {"source":"B","step_index":1,"time_s":.25,"moved":True,
             "attached":True},
        ]
        for p in problems:
            bad=base[:]
            bad[0]=ProbeTrial(t.a_local,(p,*t.b_packets[1:]))
            with self.subTest(problem=str(p)),self.assertRaises(ValueError):
                analyze_probe(tuple(bad))
        bad=base[:]
        bad[1]=ProbeTrial((replace(base[1].a_local[0],v_prev_m_s=4.),
                           *base[1].a_local[1:]),base[1].b_packets)
        with self.assertRaises(ValueError):
            analyze_probe(tuple(bad))
        bad=base[:]
        bad[0]=ProbeTrial(({"attached":True},*t.a_local[1:]),t.b_packets)
        with self.assertRaises(ValueError):
            analyze_probe(tuple(bad))
        with self.assertRaises(ValueError):
            analyze_probe(tuple(base[:2]))

    def test_suite_hash_replay_and_rehashed_false_science(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            a,b=root/"a",root/"b"
            out=suite(a,b)
            self.assertEqual(out["cases"],15)
            self.assertEqual(out["a_local_intervals"],60)
            self.assertEqual(out["b_packet_intervals"],60)
            self.assertTrue(out["byte_replay"])
            self.assertFalse(out["peer_incremental_discrimination"])
            self.assertFalse(out["topology_identified"])
            with self.assertRaises(ValueError):
                suite(a,root/"unused")
            # False physical evidence with recomputed manifest hash.
            fake=root/"fake-bit"
            shutil.copytree(a,fake)
            path="F-fixed/u0/b_packets.csv"
            file=fake/path
            with file.open(newline="",encoding="utf-8") as f:
                rows=list(csv.DictReader(f))
                names=list(rows[0])
            rows[0]["moved"]="False"
            with file.open("w",newline="",encoding="utf-8") as f:
                w=csv.DictWriter(f,fieldnames=names)
                w.writeheader()
                w.writerows(rows)
            rehash(fake,path)
            with self.assertRaises(AssertionError):
                verify_suite(fake,origin_snapshot())
            # Rehashed fabricated topology claim must be rejected.
            fake2=root/"fake-science"
            shutil.copytree(a,fake2)
            cmp=fake2/"comparison.json"
            summary=json.loads(cmp.read_text(encoding="utf-8"))
            summary["topology_identified"]=True
            cmp.write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n",
                           encoding="utf-8")
            rehash(fake2,"comparison.json")
            with self.assertRaises(AssertionError):
                verify_suite(fake2,origin_snapshot())
            # A-only vs augmented benefit forgery.
            fake3=root/"fake-peer"
            shutil.copytree(a,fake3)
            cmp=fake3/"comparison.json"
            summary=json.loads(cmp.read_text(encoding="utf-8"))
            summary["B_unique_incremental_value"]=True
            cmp.write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n",
                           encoding="utf-8")
            rehash(fake3,"comparison.json")
            with self.assertRaises(AssertionError):
                verify_suite(fake3,origin_snapshot())


if __name__=="__main__":
    unittest.main()
