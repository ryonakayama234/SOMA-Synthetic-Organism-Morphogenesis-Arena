"""Cross-check preregistered universe and independent verifier boundary."""
from __future__ import annotations
import unittest
from soma.f019 import scenario_grid
from experiments.F019.verify import expected_scenes, expected_hit_set

class F019ExperimentTest(unittest.TestCase):
    def test_independent_generator_all_frozen_worlds(self):
        a, b = scenario_grid(), expected_scenes()
        self.assertEqual(a, b)
        self.assertEqual(len({x["scenario_id"] for x in a}), 512)

    def test_independent_first_entry_owner_tie(self):
        field = {"patches": [
            {"patch_id": "P0", "center_m": .2, "radius_m": .01,
             "initial_available_uj": 1000000}]}
        path = [(0., 0.), (.3, .3), (.1, .1)]
        result = expected_hit_set(field, path)
        self.assertEqual(result[0]["winner_cell_id"], "A")
        self.assertEqual(result[0]["ordinal"], 1)
        self.assertEqual(len(result), 1)

if __name__ == "__main__":
    unittest.main()
