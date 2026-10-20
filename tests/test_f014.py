"""F014 preregistered experiment gates and adversarial evidence checks."""
import csv
import hashlib
import json
from dataclasses import replace
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from soma.f007 import Config, simulate
from soma.f008 import LocalObservation, project_local
from soma.f014 import PeerPacket, estimate_trial, validate_packet
from experiments.F014.run_suite import configuration, origin_snapshot, suite
from experiments.F014.verify import verify_suite


def trial(group="L-linked", force=2.):
    states, _, _, _ = simulate(Config.from_dict(configuration(group, force)))
    a = tuple(project_local(p, q) for p, q in zip(states, states[1:]))
    bits = tuple(PeerPacket("B", q["step_index"], q["time_s"],
                            abs(q["v_b_m_s"]-p["v_b_m_s"]) > 1e-10)
                 for p, q in zip(states, states[1:]))
    return a, bits


class F014Tests(unittest.TestCase):
    def test_frozen_15_cases_and_strict_equivalence(self):
        for u in (2., 1., .5):
            with self.subTest(u=u):
                l_a, l_b = trial("L-linked", u)
                g_a, g_b = trial("G-ghost", u)
                c_a, c_b = trial("C-coforced", u)
                n_a, n_b = trial("N-free", u)
                e_a, e_b = trial("E-unexcited", u)
                self.assertEqual(l_a, g_a)
                self.assertEqual(l_a, c_a)
                self.assertEqual(l_b, c_b)
                self.assertNotEqual(l_b, g_b)
                for group, a, b, expected in (
                    ("L", l_a,l_b,"peer_motion_seen"),
                    ("G", g_a,g_b,"peer_still"),
                    ("C", c_a,c_b,"peer_motion_seen"),
                    ("N", n_a,n_b,"peer_still"),
                    ("E", e_a,e_b,"inconclusive"),
                ):
                    self.assertEqual(estimate_trial(a,b)["status"], expected, group)
                    self.assertNotIn("attached", estimate_trial(a,b))
                    self.assertNotIn("topology_verified", estimate_trial(a,b))

    def test_binary_boundary_and_missing_packet(self):
        a, b = trial()
        result = estimate_trial(a, (b[0], None, b[2], b[3]))
        self.assertEqual(result["status"], "inconclusive")
        self.assertEqual(result["step_statuses"][1], "inconclusive")
        for wrong in (replace(b[0], source="A"), replace(b[0], step_index=2),
                      replace(b[0], time_s=.5), replace(b[0], moved=1),
                      {"source":"B","step_index":1,"time_s":.25,
                       "moved":True,"attached":True}):
            with self.subTest(wrong=str(wrong)):
                with self.assertRaises(ValueError):
                    estimate_trial(a, (wrong, *b[1:]))
        with self.assertRaises((ValueError, TypeError)):
            PeerPacket("B", 1, .25, True, attached=True)
        with self.assertRaises(ValueError):
            estimate_trial(({"attached":True}, *a[1:]), b)
        with self.assertRaises(ValueError):
            estimate_trial(a, b[:3])
        with self.assertRaises(ValueError):
            estimate_trial((replace(a[0], time_s=.5), *a[1:]), b)
        with self.assertRaises(ValueError):
            estimate_trial((a[0], replace(a[1], v_prev_m_s=9.), *a[2:]), b)

    def test_actual_excitation_required_even_with_positive_peer_bit(self):
        a, b = trial("E-unexcited")
        forged = tuple(replace(p, moved=True) for p in b)
        self.assertEqual(estimate_trial(a, forged)["status"], "inconclusive")

    def test_suite_exact_replay_and_manifest_tamper(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            a, b = root/"a", root/"b"
            result = suite(a,b)
            self.assertEqual(result["cases"], 15)
            self.assertEqual(result["local_intervals"],60)
            self.assertTrue(result["byte_replay"])
            self.assertTrue(result["L_G_separated"])
            self.assertTrue(result["L_C_indistinguishable"])
            self.assertFalse(result["topology_identified"])
            with self.assertRaises(FileExistsError):
                suite(a,root/"c")
            # SHA-only forgery: changed bit but repacked manifest SHA.
            bad = root/"fake-bit"
            shutil.copytree(a, bad)
            packet_file=bad/"L-linked"/"u2"/"b_packets.csv"
            with packet_file.open(newline="",encoding="utf-8") as fp:
                data=list(csv.DictReader(fp)); names=list(data[0])
            data[0]["moved"]="False"
            with packet_file.open("w",newline="",encoding="utf-8") as fp:
                w=csv.DictWriter(fp,fieldnames=names)
                w.writeheader(); w.writerows(data)
            mp=bad/"manifest.json"
            manifest=json.loads(mp.read_text(encoding="utf-8"))
            manifest["artifacts"]["L-linked/u2/b_packets.csv"]=hashlib.sha256(packet_file.read_bytes()).hexdigest()
            mp.write_text(json.dumps(manifest,sort_keys=True,indent=2)+"\n",encoding="utf-8")
            with self.assertRaises(AssertionError):
                verify_suite(bad,origin_snapshot())
            # Change frozen sensor threshold, rehash manifest, still reject.
            fake_cfg=root/"fake-config"
            shutil.copytree(a, fake_cfg)
            config_file=fake_cfg/"C-coforced"/"u1"/"config.json"
            cfg=json.loads(config_file.read_text(encoding="utf-8"))
            cfg["packet_threshold_m_s"]=.2
            config_file.write_text(json.dumps(cfg,sort_keys=True,indent=2)+"\n",encoding="utf-8")
            mp_cfg=fake_cfg/"manifest.json"
            manifest_cfg=json.loads(mp_cfg.read_text(encoding="utf-8"))
            manifest_cfg["artifacts"]["C-coforced/u1/config.json"]=hashlib.sha256(config_file.read_bytes()).hexdigest()
            mp_cfg.write_text(json.dumps(manifest_cfg,sort_keys=True,indent=2)+"\n",encoding="utf-8")
            with self.assertRaises(AssertionError):
                verify_suite(fake_cfg,origin_snapshot())
            # Science conclusion forgery with matching SHA cannot bypass oracle.
            fake=root/"fake-claim"
            shutil.copytree(a,fake)
            comp=fake/"comparison.json"
            data=json.loads(comp.read_text(encoding="utf-8"))
            data["topology_identified"]=True
            comp.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n",encoding="utf-8")
            mp=fake/"manifest.json"
            manifest=json.loads(mp.read_text(encoding="utf-8"))
            manifest["artifacts"]["comparison.json"]=hashlib.sha256(comp.read_bytes()).hexdigest()
            mp.write_text(json.dumps(manifest,sort_keys=True,indent=2)+"\n",encoding="utf-8")
            with self.assertRaises(AssertionError):
                verify_suite(fake,origin_snapshot())

    def test_two_destination_publication_fails_closed(self):
        from experiments.F014.run_suite import publish_dir as publish_real
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            a,b=root/"raw",root/"replay"
            preserved=root/"keep.txt"
            preserved.write_text("preserve",encoding="utf-8")
            calls=[]
            def fail_second(src,dst):
                calls.append(dst)
                if len(calls)==2:
                    raise OSError("injected second publish failure")
                return publish_real(src,dst)
            with patch("experiments.F014.run_suite.publish_dir",side_effect=fail_second):
                with self.assertRaisesRegex(OSError, "injected second"):
                    suite(a,b)
            self.assertFalse(a.exists())
            self.assertFalse(b.exists())
            self.assertEqual(preserved.read_text(encoding="utf-8"),"preserve")
            with self.assertRaises(ValueError):
                suite(root/"nested",root/"nested"/"replay")


if __name__ == "__main__":
    unittest.main()
