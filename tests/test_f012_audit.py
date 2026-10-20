"""F012 integrity negative cases, including rehashed science claims."""
import unittest
from soma.f012 import Config,simulate
from experiments.F012.verify import audit_rows


class F012IndependentOracleTests(unittest.TestCase):
    def test_independent_oracle(self):
        for case in ("B-isotropic","C-directional","D-mirror","E-no-drive"):
            rows=simulate(Config(case,1000000,.01))
            result=audit_rows(case,1000000,.01,rows)
            self.assertEqual(result["balance_uj"]+result["spent_uj"],1000000)

    def test_forged_world_row_rejected(self):
        rows=simulate(Config("C-directional",1000000,.01))
        rows[6]=dict(rows[6],x_cm_m=rows[6]["x_cm_m"]+.01)
        with self.assertRaises(ValueError):
            audit_rows("C-directional",1000000,.01,rows)

    def test_false_motor_cost_rejected(self):
        rows=simulate(Config("C-directional",1000000,.01))
        rows[1]=dict(rows[1],spent_uj=0)
        with self.assertRaises(ValueError):
            audit_rows("C-directional",1000000,.01,rows)

    def test_missing_rows_rejected(self):
        rows=simulate(Config("C-directional",1000000,.01))
        with self.assertRaises(ValueError):
            audit_rows("C-directional",1000000,.01,rows[:-1])


if __name__=="__main__": unittest.main()
