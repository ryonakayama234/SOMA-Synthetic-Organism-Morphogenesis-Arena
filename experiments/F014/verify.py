"""Independent F014 saved-data oracle; no F014 producer/inference imports.

Researcher-side verifier reads F007 raw truth for auditing only. Full F007 raw
dynamics and ledger receive the existing independent F007 oracle. Every new
F014 local/peer projection and claimed verdict is checked separately.
"""
from __future__ import annotations

import hashlib
import json
import math
from fractions import Fraction as Q
from pathlib import Path

from soma.f007 import STATE_COLUMNS
from soma.f008 import COLUMNS
from experiments.F007.verify import audit_run, read_csv

GROUPS = ("L-linked", "G-ghost", "C-coforced", "N-free", "E-unexcited")
FORCES = ((2., "u2"), (1., "u1"), (.5, "u05"))
PACKET_COLUMNS = ("source", "step_index", "time_s", "moved")
SOURCE_FILES = (
    "soma/f014.py", "experiments/F014/run_suite.py",
    "experiments/F014/verify.py", "tests/test_f014.py",
    ".github/workflows/f014.yml",
    "topics/F014-peer-body-observability/SPEC.md",
    "experiments/F014/PLAN.md", "experiments/F014/README.md",
    "findings/F014-validation.md", "docs/ARCHITECTURE.md",
    "docs/DATA_CONTRACTS.md", "README.md", "AGENTS.md",
)
FILES = {
    "config.json", "F007/config.json", "F007/states.csv", "F007/ledger/events.csv",
    "F007/link_events.csv", "F007/motion.svg", "F007/manifest.json",
    "a_local.csv", "b_packets.csv",
}
TOL = 1e-12


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError("F014 independent oracle: " + message)


def eq(value: object, expected: object, label: str) -> None:
    if expected is None or type(expected) in (bool, str, int):
        require(type(value) is type(expected) and value == expected, label)
    else:
        require(type(value) in (int, float) and math.isfinite(value) and
                abs(value - float(expected)) <= TOL, label)


def expected_acc(group: str, force: Q) -> tuple[Q, Q]:
    if group == "L-linked":
        return force/2, force/2
    if group == "G-ghost":
        return force/2, Q(0)
    if group == "C-coforced":
        return force/2, force/2
    if group == "N-free":
        return force, Q(0)
    if group == "E-unexcited":
        return Q(0), Q(0)
    raise ValueError("unexpected group")


def _status(group: str) -> str:
    if group == "E-unexcited":
        return "inconclusive"
    return "peer_motion_seen" if group in ("L-linked", "C-coforced") else "peer_still"


