"""F018 producer / independent raw-data oracle / deterministic replay tests."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from experiments.F018.run_suite import ARTIFACTS, save_suite
from experiments.F018.verify import verify
from experiments.F018.analyze import analyze
from experiments.F018.attack_test import run_attacks
from soma.f018 import scenario_grid, simulate_world


class TestF018Evidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="f018-evidence-")
        cls.first = Path(cls.temp.name)/"first"
        cls.manifest = save_suite(cls.first)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_independent_oracle_and_all_630_lineages(self):
        audit = verify(self.first)
        self.assertTrue(audit["semantic_verified"])
        self.assertEqual(audit["worlds"],630)
        self.assertEqual(audit["scenarios"],90)
        self.assertEqual(self.manifest["primary_worlds"],360)
        self.assertEqual(self.manifest["outside_worlds"],270)

    def test_report_is_from_raw_evidence(self):
        result=analyze(self.first)
        self.assertEqual(sum(x["count"] for x in
                             result["by_resource_layout"].values()),90)
        self.assertEqual(result["example_dual_link"]["delta_outside_uj"],
                         {"A":1900000,"B":2900000})
        self.assertEqual(result["example_b_link"]["delta_fixed_uj"],
                         {"A":900000,"B":2900000})

    def test_semantic_attacks_with_all_hashes_rebuilt(self):
        result=run_attacks(self.first)
        self.assertEqual(result["rehashed_semantic_attacks_rejected"],
                         ["score","physics","ledger",
                          "state_initial_candidate","state_initial_work",
                          "state_reason","state_motor_index",
                          "state_zero_motor_candidate"])

    def test_second_exact_byte_replay(self):
        second=Path(self.temp.name)/"second"
        replay=save_suite(second)
        self.assertEqual(self.manifest,replay)
        for artifact in (*ARTIFACTS,"manifest.json"):
            self.assertEqual((self.first/artifact).read_bytes(),
                             (second/artifact).read_bytes())

    def test_posthoc_scene_rejected(self):
        item = scenario_grid()[0]
        forged = {**item,"terminal_radius_m":0.03}
        with self.assertRaises(ValueError):
            simulate_world(forged,"YY")


if __name__ == "__main__":
    unittest.main()
