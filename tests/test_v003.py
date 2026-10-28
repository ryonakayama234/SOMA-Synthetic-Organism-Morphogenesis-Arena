"""V003 frozen-contract preflight tests. Real source-bound CI is separate."""
import hashlib
import inspect
import json
import math
import tempfile
import unittest
from pathlib import Path

from experiments.V003.run_suite import frozen_request, export_requests, accept_request
from experiments.V003.verify import (YS,DIGESTS,ORIGINAL_SHA,F022_FREEZE,
                                    physics,schema,read,hash_file,ORIGINAL_HASHES)

class FrozenV003(unittest.TestCase):
    def test_all_eleven_request_bytes_and_provenance(self):
        self.assertEqual(len(YS),11)
        self.assertEqual(len(set(DIGESTS.values())),11)
        for y in YS:
            with self.subTest(y=y):
                r=frozen_request(y)
                self.assertEqual(r["fork_id"],"V003-Y"+y.replace(".",""))
                self.assertEqual(r["expected_source_commit_sha"],ORIGINAL_SHA)
                self.assertEqual(r["expected_frozen_protocol_sha"],F022_FREEZE)
                self.assertEqual(hashlib.sha256(
                    (json.dumps(r,sort_keys=True,separators=(",",":"),allow_nan=False)+"\n").encode()
                ).hexdigest(),DIGESTS[y])
    def test_export_without_simulation_and_strict_input(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/"requests"
            self.assertEqual(export_requests(root),11)
            self.assertEqual(len(list(root.glob("*.json"))),11)
            for f in root.glob("*.json"):
                self.assertEqual(accept_request(f),read(f))
            with self.assertRaises(FileExistsError): export_requests(root)
            f=root/"V003-Y095.json"
            obj=read(f)
            obj["candidate_y_b_decimal"]="1.05"
            f.write_text(json.dumps(obj)+"\n")
            with self.assertRaises(Exception): accept_request(f)
    def test_fixed_analytic_contact_boundary_and_A_influence(self):
        original=dict(world_id="C05",x_a_m=-1.,y_a_m=0.,vx_a_mps=1.,vy_a_mps=0.,
                      x_b_m=1.,y_b_m=1.01,vx_b_mps=-1.,vy_b_mps=0.,
                      mass_a_kg=1.,mass_b_kg=1.,radius_a_m=.5,radius_b_m=.5,
                      restitution=1.,duration_s=2.,sample_dt_s=.25)
        impulses=graze=miss=0
        for y in YS:
            scene,frames,events=physics(original,y)
            self.assertEqual(scene["y_b_m"],float(y))
            self.assertEqual(len(frames),9)
            self.assertEqual([v["time_s"] for v in frames],[k/4 for k in range(9)])
            self.assertTrue(all(abs(f["total_ke_j"]-1.)<1e-9 for f in frames))
            if float(y)<1.:
                impulses+=1
                self.assertEqual(len(events),1)
                self.assertEqual(events[0]["kind"],"impulse")
                s=math.sqrt(1.-float(y)**2)
                self.assertAlmostEqual(events[0]["impulse_ns"],2*s)
                self.assertAlmostEqual(events[0]["time_s"],1.-s/2.)
                self.assertAlmostEqual(math.hypot(frames[-1]["vx_a_mps"]-1.,
                                                  frames[-1]["vy_a_mps"]),2*s)
            elif y=="1.00":
                graze+=1
                self.assertEqual(events[0]["kind"],"grazing_zero_impulse")
                self.assertEqual(events[0]["impulse_ns"],0.)
                self.assertEqual(frames[-1]["vx_a_mps"],1.)
            else:
                miss+=1
                self.assertEqual(events,[])
                self.assertEqual(frames[-1]["vx_a_mps"],1.)
        self.assertEqual((impulses,graze,miss),(5,1,5))
    def test_contract_rejects_cross_field_fork_provenance(self):
        import jsonschema
        contract=json.loads((Path(__file__).resolve().parents[1]/
                             "contracts/v003.derived.v1.schema.json").read_text())
        cases=contract["oneOf"]
        self.assertEqual(len(cases),11)
        for i,y in enumerate(YS):
            for j,other in enumerate(YS):
                id_value="V003-Y"+y.replace(".","")
                matches=sum(1 for c in cases
                            if c["properties"]["fork_id"]["const"]==id_value
                            and c["properties"]["scenario"]["properties"]["y_b_m"]["const"]==float(y)
                            and c["properties"]["request"]["properties"]["candidate_y_b_decimal"]["const"]==other)
                self.assertEqual(matches,1 if i==j else 0)
    def test_verifier_has_no_F022_producer_import(self):
        import experiments.V003.verify as v
        source=inspect.getsource(v)
        self.assertNotIn("from soma.f022 import",source)
        self.assertNotIn("from experiments.V003.run_suite import",source)
        self.assertEqual(ORIGINAL_HASHES["manifest.json"],
                         "f0d5d9fd4e1d126b0f0e0f77fb5e796b7b3a0860118891c10c70d919e05fadc0")

if __name__=="__main__": unittest.main()
