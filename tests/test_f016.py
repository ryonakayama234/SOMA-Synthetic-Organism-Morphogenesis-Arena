"""F016 regression, negative controls, per-case evidence and byte replay."""
import hashlib
import json
import tempfile
from pathlib import Path
import unittest

from soma.f016 import (ResourceBit, choose_force, read_b_local, run_episode,
                        GROUPS, EXPECTED_MEAN_NET_UJ)
from experiments.F016.run_suite import suite
from experiments.F016.verify import verify_suite


def rewrite_and_rehash(root: Path, filename: str, payload: dict) -> None:
    file = root / filename
    file.write_text(json.dumps(payload, sort_keys=True, indent=2)+"\n", encoding="utf-8")
    manifest_file = root / "manifest.json"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    manifest["artifacts"][filename] = hashlib.sha256(file.read_bytes()).hexdigest()
    manifest_file.write_text(json.dumps(manifest, sort_keys=True, indent=2)+"\n",
                             encoding="utf-8")


class F016Tests(unittest.TestCase):
    def test_frozen_balanced_action_value(self):
        for group in GROUPS:
            records = [run_episode(group, i) for i in range(4)]
            self.assertEqual(sum(x["net_uj"] for x in records)//4,
                             EXPECTED_MEAN_NET_UJ[group])
            self.assertTrue(all(x["motor_spent_uj"] == 1_000_000 for x in records))
            self.assertTrue(all(x["ledger_residual_uj"] == 0 for x in records))
            self.assertEqual([r["reached"] for r in records],
                             {"A0":[True,False,True,False],
                              "K":[True,False,True,False],
                              "S":[True,False,False,True],
                              "T":[True,True,True,True],
                              "H":[True,True,True,True],
                              "I":[False,False,False,False]}[group])

    def test_local_only_interface_and_forgery(self):
        self.assertEqual(choose_force(None), 2.0)
        self.assertEqual(choose_force(ResourceBit("B",0,0.0,False)), -2.0)
        self.assertTrue(read_b_local(.625,.1))
        self.assertFalse(read_b_local(-.625,.1))
        for value in (
            ResourceBit("world",0,0.0,True),
            ResourceBit("B",1,0.0,True),
            ResourceBit("B",0,.25,True),
            ResourceBit("B",0,0.0,1),
            ResourceBit("B",True,0.0,True),
            {"resource_right":True,"resource_x":.625},
        ):
            with self.assertRaises(ValueError):
                choose_force(value)

    def test_sender_insufficient_balance_drops_packet_no_phantom_spend(self):
        item = run_episode("T",0,b_initial_uj=0)
        self.assertIsNone(item["packet"])
        self.assertEqual(item["communication_spent_uj"],0)
        self.assertEqual(item["balance_b_uj"],0)
        self.assertEqual(item["motor_command_n"],2.0)
        self.assertTrue(item["reached"])
        # For the opposite target this default is causally worse.
        other = run_episode("T",1,b_initial_uj=0)
        self.assertFalse(other["reached"])
        self.assertEqual(other["net_uj"],-1_000_000)

    def test_fresh_evidence_and_byte_identical_replay(self):
        with tempfile.TemporaryDirectory() as work:
            r1, r2 = Path(work)/"r1", Path(work)/"r2"
            result = suite(r1)
            self.assertEqual(result["number_of_primary_runs"],24)
            self.assertEqual(verify_suite(r1)["cases"],24)
            suite(r2)
            a = {p.relative_to(r1): p.read_bytes() for p in r1.rglob("*") if p.is_file()}
            b = {p.relative_to(r2): p.read_bytes() for p in r2.rglob("*") if p.is_file()}
            self.assertEqual(a,b)
            with self.assertRaises(FileExistsError):
                suite(r1)

    def test_rehashed_false_science_fails_independent_oracle(self):
        with tempfile.TemporaryDirectory() as work:
            root = Path(work)/"evidence"
            suite(root)
            data = json.loads((root/"T_0.json").read_text())
            data["net_uj"] += 1_000_000
            rewrite_and_rehash(root,"T_0.json",data)
            with self.assertRaisesRegex(ValueError,"independent task/net result"):
                verify_suite(root)

    def test_rehashed_position_or_packet_forgery_fails(self):
        for changed in ("x", "bit"):
            with self.subTest(changed=changed), tempfile.TemporaryDirectory() as work:
                root = Path(work)/"evidence"
                suite(root)
                data = json.loads((root/"T_1.json").read_text())
                if changed == "x":
                    data["states"][4]["x_a_m"] += .25
                else:
                    data["packet"]["resource_right"] = True
                rewrite_and_rehash(root,"T_1.json",data)
                with self.assertRaises(ValueError):
                    verify_suite(root)


if __name__ == "__main__":
    unittest.main()
