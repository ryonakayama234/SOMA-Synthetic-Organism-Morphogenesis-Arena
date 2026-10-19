"""F010 numerical and information-boundary tests; frozen A-F preregistration."""
import unittest
from dataclasses import replace
from pathlib import Path
import tempfile

from soma.f008 import LocalObservation
from soma.f010 import estimate
from experiments.F010.run_suite import configuration, suite, cases
from soma.f007 import Config, simulate


def make_trial(force, accel, *, command=None):
    return tuple(LocalObservation(k, k*.25, .25, (k-1)*.25*accel, k*.25*accel,
                                  force if command is None else command,
                                  force, 3_000_000) for k in range(1, 5))


class F010Tests(unittest.TestCase):
    def test_frozen_hypotheses(self):
        for tag, a, alpha, beta, sig in (
            ("A-linked", (1., .5, .25), .5, 0., "inertia_like"),
            ("B-constant", (1., 0., -.5), 1., -1., "offset_like"),
            ("C-adaptive", (1., .5, .25), .5, 0., "inertia_like"),
            ("D-free", (2., 1., .5), 1., 0., "nominal_like"),
        ):
            with self.subTest(tag=tag):
                result = estimate(tuple(make_trial(u, v) for u,v in zip((2.,1.,.5),a)))
                self.assertEqual(result["status"], "affine_response_fit")
                self.assertEqual((result["alpha_per_kg"],result["beta_m_s2"]), (alpha,beta))
                self.assertEqual(result["response_signature"], sig)
                self.assertFalse(result["topology_verified"])

    def test_confound_is_identical_to_linked(self):
        x = tuple(make_trial(u,a) for u,a in zip((2.,1.,.5),(1.,.5,.25)))
        self.assertEqual(estimate(x),estimate(x))  # no topology input/API
        self.assertFalse(estimate(x)["topology_verified"])

    def test_unexcited_and_non_distinct_are_inconclusive(self):
        no = tuple(make_trial(0.,0.,command=u) for u in (2.,1.,.5))
        self.assertEqual(estimate(no)["status"], "inconclusive")
        same = tuple(make_trial(2.,1.) for _ in range(3))
        self.assertEqual(estimate(same)["status"], "inconclusive")
        self.assertEqual(estimate((make_trial(2.,1.),))["status"],"inconclusive")

    def test_third_force_is_independent_holdout(self):
        trials=(make_trial(2.,1.),make_trial(1.,.5),make_trial(.5,.75))
        x=estimate(trials)
        self.assertEqual(x["status"], "non_affine_holdout")
        self.assertFalse(x["topology_verified"])

    def test_world_field_rejected_and_time_checked(self):
        row=make_trial(2.,1.)
        with self.assertRaises(ValueError):
            estimate(((dict(row[0].__dict__) if hasattr(row[0],"__dict__") else {"attached":True},)+row[1:],)*3)
        with self.assertRaises(ValueError):
            estimate((row[:2]+row[:2],row,row))
        with self.assertRaises(ValueError):
            estimate(((replace(row[0],time_s=.3),)+row[1:],row,row))

    def test_f007_configs_without_modification(self):
        for group in ("A-linked","B-constant","C-adaptive","D-free","E-empty"):
            for force in (2.,1.,.5):
                cfg=Config.from_dict(configuration(group,force))
                self.assertEqual(cfg.steps,4)
                states, _, _, _=simulate(cfg)
                self.assertEqual(len(states),5)

    def test_suite_reproduction_and_tamper(self):
        with tempfile.TemporaryDirectory() as tmp:
            a,b=Path(tmp)/"a",Path(tmp)/"b"
            result=suite(a,b)
            self.assertEqual(result["cases"],15)
            self.assertTrue(result["byte_replay"])
            self.assertTrue(a.exists() and b.exists())
            with self.assertRaises(FileExistsError):
                suite(a,Path(tmp)/"c")
            from experiments.F010.verify import verify_suite
            from experiments.F010.run_suite import origin_snapshot
            (a/"A-linked"/"u2"/"local.csv").write_text("tampered",encoding="utf-8")
            with self.assertRaises((ValueError,AssertionError)):
                verify_suite(a,origin_snapshot())


if __name__ == "__main__":
    unittest.main()
