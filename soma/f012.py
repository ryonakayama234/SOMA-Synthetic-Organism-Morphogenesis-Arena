"""F012: research-only finite positive-mechanical-work budget for F011's 1D passive ground.

Not a cell-local controller, real electric battery, or a new continuous contact model.
Unmodified F011 passive law and F005 ideal positive-work integrator are reused.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

from soma.f005 import positive_motor_work
from soma.f011 import passive_contact

SCHEMA = "f012.energy.v1"
DTS = (0.01, 0.005, 0.0025)
BUDGETS_UJ = (0, 1_000_000, 3_000_000, 10_000_000)
CASES = {
    "B-isotropic": (0.04, 0.04, True),
    "C-directional": (0.02, 0.08, True),
    "D-mirror": (0.08, 0.02, True),
    "E-no-drive": (0.02, 0.08, False),
}
COLUMNS = (
    "step", "time_s", "x_a_m", "x_b_m", "v_a_m_s", "v_b_m_s",
    "r_m", "x_cm_m", "motor_command_n", "motor_applied_n",
    "motor_candidate_positive_j", "motor_positive_j", "motor_signed_j",
    "spent_uj", "balance_uj", "decision", "ground_a_n", "ground_b_n",
    "ground_work_j", "kinetic_j", "spring_j", "impulse_residual_ns",
    "energy_defect_j", "expected_defect_j",
)


@dataclass(frozen=True)
class Config:
    case_id: str
    budget_uj: int
    dt_s: float

    def __post_init__(self):
        if type(self.case_id) is not str or self.case_id not in CASES:
            raise ValueError("not a frozen F012 case")
        if type(self.budget_uj) is not int or self.budget_uj not in BUDGETS_UJ:
            raise ValueError("not a frozen integer-microjoule budget")
        if type(self.dt_s) is not float or self.dt_s not in DTS:
            raise ValueError("not a frozen timestep")

    def as_dict(self):
        plus, minus, active = CASES[self.case_id]
        return {
            "schema_version": SCHEMA, "case_id": self.case_id,
            "budget_uj": self.budget_uj, "dt_s": self.dt_s,
            "duration_s": 9.6, "seed": None, "m_kg": 1.0,
            "g_m_s2": 9.81, "initial_x_a_m": -0.25,
            "initial_x_b_m": 0.25, "initial_v_a_m_s": 0.0,
            "initial_v_b_m_s": 0.0, "rest_m": 0.5,
            "spring_n_m": 20.0, "period_s": 1.2,
            "motor_amplitude_n": 1.0 if active else 0.0,
            "mu_plus": plus, "mu_minus": minus,
            "min_stroke_m": 0.2, "max_stroke_m": 0.8,
            "charge_rule": "ceil_per_accepted_interval_positive_relative_mechanical_work_uj",
            "ground_rule": "f011_velocity_implicit_directional_coulomb",
        }


class StrokeLimitError(ValueError):
    def __init__(self, step: int, attempted_r: float, valid_rows: list[dict]):
        self.step = step
        self.attempted_r = attempted_r
        self.valid_rows = valid_rows
        super().__init__("F012 stroke limit at step %d r=%r" % (step, attempted_r))


def _step(xa, xb, va, vb, h, u, plus, minus):
    r = xb - xa
    internal = u + 20.0 * (r - 0.5)
    va_star = va + h * internal
    vb_star = vb - h * internal
    van, fa = passive_contact(va_star, h, plus, minus)
    vbn, fb = passive_contact(vb_star, h, plus, minus)
    xan, xbn = xa + h * van, xb + h * vbn
    values = (van, vbn, fa, fb, xan, xbn, xbn - xan)
    if not all(math.isfinite(v) for v in values):
        raise ValueError("nonfinite derived world state")
    return xan, xbn, van, vbn, fa, fb


def simulate(cfg: Config) -> list[dict]:
    if not isinstance(cfg, Config):
        raise TypeError("F012 Config required")
    h, balance = cfg.dt_s, cfg.budget_uj
    n = round(9.6 / h)
    half = round(0.6 / h)
    plus, minus, has_motor = CASES[cfg.case_id]
    xa, xb, va, vb = -0.25, 0.25, 0.0, 0.0
    rows = []

    def record(i, cmd=None, applied=None, candidate=None, wplus=None,
               wsigned=None, spent=None, decision=None, fa=None, fb=None,
               wg=None, impulse=None, defect=None, expected=None):
        rr = xb - xa
        values = (i, i * h, xa, xb, va, vb, rr, (xa + xb) / 2,
                  cmd, applied, candidate, wplus, wsigned,
                  spent, balance, decision, fa, fb, wg,
                  (va * va + vb * vb) / 2, 10.0 * (rr - 0.5) ** 2,
                  impulse, defect, expected)
        return dict(zip(COLUMNS, values))

    rows.append(record(0))
    for i in range(1, n + 1):
        command = (1.0 if ((i - 1) // half) % 2 == 0 else -1.0) if has_motor else 0.0
        candidate = 0.0
        spent = 0
        if not command:
            applied, decision = 0.0, "zero_command"
        elif balance == 0:
            applied, decision = 0.0, "zero_balance"
        else:
            test = _step(xa, xb, va, vb, h, command, plus, minus)
            candidate = positive_motor_work(command, va - vb, test[2] - test[3], h)
            if not math.isfinite(candidate) or candidate < 0:
                raise ValueError("nonfinite candidate work")
            charge_float = 1_000_000 * candidate
            if not math.isfinite(charge_float):
                raise ValueError("nonfinite candidate charge")
            wanted = math.ceil(charge_float)
            if wanted <= balance:
                applied, spent = command, wanted
                decision = "accepted_positive_work" if wanted else "accepted_nonpositive_work"
            else:
                applied, decision = 0.0, "insufficient_balance"

        old_r = xb - xa
        old_k = (va * va + vb * vb) / 2
        old_s = 10.0 * (old_r - 0.5) ** 2
        xan, xbn, van, vbn, fa, fb = _step(
            xa, xb, va, vb, h, applied, plus, minus)
        new_r = xbn - xan
        if new_r < 0.2 - 1e-12 or new_r > 0.8 + 1e-12:
            raise StrokeLimitError(i, new_r, rows)
        wplus = positive_motor_work(applied, va - vb, van - vbn, h)
        if spent != (math.ceil(1_000_000 * wplus) if applied else 0):
            raise ArithmeticError("accepted cost inconsistent with applied motion")
        wsigned = h * applied * (van - vbn)
        wg = h * (fa * van + fb * vbn)
        new_k = (van * van + vbn * vbn) / 2
        new_s = 10.0 * (new_r - 0.5) ** 2
        impulse = (van + vbn - va - vb) - h * (fa + fb)
        defect = (new_k + new_s - old_k - old_s) - wsigned - wg
        expected = 10.0 * (new_r - old_r) ** 2 - (
            (van - va) ** 2 + (vbn - vb) ** 2) / 2
        if wg > 1e-11 or abs(impulse) > 1e-10 or abs(defect - expected) > 1e-9:
            raise ArithmeticError("F012 motion/energy identity failed")
        if spent > balance:
            raise ArithmeticError("overdraft")
        balance -= spent
        xa, xb, va, vb = xan, xbn, van, vbn
        rows.append(record(i, command, applied, candidate, wplus,
                           wsigned, spent, decision, fa, fb, wg,
                           impulse, defect, expected))
    if sum(int(x["spent_uj"]) for x in rows[1:]) + balance != cfg.budget_uj:
        raise ArithmeticError("integer budget identity failed")
    return rows


def measurements(rows: list[dict]) -> dict:
    if len(rows) < 3:
        raise ValueError("full trace required")
    h = rows[1]["time_s"]
    period_steps = round(1.2 / h)
    last, prev, earlier = rows[-1], rows[-1 - period_steps], rows[-1 - 2 * period_steps]
    positive = math.fsum(x["motor_positive_j"] for x in rows[1:])
    charged = sum(x["spent_uj"] for x in rows[1:])
    return {
        "center_final_m": last["x_cm_m"],
        "last_period_m": last["x_cm_m"] - prev["x_cm_m"],
        "penultimate_period_m": prev["x_cm_m"] - earlier["x_cm_m"],
        "stroke_return_m": last["r_m"] - prev["r_m"],
        "accepted_steps": sum(x["motor_applied_n"] != 0 for x in rows[1:]),
        "rejected_steps": sum(x["decision"] in ("zero_balance", "insufficient_balance")
                              and x["motor_command_n"] != 0 for x in rows[1:]),
        "spent_uj": charged,
        "balance_uj": last["balance_uj"],
        "positive_work_j": positive,
        "quantization_excess_j": charged / 1_000_000 - positive,
        "signed_motor_work_j": math.fsum(x["motor_signed_j"] for x in rows[1:]),
        "ground_work_j": math.fsum(x["ground_work_j"] for x in rows[1:]),
        "min_stroke_m": min(x["r_m"] for x in rows),
        "max_stroke_m": max(x["r_m"] for x in rows),
    }
