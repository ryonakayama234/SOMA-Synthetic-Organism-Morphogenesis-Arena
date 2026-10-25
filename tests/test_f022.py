"""Preregistered F022 analytic, invalid-state, archive and integrity controls."""
import json
from pathlib import Path
import tempfile
import unittest

from soma.f022 import FREEZE_COMMIT, grid, simulate, validate, _toi
from experiments.F022.run_suite import produce
from experiments.F022.verify import verify
from experiments.F022.attack_test import attack

SOURCE = 'a' * 40


class FrozenF022(unittest.TestCase):
    def test_exact_roster_and_nine_samples(self):
        cases=grid()
        self.assertEqual([s['world_id'] for s in cases], [f'C{i:02d}' for i in range(1,14)])
        self.assertEqual(FREEZE_COMMIT,'3984e9dcb2cb420abab5ca92b4d029b31b5173f8')
        self.assertTrue(all(len(simulate(s)[0])==9 for s in cases))

    def test_fixed_collision_kinds_and_time(self):
        events={s['world_id']:simulate(s)[1] for s in grid()}
        self.assertEqual(len([a for a in events.values() if a]),10)
        for i, t in [(1,.5),(2,.5),(3,.6),(4,.6),(7,1.),(13,.095)]:
            self.assertAlmostEqual(events[f'C{i:02d}'][0]['time_s'],t)
        self.assertTrue(all(not events[f'C{i:02d}'] for i in (5,8,9)))
        self.assertEqual(events['C07'][0]['kind'],'grazing_zero_impulse')
        self.assertEqual(events['C07'][0]['impulse_ns'],0.)
        self.assertGreater(events['C06'][0]['impulse_ns'],0.)

    def test_oblique_rational_wolfram_reference(self):
        cases=grid()
        _,e=simulate(cases[2]);x=e[0]
        self.assertAlmostEqual(x['normal_x'],4/5)
        self.assertAlmostEqual(x['normal_y'],3/5)
        self.assertAlmostEqual(x['impulse_ns'],8/5)
        self.assertAlmostEqual(x['post_vx_a_mps'],-7/25)
        self.assertAlmostEqual(x['post_vy_a_mps'],-24/25)
        states,e=simulate(cases[3]);y=e[0]
        self.assertAlmostEqual(y['impulse_ns'],6/5)
        self.assertAlmostEqual(y['post_vx_a_mps'],1/25)
        self.assertAlmostEqual(y['post_vy_b_mps'],18/25)
        self.assertAlmostEqual(states[-1]['total_ke_j'],13/25)

    def test_invalid_inputs_are_rejected(self):
        x=grid()[0]
        alterations=[{'x_a_m':-.2,'x_b_m':.2},
                     {'x_a_m':0.,'x_b_m':0.},
                     {'x_a_m':float('nan')},
                     {'mass_a_kg':-1.},
                     {'x_a_m':-.5,'x_b_m':.5},
                     {'duration_s':5.},
                     {'restitution':1.1}]
        for d in alterations:
            with self.subTest(d=d),self.assertRaises(ValueError):validate(dict(x,**d))

    def test_fail_closed_ambiguous_discriminant(self):
        # Very small *nonzero* positive or negative discriminant.
        with self.assertRaisesRegex(ValueError,'ambiguous_geometry'):
            _toi((-1.,0.),(1.,1.-1e-13),(1.,0.),(-1.,0.))

    def test_archive_oracle_attacks_replay(self):
        with tempfile.TemporaryDirectory(prefix='f022-test-') as tmp:
            a=Path(tmp)/'a';b=Path(tmp)/'b'
            report=produce(a,source_sha=SOURCE)
            self.assertEqual(report['sample_count'],117)
            self.assertEqual(verify(a,expected_source_sha=SOURCE)['worlds'],13)
            self.assertEqual(attack(a)['rehash_semantic_attacks_rejected'],8)
            produce(b,source_sha=SOURCE)
            self.assertEqual({x.name:x.read_bytes() for x in a.iterdir()},
                             {x.name:x.read_bytes() for x in b.iterdir()})
            with self.assertRaises(FileExistsError):produce(a,source_sha=SOURCE)
            with self.assertRaises(AssertionError):verify(a,expected_source_sha='b'*40)
            self.assertEqual(json.loads((a/'scenario.json').read_text())['schema_version'],
                             'f022.archive.v1')


if __name__=='__main__':
    unittest.main()
