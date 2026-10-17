"""V001 regression: F007 world truth cannot be changed by the viewer."""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from experiments.F007.run_suite import scenarios
from experiments.F007.verify import audit_run
from experiments.V001.build_view import generate
from experiments.V001.verify import audit_view
from soma.f007 import Config, provenance, save_run
from soma.v001 import canonical_json, project_run, sha256, verify_frame_projection


class V001Test(unittest.TestCase):
    def make_pair(self, case: str, base: Path) -> tuple[Path,Path,dict]:
        source, view = base / "raw", base / "view"
        save_run(Config.from_dict(scenarios()[case]), source)
        origin = provenance()
        generate(source, view, trusted_origin=origin)
        return source, view, origin

    def test_every_f007_scenario_projects_without_changes(self):
        for name in scenarios():
            with self.subTest(name=name), TemporaryDirectory() as tmp:
                source,view,identity = self.make_pair(name,Path(tmp))
                audit_run(source,trusted_origin=identity)
                report = audit_view(source,view,trusted_origin=identity)
                self.assertEqual(report["coverage"],1.0)
                self.assertEqual(report["max_projection_error"],0)
                original = json.loads((view/"frames.json").read_text("utf-8"))
                self.assertEqual(verify_frame_projection(source,original,
                    trusted_origin=identity)["frames_checked"],
                    Config.from_dict(scenarios()[name]).steps+1)
                html=(view/"viewer.html").read_text("utf-8")
                self.assertIn('id="rail"',html)
                self.assertNotIn("__FRAME_B64__",html)
                self.assertIn('type="range"',html)

    def test_cut_is_post_event_without_motion_jump(self):
        with TemporaryDirectory() as tmp:
            source,view,_=self.make_pair("E-cut",Path(tmp))
            frames=json.loads((view/"frames.json").read_text())["frames"]
            self.assertEqual([f["attached"] for f in frames],
                             [True,True,False,False,False])
            self.assertEqual(frames[0]["link_event_kind"],"attach_initial")
            self.assertEqual(frames[2]["link_event_kind"],"detach")
            self.assertEqual((frames[2]["time_s"],frames[2]["x_a_m"],
                              frames[2]["x_b_m"]),(0.5,0.1875,0.6875))
            self.assertEqual((frames[4]["v_a_m_s"],frames[4]["v_b_m_s"]),(1.5,0.5))

    def test_motor_command_not_confused_with_applied(self):
        with TemporaryDirectory() as tmp:
            _,view,_=self.make_pair("C-zero",Path(tmp))
            frames=json.loads((view/"frames.json").read_text())["frames"]
            self.assertTrue(all(f["motor_command_n"]==2 for f in frames))
            self.assertTrue(all(f["motor_applied_n"]==0 for f in frames))
            self.assertTrue(all(f["balance_a_uj"]==0 for f in frames))

    def test_frame_tamper_with_recomputed_hash_is_rejected(self):
        with TemporaryDirectory() as tmp:
            source,view,origin=self.make_pair("E-cut",Path(tmp))
            payload=json.loads((view/"frames.json").read_text("utf-8"))
            payload["frames"][2]["x_a_m"]+=0.125
            (view/"frames.json").write_bytes(canonical_json(payload))
            manifest=json.loads((view/"viewer_manifest.json").read_text())
            manifest["output_artifacts_sha256"]["frames.json"]=sha256(view/"frames.json")
            (view/"viewer_manifest.json").write_bytes(canonical_json(manifest))
            with self.assertRaises(ValueError):
                audit_view(source,view,trusted_origin=origin)

    def test_html_tamper_with_recomputed_hash_is_rejected(self):
        with TemporaryDirectory() as tmp:
            source,view,origin=self.make_pair("A-free",Path(tmp))
            with (view/"viewer.html").open("ab") as fp:
                fp.write(b"\n<!-- malicious change -->\n")
            manifest=json.loads((view/"viewer_manifest.json").read_text())
            manifest["output_artifacts_sha256"]["viewer.html"]=sha256(view/"viewer.html")
            (view/"viewer_manifest.json").write_bytes(canonical_json(manifest))
            with self.assertRaisesRegex(ValueError,"viewer HTML differs"):
                audit_view(source,view,trusted_origin=origin)

    def test_source_rehash_cannot_hide_semantic_change(self):
        with TemporaryDirectory() as tmp:
            source,view,origin=self.make_pair("B-linked",Path(tmp))
            rows=(source/"states.csv").read_text("utf-8")
            self.assertIn("0.625",rows)
            (source/"states.csv").write_text(rows.replace("0.625","0.626",1),encoding="utf-8")
            saved=json.loads((source/"manifest.json").read_text())
            saved["artifacts"]["states.csv"]=sha256(source/"states.csv")
            (source/"manifest.json").write_text(json.dumps(saved,indent=2,sort_keys=True)+"\n")
            with self.assertRaises((AssertionError, ValueError)):
                audit_view(source,view,trusted_origin=origin)

    def test_missing_source_field_and_existing_destination_fail(self):
        with TemporaryDirectory() as tmp:
            base=Path(tmp)
            source,view,origin=self.make_pair("A-free",base)
            with self.assertRaises(FileExistsError):
                generate(source,view,trusted_origin=origin)
            (source/"link_events.csv").unlink()
            with self.assertRaises((AssertionError, ValueError, FileNotFoundError)):
                project_run(source,trusted_origin=origin)

    def test_same_input_recreates_identical_all_evidence(self):
        with TemporaryDirectory() as tmp:
            base=Path(tmp)
            source,view,identity=self.make_pair("E-cut",base)
            other=base/"view_again"
            generate(source,other,trusted_origin=identity)
            for name in ("frames.json","viewer.html","viewer_manifest.json"):
                self.assertEqual((view/name).read_bytes(),(other/name).read_bytes(),name)

    def test_no_invalid_output_on_failed_verification(self):
        with TemporaryDirectory() as tmp:
            base=Path(tmp)
            source,view,origin=self.make_pair("A-free",base)
            (source/"states.csv").write_text("corrupt\n",encoding="utf-8")
            failed=base/"failed"
            with self.assertRaises((AssertionError,ValueError)):
                generate(source,failed,trusted_origin=origin)
            self.assertFalse(failed.exists())
            self.assertTrue(view.exists())


if __name__ == "__main__":
    unittest.main()
