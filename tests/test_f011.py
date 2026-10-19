"""F011 model, scientific controls, evidence and forgery negatives."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from soma.f011 import Config, CASES, DTS, StrokeLimitError, simulate
from experiments.F011.run_suite import run_pair
from experiments.F011.verify import verify_suite

class F011Tests(unittest.TestCase):
    def test_only_preregistered_configs(self):
        for case,h in [('unknown',.01),('A-no-contact',.1),('A-no-contact',True)]:
            with self.assertRaises(ValueError):Config(case,h)

    def test_no_contact_stroke_negative_preserved_not_silent(self):
        for h in DTS:
            with self.assertRaises(StrokeLimitError) as cm:
                simulate(Config('A-no-contact',h))
            err=cm.exception
            self.assertEqual(err.step,len(err.valid_rows))
            self.assertGreater(err.step,100)
            self.assertGreater(err.attempted_r,.8)
            for row in err.valid_rows:
                self.assertLess(abs(row['x_cm_m']),1e-10)
                self.assertLess(abs(row['v_a_m_s']+row['v_b_m_s']),1e-10)

    def test_symmetric_mirror_and_ground_passivity(self):
        for h in DTS:
            iso=simulate(Config('B-isotropic',h))
            plus=simulate(Config('C-directional',h))
            minus=simulate(Config('D-mirror',h))
            quiet=simulate(Config('E-no-motor',h))
            for rows in (iso,quiet):
                self.assertTrue(all(abs(row['x_cm_m'])<1e-10 for row in rows))
            for left,right in zip(plus,minus):
                self.assertAlmostEqual(left['x_cm_m'],-right['x_cm_m'],delta=1e-9)
                self.assertAlmostEqual(left['r_m'],right['r_m'],delta=1e-9)
            for rows in (iso,plus,minus,quiet):
                self.assertTrue(all(z['ground_work_j']<=1e-11 for z in rows[1:]))
                self.assertTrue(all(abs(z['energy_defect_j']-z['expected_defect_j'])<1e-9 for z in rows[1:]))

    def test_saved_evidence_replay_and_hash_forgery(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'run';q=Path(t)/'replay'
            result=run_pair(p,q)
            self.assertTrue(result['result']['persistent_directional_model_drift'])
            self.assertGreaterEqual(result['byte_identical_files'],32)
            self.assertEqual(verify_suite(p)['verified_cases'],15)
            with self.assertRaises(ValueError):run_pair(p,Path(t)/'another')
            raw=p/'C-directional'/'0.0025'/'states.csv'
            before=raw.read_bytes()
            raw.write_bytes(before.replace(b'0.0025',b'0.0026',1))
            with self.assertRaises(ValueError):verify_suite(p)
            raw.write_bytes(before)
            self.assertEqual(verify_suite(p)['verified_cases'],15)
            # Recomputed manifest SHA must NOT authenticate forged science claim.
            summary=p/'comparison.json'
            original=summary.read_bytes()
            forged=json.loads(original.decode())
            forged['persistent_directional_model_drift']=False
            summary.write_text(json.dumps(forged,sort_keys=True)+'\n')
            manpath=p/'manifest.json'
            manifest=json.loads(manpath.read_text())
            manifest['files']['comparison.json']=hashlib.sha256(summary.read_bytes()).hexdigest()
            manpath.write_text(json.dumps(manifest,sort_keys=True)+'\n')
            with self.assertRaises(ValueError):verify_suite(p)
            # A recomputed manifest must not permit forgery of a primary
            # measured displacement while leaving the summary status intact.
            summary.write_bytes(original)
            manifest['files']['comparison.json']=hashlib.sha256(original).hexdigest()
            manpath.write_text(json.dumps(manifest,sort_keys=True)+'\n')
            self.assertEqual(verify_suite(p)['verified_cases'],15)
            metric_forgery=json.loads(original.decode())
            metric_forgery['results']['C-directional']['0.0025']['last_period_m']+=0.125
            summary.write_text(json.dumps(metric_forgery,sort_keys=True)+'\n')
            manifest['files']['comparison.json']=hashlib.sha256(summary.read_bytes()).hexdigest()
            manpath.write_text(json.dumps(manifest,sort_keys=True)+'\n')
            with self.assertRaises(ValueError):verify_suite(p)

    def test_do_not_overwrite_existing_evidence(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'existing';p.mkdir()
            (p/'keep').write_text('do not replace')
            with self.assertRaises(ValueError):run_pair(p,Path(t)/'other')
            self.assertEqual((p/'keep').read_text(),'do not replace')

if __name__=='__main__':unittest.main()
