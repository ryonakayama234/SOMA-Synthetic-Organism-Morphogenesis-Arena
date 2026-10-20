"""F011: frozen 1D two-cell internal actuation and passive grounded stick/slip.

Research-only world model, not an autonomous agent, real contact, or battery.
Existing F001-F010 interfaces deliberately remain untouched.
"""
from __future__ import annotations
from dataclasses import dataclass
import math

SCHEMA = 'f011.states.v1'
DTS = (0.01, 0.005, 0.0025)
CASES = {
    'A-no-contact': (0.0, 0.0, 1.0),
    'B-isotropic': (0.04, 0.04, 1.0),
    'C-directional': (0.02, 0.08, 1.0),
    'D-mirror': (0.08, 0.02, 1.0),
    'E-no-motor': (0.02, 0.08, 0.0),
}
COLUMNS = ('step','time_s','x_a_m','x_b_m','v_a_m_s','v_b_m_s','r_m',
    'x_cm_m','internal_n','ground_a_n','ground_b_n','ground_work_j',
    'motor_work_j','kinetic_j','spring_j','impulse_residual_ns',
    'energy_defect_j','expected_defect_j')

@dataclass(frozen=True)
class Config:
    case_id: str
    dt_s: float

    def __post_init__(self):
        if not isinstance(self.case_id, str) or self.case_id not in CASES:
            raise ValueError('case is not preregistered')
        if type(self.dt_s) is not float or self.dt_s not in DTS:
            raise ValueError('dt is not preregistered')

    def as_dict(self):
        mu_plus, mu_minus, amp = CASES[self.case_id]
        return {'schema_version':'f011.config.v1','case_id':self.case_id,
          'dt_s':self.dt_s,'duration_s':9.6,'m_kg':1.0,'g_m_s2':9.81,
          'x_a0_m':-0.25,'x_b0_m':0.25,'v_a0_m_s':0.0,'v_b0_m_s':0.0,
          'rest_m':0.5,'k_n_m':20.0,'amplitude_n':amp,'period_s':1.2,
          'mu_plus':mu_plus,'mu_minus':mu_minus,'stroke_min_m':0.2,
          'stroke_max_m':0.8,'seed':None,
          'ground_semantics':'velocity_implicit_directional_coulomb_equal_static_kinetic'}

def passive_contact(v_star: float, h: float, mu_plus: float, mu_minus: float):
    """Velocity-implicit Coulomb shrinkage. Returns (vnext, ground force) at m=1 kg."""
    if v_star > 0.0:
        v_next = max(0.0, v_star - h * mu_plus * 9.81)
    elif v_star < 0.0:
        v_next = min(0.0, v_star + h * mu_minus * 9.81)
    else:
        v_next = 0.0
    return v_next, (v_next - v_star) / h

class StrokeLimitError(ValueError):
    def __init__(self, step: int, attempted_r: float, valid_rows: list[dict]):
        self.step=step
        self.attempted_r=attempted_r
        self.valid_rows=valid_rows
        super().__init__(f'outside preregistered stroke at step {step}: {attempted_r}')

def simulate(config: Config) -> list[dict]:
    if not isinstance(config, Config):
        raise TypeError('requires frozen Config')
    h=config.dt_s
    half_steps=round(0.6/h)
    n_steps=round(9.6/h)
    if abs(half_steps*h-0.6)>1e-12 or abs(n_steps*h-9.6)>1e-12:
        raise ValueError('inexact experiment grid')
    mu_plus,mu_minus,amp=CASES[config.case_id]
    xa,xb,va,vb=-0.25,0.25,0.0,0.0
    rows=[]
    def state(i,internal=None,ga=None,gb=None,gw=None,mw=None,impulse=None,defect=None,expected=None):
        r=xb-xa
        return dict(zip(COLUMNS,(i,i*h,xa,xb,va,vb,r,(xa+xb)/2,
           internal,ga,gb,gw,mw,(va*va+vb*vb)/2,
           10.0*(r-0.5)**2,impulse,defect,expected)))
    rows.append(state(0))
    for step in range(1,n_steps+1):
        u=amp*(1.0 if ((step-1)//half_steps)%2==0 else -1.0)
        r=xb-xa
        internal=u+20.0*(r-0.5)
        a_star=va+h*internal
        b_star=vb-h*internal
        va_next,fa=passive_contact(a_star,h,mu_plus,mu_minus)
        vb_next,fb=passive_contact(b_star,h,mu_plus,mu_minus)
        xa_next=xa+h*va_next
        xb_next=xb+h*vb_next
        r_next=xb_next-xa_next
        if not all(map(math.isfinite,(va_next,vb_next,xa_next,xb_next,fa,fb,r_next))):
            raise ValueError('nonfinite derived state')
        if not 0.2-1e-12<=r_next<=0.8+1e-12:
            raise StrokeLimitError(step,r_next,rows)
        old_energy=(va*va+vb*vb)/2+10.0*(r-0.5)**2
        new_energy=(va_next**2+vb_next**2)/2+10.0*(r_next-0.5)**2
        wm=h*u*(va_next-vb_next)
        wg=h*(fa*va_next+fb*vb_next)
        impulse=(va_next+vb_next-va-vb)-h*(fa+fb)
        energy_defect=(new_energy-old_energy)-wm-wg
        expected_defect=10.0*(r_next-r)**2-((va_next-va)**2+(vb_next-vb)**2)/2
        if wg>1e-11 or abs(impulse)>1e-10 or abs(energy_defect-expected_defect)>1e-9:
            raise ArithmeticError(f'physics invariant broken at step {step}')
        xa,xb,va,vb=xa_next,xb_next,va_next,vb_next
        rows.append(state(step,internal,fa,fb,wg,wm,impulse,energy_defect,expected_defect))
    return rows

def measurements(rows: list[dict]) -> dict:
    h=rows[1]['time_s']
    steps_period=round(1.2/h)
    z=rows[-1];p=rows[-1-steps_period];q=rows[-1-2*steps_period]
    return {'center_final_m':z['x_cm_m'],
       'last_period_m':z['x_cm_m']-p['x_cm_m'],
       'penultimate_period_m':p['x_cm_m']-q['x_cm_m'],
       'last_period_stroke_return_m':z['r_m']-p['r_m'],
       'max_impulse_residual_ns':max(abs(x['impulse_residual_ns']) for x in rows[1:]),
       'max_energy_identity_error_j':max(abs(x['energy_defect_j']-x['expected_defect_j']) for x in rows[1:]),
       'sum_ground_work_j':math.fsum(x['ground_work_j'] for x in rows[1:]),
       'sum_motor_work_j':math.fsum(x['motor_work_j'] for x in rows[1:]),
       'max_stroke_m':max(x['r_m'] for x in rows),
       'min_stroke_m':min(x['r_m'] for x in rows)}