def verify_suite(directory: Path, trusted_origin: dict) -> dict:
    root = Path(directory)
    manifest = json.loads((root/"manifest.json").read_text(encoding="utf-8"))
    require(set(manifest) == {"schema_version", "origin", "cases", "artifacts"},
            "manifest fields")
    require(manifest["schema_version"] == "f014.evidence.v1", "manifest version")
    require(manifest["origin"] == trusted_origin, "bound origin")
    require(manifest["cases"] == list(GROUPS), "case list")
    require(set(trusted_origin) == {"f007", "f014_source_hashes"}, "origin fields")
    require(set(trusted_origin["f014_source_hashes"]) == set(SOURCE_FILES),
            "source inventory")
    repo = Path(__file__).resolve().parents[2]
    for name, checksum in trusted_origin["f014_source_hashes"].items():
        require(type(checksum) is str and len(checksum) == 64,
                "source hash field")
        require(hashlib.sha256((repo/name).read_bytes()).hexdigest() == checksum,
                "source hash changed: " + name)
    expected_files = {"comparison.json"}
    for group in GROUPS:
        for _, tag in FORCES:
            expected_files.update(group+"/"+tag+"/"+name for name in FILES)
    found = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
    require(found == expected_files | {"manifest.json"}, "missing/extra evidence files")
    require(set(manifest["artifacts"]) == expected_files, "artifact inventory")
    for name, checksum in manifest["artifacts"].items():
        require(type(checksum) is str and len(checksum) == 64 and
                hashlib.sha256((root/name).read_bytes()).hexdigest() == checksum,
                "artifact SHA mismatch: " + name)

    for group in GROUPS:
        for force, tag in FORCES:
            prefix = group + "/" + tag
            folder = root/prefix
            audit_run(folder/"F007", trusted_origin=trusted_origin["f007"])
            frozen = json.loads((folder/"config.json").read_text(encoding="utf-8"))
            require(set(frozen) == {
                "schema_version", "experiment_id", "case_id", "u_n",
                "dt_s", "duration_s", "packet_threshold_m_s", "seed"},
                "F014 envelope schema")
            require(frozen["schema_version"] == "f014.config.v1" and
                    frozen["experiment_id"] == "F014-"+group+"-"+tag and
                    frozen["case_id"] == group and frozen["seed"] is None,
                    "F014 envelope identity")
            for key, target in (("u_n", force), ("dt_s", .25),
                                ("duration_s", 1.),
                                ("packet_threshold_m_s", 1e-10)):
                eq(frozen[key], target, "F014 envelope "+key)
            config = json.loads((folder/"F007/config.json").read_text(encoding="utf-8"))
            require(config["schema_version"] == "f007.v1" and
                    config["experiment_id"] == "F014-"+group+"-"+tag,
                    "F007 config identity " + prefix)
            for key, want in (("dt_s", .25), ("duration_s", 1.),
                              ("drag_per_s", 0.), ("motor_force_n", force)):
                eq(config[key], want, "config "+prefix+key)
            require(config["seed"] is None, "randomness added")
            link = config["link"]
            require(link["initially_attached"] is (group == "L-linked") and
                    link["detach_time_s"] is None, "link mismatch " + prefix)
            eq(link["length_m"], .5, "link length")
            cells = config["cells"]
            require([c["id"] for c in cells] == ["A", "B"], "cell ordering")
            for cell, x in zip(cells, (0., .5)):
                eq(cell["initial_x_m"], x, "initial x")
                eq(cell["initial_v_m_s"], 0., "initial v")
                eq(cell["mass_kg"], 1., "mass")
            eq(cells[0]["initial_balance_uj"],
               0 if group == "E-unexcited" else 3_000_000, "A battery")
            eq(cells[1]["initial_balance_uj"], 0, "B battery")
            eq(cells[0]["external_force_n"],
               -force/2 if group in ("G-ghost", "C-coforced") else 0.,
               "A hidden external")
            eq(cells[1]["external_force_n"],
               force/2 if group == "C-coforced" else 0., "B hidden external")

            raw = read_csv(folder/"F007/states.csv", STATE_COLUMNS,
                           strings=("decision_reason",), flags=("attached",),
                           integers=("step_index", "spent_a_uj", "balance_a_uj",
                                     "balance_b_uj", "ledger_event_index"))
            local = read_csv(folder/"a_local.csv", COLUMNS,
                             strings=("status",),
                             integers=("step_index", "balance_a_uj"))
            packets = read_csv(folder/"b_packets.csv", PACKET_COLUMNS,
                               strings=("source",), flags=("moved",),
                               integers=("step_index",))
            require(len(raw) == 5 and len(local) == len(packets) == 4,
                    "row count " + prefix)
            a, b = expected_acc(group, Q(str(force)))
            h = Q(1, 4)
            for k, (p, r, loc, pkt) in enumerate(zip(raw, raw[1:], local, packets), 1):
                mark = prefix + " step " + str(k) + " "
                eq(r["v_a_m_s"], a*k*h, mark+"A velocity")
                eq(r["x_a_m"], a*h*h*k*(k+1)/2, mark+"A position")
                eq(r["v_b_m_s"], b*k*h, mark+"B velocity")
                eq(r["x_b_m"], Q(1,2) + b*h*h*k*(k+1)/2,
                   mark+"B position")
                applied = 0. if group == "E-unexcited" else force
                eq(r["motor_applied_n"], applied, mark+"applied")
                required_local = {
                    "step_index": k, "time_s": k*.25, "dt_s": .25,
                    "v_prev_m_s": p["v_a_m_s"], "v_a_m_s": r["v_a_m_s"],
                    "motor_command_n": force, "motor_applied_n": applied,
                    "balance_a_uj": r["balance_a_uj"],
                    "observed_accel_m_s2": a,
                    "expected_accel_m_s2": None if group == "E-unexcited" else force,
                    "residual_m_s2": None if group == "E-unexcited" else a-Q(str(force)),
                    "status": ("not_excited" if group == "E-unexcited" else
                               "nominal" if group == "N-free" else "anomaly"),
                }
                require(set(loc) == set(required_local), mark+"A fields")
                for field, expected in required_local.items():
                    eq(loc[field], expected, mark+"local "+field)
                require(set(pkt) == set(PACKET_COLUMNS), mark+"peer fields")
                eq(pkt["source"], "B", mark+"peer source")
                eq(pkt["step_index"], k, mark+"peer index")
                eq(pkt["time_s"], k*.25, mark+"peer timestamp")
                eq(pkt["moved"], abs(float(b*h)) > 1e-10, mark+"peer sensor bit")

    for _, tag in FORCES:
        a = root/"L-linked"/tag
        g = root/"G-ghost"/tag
        c = root/"C-coforced"/tag
        require((a/"a_local.csv").read_bytes() == (g/"a_local.csv").read_bytes() ==
                (c/"a_local.csv").read_bytes(),
                "complete L/G/C local observational identity " + tag)
        require((a/"b_packets.csv").read_bytes() == (c/"b_packets.csv").read_bytes(),
                "L/C peer packet observational identity " + tag)
        require((a/"b_packets.csv").read_bytes() != (g/"b_packets.csv").read_bytes(),
                "L/G peer bit separation " + tag)

    comparison = json.loads((root/"comparison.json").read_text(encoding="utf-8"))
    require(set(comparison) == {
        "schema_version", "science_status", "researcher_truth_only",
        "fixed_cases", "force_levels_n", "intervals", "outcomes",
        "dropout_diagnostics", "A_local_LGC_byte_equal",
        "L_G_peer_bits_differ", "L_C_full_observation_equal",
        "topology_identified"}, "comparison schema")
    require(comparison["schema_version"] == "f014.comparison.v1", "comparison version")
    require(comparison["science_status"] == "software_model_candidate_not_adopted",
            "fabricated scientific acceptance")
    require(comparison["researcher_truth_only"] is True and
            comparison["topology_identified"] is False, "topology claim")
    require(comparison["fixed_cases"] == list(GROUPS) and
            comparison["force_levels_n"] == [2., 1., .5] and
            comparison["intervals"] == 60, "frozen labels/counts")
    for field in ("A_local_LGC_byte_equal", "L_G_peer_bits_differ",
                  "L_C_full_observation_equal"):
        require(comparison[field] is True, "counterexample or science claim")
    require(set(comparison["outcomes"]) == set(GROUPS), "outcome cases")
    for group in GROUPS:
        require(set(comparison["outcomes"][group]) == {tag for _,tag in FORCES},
                "outcome force tags")
        for _, tag in FORCES:
            r = comparison["outcomes"][group][tag]
            require(set(r) == {"schema_version", "status", "step_statuses",
                               "interpretation"}, "outcome fields")
            require(r["schema_version"] == "f014.comparison.v1" and
                    r["status"] == _status(group) and
                    r["step_statuses"] == [_status(group)]*4 and
                    r["interpretation"] == "peer_motion_only_not_mechanical_coupling",
                    "outcome independently evaluated " + group+"/"+tag)
    require(set(comparison["dropout_diagnostics"]) == {tag for _,tag in FORCES},
            "missing dropout condition")
    for _, tag in FORCES:
        r = comparison["dropout_diagnostics"][tag]
        require(set(r) == {"schema_version", "status", "step_statuses",
                           "interpretation"}, "dropout fields")
        require(r["schema_version"] == "f014.comparison.v1" and
                r["status"] == "inconclusive" and
                r["step_statuses"] == ["peer_motion_seen", "inconclusive",
                                     "peer_motion_seen", "peer_motion_seen"] and
                r["interpretation"] == "peer_motion_only_not_mechanical_coupling",
                "dropout evidence step 2")
    return {"cases": 15, "local_intervals": 60, "peer_bits": 60,
            "dropout_controls": 3, "L_G_separated": True,
            "L_C_indistinguishable": True, "topology_identified": False,
            "evidence_files": len(found)}
