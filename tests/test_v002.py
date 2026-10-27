"""Initial V002 exact archive projection regression; no UI acceptance implied."""
from pathlib import Path
import importlib.util
import tempfile
import unittest

from experiments.F022.run_suite import produce as f022_produce
from experiments.F023.run_suite import produce as f023_produce
from experiments.V002.project import project, publish, canonical


@unittest.skipUnless(importlib.util.find_spec('jsonschema'), 'V002 schema validator not installed in inherited workflow')
class ProjectionSmokeTest(unittest.TestCase):
    SHA = "a" * 40

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def build(self, name, producer):
        path = self.root / name
        producer(path, source_sha=self.SHA)
        return path

    def project_pair(self, source, left, right):
        return project(source, source, left, right, expected_left_sha=self.SHA,
                       expected_right_sha=self.SHA,
                       trusted_left_anchor="test-checkout",
                       trusted_right_anchor="test-checkout")

    def test_f022_near_miss_and_graze(self):
        src = self.build("f022", f022_produce)
        near = self.project_pair(src, "C05", "C06")
        self.assertEqual([len(x["contacts"]) for x in near["worlds"]], [0, 1])
        self.assertEqual(near["worlds"][0]["cell_model"], {"kind": "not_modeled"})
        self.assertEqual(len(near["joint_sample_times_s"]), 9)
        self.assertEqual(near["pair_inference"], "single_field")
        offgrid = self.project_pair(src, "C13", "C01")
        t = offgrid["worlds"][0]["contacts"][0]["record"]["time_s"]
        self.assertAlmostEqual(t, .095)
        self.assertNotIn(t, offgrid["joint_sample_times_s"])

    def test_f023_private_ledgers_and_funding(self):
        src = self.build("f023", f023_produce)
        view = self.project_pair(src, "Q02", "Q04")
        self.assertEqual(view["worlds"][0]["cell_model"]["kind"], "f023_private")
        self.assertEqual(len(view["worlds"][0]["cell_model"]["actions"]), 2)
        self.assertEqual([len(x["contacts"]) for x in view["worlds"]], [1, 0])
        self.assertEqual(view["pair_inference"], "single_field")

    def test_invalid_trust_and_immutable_output(self):
        src = self.build("f022", f022_produce)
        with self.assertRaises(AssertionError):
            project(src, src, "C01", "C02", expected_left_sha="b"*40,
                    expected_right_sha=self.SHA,
                    trusted_left_anchor="external", trusted_right_anchor="external")
        view = self.project_pair(src, "C01", "C02")
        dest = self.root / "view"
        publish(dest, view, left_root=src, right_root=src,
                expected_left_sha=self.SHA, expected_right_sha=self.SHA,
                trusted_left_anchor="test-checkout", trusted_right_anchor="test-checkout")
        self.assertEqual((dest/"view.json").read_text(), canonical(view)+"\n")
        html = (dest/"index.html").read_text()
        self.assertIn("SOMA · V002 Counterfactual Observatory", html)
        self.assertIn("NO_RECORDED_SNAPSHOT_AT_TIME", html)
        self.assertIn("NOT MODELED", html)
        self.assertIn("Arena", html)
        from experiments.V002.verify_view import verify_view
        result = verify_view(dest/"view.json", src, src,
                             expected_left_sha=self.SHA, expected_right_sha=self.SHA,
                             trusted_left_anchor="test-checkout",
                             trusted_right_anchor="test-checkout")
        self.assertEqual(result["view_oracle"], "pass")
        import copy
        forged = copy.deepcopy(view)
        forged["worlds"][0]["samples"][0]["record"]["x_a_m"] += .1
        forged_dir = self.root/"forged-view"
        forged_dir.mkdir()
        (forged_dir/"view.json").write_text(canonical(forged)+"\n")
        with self.assertRaises(AssertionError):
            verify_view(forged_dir/"view.json", src, src,
                        expected_left_sha=self.SHA, expected_right_sha=self.SHA,
                        trusted_left_anchor="test-checkout",
                        trusted_right_anchor="test-checkout")
        with self.assertRaises(FileExistsError):
            publish(dest, view)


if __name__ == "__main__":
    unittest.main()
