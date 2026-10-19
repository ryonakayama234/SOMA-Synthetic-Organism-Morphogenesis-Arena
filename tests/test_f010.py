"""F010 numerical and information-boundary tests; frozen A-F preregistration."""
import unittest
from dataclasses import replace
from pathlib import Path
import tempfile
from unittest.mock import patch

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
        # Actual adopted F007 world dynamics -> adopted F008 strict projection.
        # Verify all LOCAL observations, including battery, not world truth.
        from soma.f008 import project_local
        for u in (2.,1.,.5):
            linked, _, _, _ = simulate(Config.from_dict(configuration("A-linked",u)))
            mimic, _, _, _ = simulate(Config.from_dict(configuration("C-adaptive",u)))
            lhs=tuple(project_local(p,q) for p,q in zip(linked,linked[1:]))
            rhs=tuple(project_local(p,q) for p,q in zip(mimic,mimic[1:]))
            self.assertEqual(lhs,rhs)
        self.assertFalse(estimate(tuple(make_trial(u,a) for u,a in
                        zip((2.,1.,.5),(1.,.5,.25))))["topology_verified"])

    def test_unexcited_and_non_distinct_are_inconclusive(self):
        no = tuple(make_trial(0.,0.,command=u) for u in (2.,1.,.5))
        self.assertEqual(estimate(no)["status"], "inconclusive")
        same = tuple(make_trial(2.,1.) for _ in range(3))
        self.assertEqual(estimate(same)["status"], "inconclusive")
        self.assertEqual(estimate((make_trial(2.,1.),))["status"],"inconclusive")

    def test_command_applied_mismatch_is_inconclusive(self):
        # Preregistered command/applied equality is separate from nonzero
        # and distinct applied forces: a consistent partial motor is invalid.
        levels = (2., 1., .5)
        expected_a = (1., .5, .25)
        mismatched = tuple(make_trial(u, a, command=u + 1.)
                           for u, a in zip(levels, expected_a))
        outcome = estimate(mismatched)
        self.assertEqual(outcome["status"], "inconclusive")
        self.assertEqual(outcome["reason"], "rejected_or_unstable_applied_excitation")
        self.assertIsNone(outcome["alpha_per_kg"])
        # A single rejected step within an otherwise valid three-probe suite
        # must also make the result inconclusive, not an affine fit.
        trials = tuple(make_trial(u, a) for u, a in zip(levels, expected_a))
        bad = list(trials[0])
        bad[2] = replace(bad[2], motor_command_n=3.)
        self.assertEqual(
            estimate((tuple(bad), *trials[1:]))["status"], "inconclusive"
        )

    def test_third_force_is_independent_holdout(self):
        trials=(make_trial(2.,1.),make_trial(1.,.5),make_trial(.5,.75))
        x=estimate(trials)
        self.assertEqual(x["status"], "non_affine_holdout")
        self.assertFalse(x["topology_verified"])

    def test_world_field_rejected_and_time_checked(self):
        row=make_trial(2.,1.)
        with self.assertRaises(ValueError):
            estimate(((({"attached":True},)+row[1:]),)*3)
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


    def test_rehashed_local_and_science_claim_forgery_rejected(self):
        import csv
        import hashlib
        import json
        import shutil
        from experiments.F010.verify import verify_suite
        from experiments.F010.run_suite import origin_snapshot
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            a,b=root/"raw",root/"replay"
            suite(a,b)
            trusted=origin_snapshot()
            verify_suite(a,trusted)
            # Forge a numerical A-local row and repack outer SHA.
            fake=root/"fake-local"
            shutil.copytree(a,fake)
            target=fake/"A-linked"/"u2"/"local.csv"
            with target.open(newline="",encoding="utf-8") as fp:
                data=list(csv.DictReader(fp))
                cols=list(data[0])
            data[0]["observed_accel_m_s2"]="1.25"
            with target.open("w",newline="",encoding="utf-8") as fp:
                writer=csv.DictWriter(fp,fieldnames=cols)
                writer.writeheader()
                writer.writerows(data)
            manifest=fake/"manifest.json"
            m=json.loads(manifest.read_text(encoding="utf-8"))
            m["artifacts"]["A-linked/u2/local.csv"]=hashlib.sha256(target.read_bytes()).hexdigest()
            manifest.write_text(json.dumps(m,sort_keys=True,indent=2)+"\n",encoding="utf-8")
            with self.assertRaises(AssertionError):
                verify_suite(fake,trusted)
            # Forge the scientific conclusion with fresh matching hash.
            fake2=root/"fake-claim"
            shutil.copytree(a,fake2)
            cmpfile=fake2/"comparison.json"
            comparison=json.loads(cmpfile.read_text(encoding="utf-8"))
            comparison["signatures"]["C-adaptive"]["topology_verified"]=True
            cmpfile.write_text(json.dumps(comparison,sort_keys=True,indent=2)+"\n",encoding="utf-8")
            manifest2=fake2/"manifest.json"
            m2=json.loads(manifest2.read_text(encoding="utf-8"))
            m2["artifacts"]["comparison.json"]=hashlib.sha256(cmpfile.read_bytes()).hexdigest()
            manifest2.write_text(json.dumps(m2,sort_keys=True,indent=2)+"\n",encoding="utf-8")
            with self.assertRaises(AssertionError):
                verify_suite(fake2,trusted)

    def test_replay_publication_failure_rolls_back_first(self):
        from experiments.F010.run_suite import publish_dir as real_publish
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker = root / "preserve.txt"
            marker.write_text("preserve", encoding="utf-8")
            a, b = root / "raw", root / "replay"
            calls = []

            def fail_second(source, destination):
                calls.append(destination)
                if len(calls) == 2:
                    raise OSError("injected replay publication failure")
                return real_publish(source, destination)

            with patch("experiments.F010.run_suite.publish_dir", side_effect=fail_second):
                with self.assertRaisesRegex(OSError, "injected replay"):
                    suite(a, b)
            self.assertEqual(calls, [a, b])
            self.assertFalse(a.exists())
            self.assertFalse(b.exists())
            self.assertEqual([p.name for p in root.iterdir()], ["preserve.txt"])
            self.assertEqual(marker.read_text(encoding="utf-8"), "preserve")
            result = suite(a, b)
            self.assertTrue(result["byte_replay"])
            self.assertTrue(a.is_dir() and b.is_dir())

    def test_overlap_rejection_preserves_existing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"existing").mkdir()
            marker=root/"existing"/"keep.txt"
            marker.write_text("do not replace",encoding="utf-8")
            with self.assertRaises((ValueError,FileExistsError)):
                suite(root/"existing",root/"next")
            with self.assertRaises(ValueError):
                suite(root/"new",root/"new"/"inside")
            self.assertEqual(marker.read_text(encoding="utf-8"),"do not replace")


if __name__ == "__main__":
    unittest.main()
