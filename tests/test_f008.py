"""F008 frozen controls, A-local information boundary and adversarial evidence tests."""
from __future__ import annotations

import csv
from dataclasses import fields, replace
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from soma.f007 import Config, simulate
from soma.f008 import COLUMNS, LocalObservation, analyze, detect, project_local
from experiments.F008.run_suite import CASES, compare_bytes, configuration, suite
from experiments.F008.verify import verify_suite


class F008Tests(unittest.TestCase):
    def test_frozen_physics_controls_and_confounded_local_trace(self):
        traces = {}
        expected = {
            "A-free": [2.,2.,2.,2.],
            "B-linked": [1.,1.,1.,1.],
            "C-cut": [1.,1.,2.,2.],
            "D-hidden-force": [1.,1.,1.,1.],
            "E-empty-battery": [0.,0.,0.,0.],
        }
        for case in CASES:
            with self.subTest(case=case):
                rows,_,_,_=simulate(Config.from_dict(configuration(case)))
                local = analyze(rows)
                self.assertEqual(len(local),4)
                self.assertEqual([r["observed_accel_m_s2"] for r in local],expected[case])
                self.assertEqual([r["status"] for r in local],
                    (["not_excited"]*4 if case=="E-empty-battery" else
                     ["anomaly","anomaly","nominal","nominal"] if case=="C-cut" else
                     ["nominal"]*4 if case=="A-free" else ["anomaly"]*4))
                traces[case] = local
        self.assertEqual(traces["B-linked"],traces["D-hidden-force"])

    def test_world_truth_is_never_given_to_detector(self):
        rows,_,_,_=simulate(Config.from_dict(configuration("B-linked")))
        allowed = {f.name for f in fields(LocalObservation)}
        self.assertEqual(allowed,{
            "step_index","time_s","dt_s","v_prev_m_s","v_a_m_s",
            "motor_command_n","motor_applied_n","balance_a_uj"})
        obs = project_local(rows[0], rows[1])
        self.assertEqual(set(detect(obs)),set(COLUMNS))
        for secret in ("attached","x_a_m","x_b_m","v_b_m_s","external_force_a_n",
                       "link_force_a_n","link_force_b_n","decision_reason"):
            self.assertNotIn(secret,allowed)
            self.assertNotIn(secret,detect(obs))
        spoofed = [dict(r,attached=not r["attached"],v_b_m_s=1e6,
                        external_force_a_n=1000.,link_force_b_n=1e9)
                   for r in rows]
        self.assertEqual(analyze(rows),analyze(spoofed))

    def test_off_motor_cannot_infer_mass_from_externally_driven_motion(self):
        rows,_,_,_=simulate(Config.from_dict(configuration("E-empty-battery")))
        data = analyze(rows)
        self.assertTrue(all(r["expected_accel_m_s2"] is None and
                            r["residual_m_s2"] is None for r in data))
        obs=project_local(rows[0],rows[1])
        self.assertEqual(detect(replace(obs,motor_applied_n=0,
                                        v_a_m_s=1.))["status"],"not_excited")

    def test_reject_nonfinite_and_invalid_local_observations(self):
        rows,_,_,_=simulate(Config.from_dict(configuration("A-free")))
        obs=project_local(rows[0],rows[1])
        for bad in (replace(obs,dt_s=0),replace(obs,v_a_m_s=float("nan")),
                    replace(obs,balance_a_uj=-1),replace(obs,step_index=True)):
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                detect(bad)
        with self.assertRaises(ValueError):
            detect(obs,nominal_mass_kg=0)
        with self.assertRaises(ValueError):
            project_local(rows[1],rows[1])

    def test_saved_independent_oracle_and_byte_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            from experiments.F008.run_suite import local_provenance
            identity=local_provenance()
            a,b=Path(tmp)/"one",Path(tmp)/"two"
            summary=suite(a,origin=identity)
            suite(b,origin=identity)
            self.assertEqual(summary["cases"],5)
            self.assertEqual(summary["observations"],20)
            self.assertTrue(summary["linked_external_indistinguishable"])
            self.assertGreaterEqual(compare_bytes(a,b),31)
            self.assertEqual(verify_suite(a,trusted_origin=identity)["observations"],20)

    def test_tampered_local_semantics_refused_even_after_rehash(self):
        with tempfile.TemporaryDirectory() as tmp:
            from experiments.F008.run_suite import local_provenance
            identity=local_provenance()
            path=Path(tmp)/"out"
            suite(path,origin=identity)
            local=path/"B-linked"/"local.csv"
            with local.open(encoding="utf-8",newline="") as fp:
                reader=csv.DictReader(fp)
                columns=reader.fieldnames
                rows=list(reader)
            rows[0]["residual_m_s2"]="0.0"
            with local.open("w",encoding="utf-8",newline="") as fp:
                writer=csv.DictWriter(fp,fieldnames=columns)
                writer.writeheader()
                writer.writerows(rows)
            manifest=path/"manifest.json"
            obj=json.loads(manifest.read_text(encoding="utf-8"))
            obj["artifacts"]["B-linked/local.csv"]=hashlib.sha256(local.read_bytes()).hexdigest()
            manifest.write_text(json.dumps(obj,sort_keys=True),encoding="utf-8")
            with self.assertRaises(AssertionError):
                verify_suite(path,trusted_origin=identity)

    def test_world_source_tamper_rehashed_still_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            from experiments.F008.run_suite import local_provenance
            identity=local_provenance()
            path=Path(tmp)/"out"
            suite(path,origin=identity)
            original=path/"B-linked"/"F007"/"states.csv"
            original.write_text(original.read_text().replace("0.0625","0.0626",1),
                                encoding="utf-8")
            inner=path/"B-linked"/"F007"/"manifest.json"
            m=json.loads(inner.read_text(encoding="utf-8"))
            m["artifacts"]["states.csv"]=hashlib.sha256(original.read_bytes()).hexdigest()
            inner.write_text(json.dumps(m),encoding="utf-8")
            outer=path/"manifest.json"
            top=json.loads(outer.read_text(encoding="utf-8"))
            for name in ("B-linked/F007/states.csv","B-linked/F007/manifest.json"):
                top["artifacts"][name]=hashlib.sha256((path/name).read_bytes()).hexdigest()
            outer.write_text(json.dumps(top),encoding="utf-8")
            with self.assertRaises(AssertionError):
                verify_suite(path,trusted_origin=identity)

    def test_f008_dependency_provenance_is_checked(self):
        from experiments.F008.run_suite import local_provenance
        from experiments.F008.verify import F008_SOURCE_FILES
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "out"
            trusted = local_provenance()
            suite(root, origin=trusted)
            self.assertEqual(set(trusted["f008_source_hashes"]), set(F008_SOURCE_FILES))
            forged = dict(trusted)
            forged["f008_source_hashes"] = dict(trusted["f008_source_hashes"])
            forged["f008_source_hashes"]["soma/f008.py"] = "0" * 64
            # Even when caller and evidence agree on a *forged* origin,
            # the independently recomputed checkout hashes must reject it.
            obj=json.loads((root/"manifest.json").read_text(encoding="utf-8"))
            obj["origin"] = forged
            (root/"manifest.json").write_text(json.dumps(obj), encoding="utf-8")
            with self.assertRaises(AssertionError):
                verify_suite(root, trusted_origin=forged)

    def test_rehashed_scientific_summary_and_manifest_claims_are_rejected(self):
        from experiments.F008.run_suite import local_provenance
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)/"out"
            identity = local_provenance()
            suite(root, origin=identity)
            mp = root/"manifest.json"
            cp = root/"comparison.json"
            original_manifest = mp.read_bytes()
            original_comparison = cp.read_bytes()

            # A self-consistent SHA is not a validation of a scientific claim.
            comparison = json.loads(original_comparison)
            comparison["confound_cannot_prove_attachment"] = False
            cp.write_text(json.dumps(comparison, sort_keys=True), encoding="utf-8")
            manifest = json.loads(original_manifest)
            manifest["artifacts"]["comparison.json"] = hashlib.sha256(cp.read_bytes()).hexdigest()
            mp.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")
            with self.assertRaises(AssertionError):
                verify_suite(root, trusted_origin=identity)

            cp.write_bytes(original_comparison)
            for key, fake in (("cases", ["A-free"]), ("source", "unverified world model")):
                with self.subTest(manifest_key=key):
                    manifest = json.loads(original_manifest)
                    manifest[key] = fake
                    mp.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")
                    with self.assertRaises(AssertionError):
                        verify_suite(root, trusted_origin=identity)

    def test_pair_rejects_nested_paths_without_publication(self):
        from experiments.F008.run_suite import run_pair
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            for first, second in (
                    (parent/"test"/"nested", parent/"test"),
                    (parent/"test", parent/"test"/"nested")):
                with self.subTest(first=first, second=second):
                    with self.assertRaises(ValueError):
                        run_pair(first, second)
                    self.assertFalse((parent/"test").exists())

    def test_no_partial_publication_on_oracle_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/"out"
            with patch("experiments.F008.run_suite.verify_suite",
                       side_effect=AssertionError("injected")):
                with self.assertRaises(AssertionError):
                    suite(target,origin={})
            self.assertFalse(target.exists())
            self.assertFalse(list(Path(tmp).glob(".out-stage-*")))


if __name__ == "__main__":
    unittest.main()
