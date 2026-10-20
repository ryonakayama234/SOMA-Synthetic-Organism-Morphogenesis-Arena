"""F013: preregistered *alternative* smooth passive-friction two-cell model.

Researcher-only ideal 1D world, never an autonomous cell interface. No import
of F011/F012 simulation and no changes to their accepted semantics.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

SCHEMA = "f013.states.v1"
DTS = (0.01, 0.005, 0.0025)
EPSILONS = (0.02, 0.005, 0.001)
CASES = {
    "B-isotropic": (0.04, 0.04, True),
    "C-directional": (0.02, 0.08, True),
    "D-mirror": (0.08, 0.02, True),
    "E-no-drive": (0.02, 0.08, False),
}
COLUMNS = (
    "step", "time_s", "x_a_m", "x_b_m", "v_a_m_s", "v_b_m_s",
    "r_m", "x_cm_m", "motor_n", "ground_a_n", "ground_b_n",
    "ground_work_j", "motor_work_j", "kinetic_j", "spring_j",
    "impulse_residual_ns", "energy_defect_j", "expected_defect_j",
)


@dataclass(frozen=True)
class Config:
    case_id: str
    eps_m_s: float
    dt_s: float

    def __post_init__(self):
        if type(self.case_id) is not str or self.case_id not in CASES:
            raise ValueError("invalid frozen F013 case")
        if type(self.eps_m_s) is not float or self.eps_m_s not in EPSILONS:
            raise ValueError("invalid frozen smoothing width")
        if type(self.dt_s) is not float or self.dt_s not in DTS:
            raise ValueError("invalid frozen integration step")

    def as_dict(self):
        mp, mm, motor = CASES[self.case_id]
        return dict(
            schema_version="f013.config.v1", case_id=self.case_id,
            eps_m_s=self.eps_m_s, dt_s=self.dt_s,
            mu_plus=mp, mu_minus=mm, amplitude_n=1.0 if motor else 0.0,
            mass_kg=1.0, gravity_m_s2=9.81, spring_n_m=20.0,
            rest_m=0.5, x_a0_m=-0.25, x_b0_m=0.25,
            v_a0_m_s=0.0, v_b0_m_s=0.0,
            stroke_min_m=0.2, stroke_max_m=0.8,
            period_s=1.2, duration_s=9.6, seed=None,
            ground_model="smooth_directional_tanh_implicit_v1",
            solver="bounded_monotone_bisection_velocity_abs_1e-13",
        )


def passive_contact(v_star: float, h: float, mp: float, mm: float, eps: float):
    """Solve v+h*g*mu_sign*tanh(v/eps)=vstar with monotone bracketing."""
    if not all(math.isfinite(x) for x in (v_star, h, mp, mm, eps)):
        raise ValueError("nonfinite contact input")
    if h <= 0 or eps <= 0 or min(mp, mm) < 0:
        raise ValueError("invalid contact parameters")
    if v_star == 0:
        return 0.0, 0.0
    mu = mp if v_star > 0 else mm
    lo, hi = (0.0, v_star) if v_star > 0 else (v_star, 0.0)
    for _ in range(80):
        mid = lo + (hi - lo) * 0.5
        residual = mid + h * 9.81 * mu * math.tanh(mid / eps) - v_star
        if residual < 0:
            lo = mid
        else:
            hi = mid
        if hi - lo <= 1e-13:
            break
    else:
        raise ArithmeticError("unresolved implicit friction root")
    v_next = lo + (hi - lo) * 0.5
    f_ground = (v_next - v_star) / h
    if v_next * f_ground > 1e-11:
        raise ArithmeticError("contact did positive work")
    return v_next, f_ground


class StrokeLimitError(ValueError):
    def __init__(self, step: int, attempted_r: float, valid_rows: list):
        self.step = step
        self.attempted_r = attempted_r
        self.valid_rows = valid_rows
        super().__init__(f"F013 frozen stroke invalid at {step}: {attempted_r}")


def simulate(cfg: Config):
    if not isinstance(cfg, Config):
        raise TypeError("Config required")
    h, eps = cfg.dt_s, cfg.eps_m_s
    half, count = round(0.6 / h), round(9.6 / h)
    if abs(half*h - 0.6) > 1e-12 or abs(count*h - 9.6) > 1e-12:
        raise ValueError("not aligned with frozen drive phase")
    mp, mm, active = CASES[cfg.case_id]
    xa, xb, va, vb = -0.25, 0.25, 0.0, 0.0
    rows = []

    def row(i, u=None, fa=None, fb=None, wg=None, wm=None, imp=None,
            defect=None, expected=None):
        rr = xb-xa
        return dict(zip(COLUMNS, (
            i, i*h, xa, xb, va, vb, rr, (xa+xb)/2,
            u, fa, fb, wg, wm, (va*va+vb*vb)/2,
            10.0*(rr-0.5)**2, imp, defect, expected,
        )))

    rows.append(row(0))
    for i in range(1, count+1):
        u = (1.0 if ((i-1)//half)%2 == 0 else -1.0) if active else 0.0
        old_r = xb-xa
        internal = u+20.0*(old_r-0.5)
        van, fa = passive_contact(va+h*internal, h, mp, mm, eps)
        vbn, fb = passive_contact(vb-h*internal, h, mp, mm, eps)
        xan, xbn = xa+h*van, xb+h*vbn
        rn = xbn-xan
        if not all(map(math.isfinite, (van, vbn, fa, fb, xan, xbn, rn))):
            raise ArithmeticError("nonfinite simulated state")
        if not 0.2-1e-12 <= rn <= 0.8+1e-12:
            raise StrokeLimitError(i, rn, rows)
        old_energy = (va*va+vb*vb)/2 + 10.0*(old_r-0.5)**2
        new_energy = (van*van+vbn*vbn)/2 + 10.0*(rn-0.5)**2
        wm = h*u*(van-vbn)
        wg = h*(fa*van+fb*vbn)
        imp = van+vbn-va-vb-h*(fa+fb)
        defect = new_energy-old_energy-wm-wg
        expected = 10.0*(rn-old_r)**2-((van-va)**2+(vbn-vb)**2)/2
        if wg > 1e-11 or abs(imp) > 1e-10 or abs(defect-expected) > 1e-9:
            raise ArithmeticError("invalid discrete mechanics")
        xa, xb, va, vb = xan, xbn, van, vbn
        rows.append(row(i, u, fa, fb, wg, wm, imp, defect, expected))
    return rows


def summarize(rows):
    h = rows[1]["time_s"]
    period = round(1.2/h)
    z = rows[-1]
    result = dict(
        observed_steps=len(rows)-1, complete=len(rows)-1 == round(9.6/h),
        center_final_m=z["x_cm_m"],
        max_abs_impulse_residual_ns=max(abs(r["impulse_residual_ns"]) for r in rows[1:]),
        max_abs_energy_identity_error_j=max(abs(r["energy_defect_j"]-r["expected_defect_j"]) for r in rows[1:]),
        ground_work_total_j=math.fsum(r["ground_work_j"] for r in rows[1:]),
        min_r_m=min(r["r_m"] for r in rows),
        max_r_m=max(r["r_m"] for r in rows),
    )
    if result["complete"]:
        p, q = rows[-1-period], rows[-1-2*period]
        result.update(
            last_period_m=z["x_cm_m"]-p["x_cm_m"],
            penultimate_period_m=p["x_cm_m"]-q["x_cm_m"],
            last_period_r_return_m=z["r_m"]-p["r_m"],
        )
    return result
