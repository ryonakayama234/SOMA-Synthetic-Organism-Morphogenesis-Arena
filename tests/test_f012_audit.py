"""F012 integrity negative cases, including rehashed science claims."""
import unittest
import json
import tempfile
from pathlib import Path
from soma.f012 import Config,simulate
from experiments.F012.verify import audit_rows, verify_suite, sha
from experiments.F012.run_suite import build


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

    def test_rehashed_false_summary_still_rejected(self):
        checkout=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(prefix="f012-forgery-") as tmp:
            root=Path(tmp)/"study"
            build(root,checkout)
            comparison=root/"comparison.json"
            summary=json.loads(comparison.read_text(encoding="utf-8"))
            label="C-directional__1000000uj__dt0.01"
            summary["outcomes"][label]["center_final_m"]+=2.0
            comparison.write_text(json.dumps(summary,sort_keys=True)+"\n",encoding="utf-8")
            manifest=root/"manifest.json"
            metadata=json.loads(manifest.read_text(encoding="utf-8"))
            metadata["files"]["comparison.json"]=sha(comparison)
            manifest.write_text(json.dumps(metadata,sort_keys=True)+"\n",encoding="utf-8")
            with self.assertRaises(ValueError):
                verify_suite(root,checkout)


if __name__=="__main__": unittest.main()
