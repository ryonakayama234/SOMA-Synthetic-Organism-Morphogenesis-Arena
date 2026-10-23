"""F020 archived record semantic adversarial tests (no producer import in verifier)."""
from __future__ import annotations

from copy import deepcopy
import unittest

from experiments.F020.verify import check_world, fail
from soma.f020 import calibration_scene, scene_for, simulate_world


class F020ArchiveTest(unittest.TestCase):
    def setUp(self):
        self.positive = simulate_world(calibration_scene(), "YY", "feedback")
        self.deferred = simulate_world(calibration_scene(), "YY", "deferred_credit")
        self.b_only = simulate_world(calibration_scene("b_only"), "YY", "feedback")

    def test_standalone_oracle_accepts_untampered(self):
        for world in (self.positive, self.deferred, self.b_only,
                      simulate_world(scene_for(1, -1, 5, .06, 250_000, 25_000),
                                     "NN", "deferred_credit")):
            check_world(world)

    def test_reject_semantic_forgeries_even_with_valid_rehashed_envelope(self):
        modifications = (
            (self.positive, lambda w: w["states"][2].__setitem__("x_a_m", .99)),
            (self.positive, lambda w: w["states"][1].__setitem__("balance_a_uj", 777)),
            (self.positive, lambda w: w["states"][1].__setitem__("motor_applied_n", 0.)),
            (self.positive, lambda w: w["harvests"][0].__setitem__("winner_cell_id", "B")),
            (self.positive, lambda w: w["harvests"][0].__setitem__("entry_time_s", .1)),
            (self.positive, lambda w: w["events"][1].__setitem__("amount_uj", 2)),
            (self.positive, lambda w: w["ledger"].__setitem__("balance_a_uj", 4)),
            (self.deferred, lambda w: w["states"][1].__setitem__("pending_a_uj", 0)),
            (self.deferred, lambda w: w["events"][-1].__setitem__("phase", "harvest")),
            (self.b_only, lambda w: w["states"][2].__setitem__("motor_applied_n", 2.)),
            (self.positive, lambda w: w["scenario"]["field"]["patches"][0].__setitem__(
                "center_m", .08)),
            (self.positive, lambda w: w["net_uj"].__setitem__("A", 12)),
        )
        for i, (original, alter) in enumerate(modifications):
            with self.subTest(attack=i):
                tampered = deepcopy(original)
                alter(tampered)
                with self.assertRaises(ValueError):
                    check_world(tampered)

    def test_reject_completely_altered_accounting_and_duplicate_claims(self):
        bad = deepcopy(self.positive)
        bad["harvests"] = bad["harvests"]*2
        with self.assertRaises(ValueError):
            check_world(bad)
        bad = deepcopy(self.positive)
        bad["states"][1]["candidate_charge_uj"] -= 1
        with self.assertRaises(ValueError):
            check_world(bad)


if __name__ == "__main__":
    unittest.main()
