"""Run F001 A--E control experiments; save immutable traces + comparison."""

from dataclasses import replace
import argparse
import json
from pathlib import Path

from soma.f001 import RunConfig, analytic_state, save_run


def main() -> None:
    parser = argparse.ArgumentParser(description="Run F001 control conditions A--E")
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    base = RunConfig.from_json(Path("experiments/F001/configs/B_positive.json"))
    settings = {
        "A_rest": replace(base, experiment_id="F001-A-rest", force_n=0.0),
        "B_positive": base,
        "C_negative": replace(base, experiment_id="F001-C-negative", force_n=-1.0),
        "D_drag": replace(base, experiment_id="F001-D-drag", force_n=0.0, initial_v_m_s=1.0),
        "E_half": replace(base, experiment_id="F001-E-half", dt_s=0.005),
        "E_quarter": replace(base, experiment_id="F001-E-quarter", dt_s=0.0025),
    }
    args.output_dir.mkdir(parents=True, exist_ok=False)
    results = {key: save_run(cfg, args.output_dir/key) for key,cfg in settings.items()}
    x_ref, v_ref = analytic_state(base,base.duration_s)
    errors = [results[key]["absolute_x_error_m"] for key in ("B_positive", "E_half", "E_quarter")]
    report = {
        "model": "1d_linear_drag", "numerical_method": "semi_implicit_euler",
        "continuous_reference_x_m": x_ref,
        "continuous_reference_v_m_s": v_ref,
        "condition_summary": {key: {k:v for k,v in result.items() if k in ("sample_count", "final_x_m", "final_v_m_s", "absolute_x_error_m", "absolute_v_error_m_s")} for key,result in results.items()},
        "step_halving": {"dt_s":[.01,.005,.0025], "x_errors_m":errors, "error_ratios":[errors[0]/errors[1],errors[1]/errors[2]], "position_difference_m":results["B_positive"]["final_x_m"]-results["E_half"]["final_x_m"]},
    }
    (args.output_dir/"comparison.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))


if __name__ == "__main__":
    main()
