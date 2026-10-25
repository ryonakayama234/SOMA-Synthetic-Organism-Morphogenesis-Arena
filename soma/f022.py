"""F022.v1: passive two-disk continuous 2D encounter, not self-assembly.

Frozen before observation: experiments/F022/FROZEN_V1.md at
3984e9dcb2cb420abab5ca92b4d029b31b5173f8.
No controller, ground reaction, motor, energy ledger or bond is modeled.
"""
from __future__ import annotations

import math

SCHEMA = 'f022.archive.v1'
FREEZE_COMMIT = '3984e9dcb2cb420abab5ca92b4d029b31b5173f8'
SAMPLES = tuple(k / 4 for k in range(9))
FIELDS = ('world_id', 'x_a_m', 'y_a_m', 'vx_a_mps', 'vy_a_mps',
          'x_b_m', 'y_b_m', 'vx_b_mps', 'vy_b_mps', 'mass_a_kg',
          'mass_b_kg', 'radius_a_m', 'radius_b_m', 'restitution',
          'duration_s', 'sample_dt_s')


def grid() -> list[dict]:
    result = []
    for i in range(1, 14):
        y = {3: .6, 4: .6, 5: 1.01, 6: .99, 7: 1., 9: .6, 11: .6}.get(i, 0.)
        pa, pb, va, vb = (-1., 0.), (1., y), (1., 0.), (-1., 0.)
        e = .5 if i in (2, 4) else 1.
        if i == 8:
            va, vb = (-1., 0.), (1., 0.)
        if i == 9:
            vb = (1., 0.)
        if i == 10:
            pa, pb = (9., -7.), (11., -7.)
        if i == 11:
            rot = lambda p: (-p[1], p[0])
            pa, pb, va, vb = map(rot, (pa, pb, va, vb))
        if i == 12:
            pa, pb, va, vb = pb, pa, vb, va
        if i == 13:
            pa, pb, va, vb = (-10., 0.), (10., 0.), (100., 0.), (-100., 0.)
        result.append(dict(world_id=f'C{i:02d}', x_a_m=pa[0], y_a_m=pa[1],
                           x_b_m=pb[0], y_b_m=pb[1], vx_a_mps=va[0],
                           vy_a_mps=va[1], vx_b_mps=vb[0], vy_b_mps=vb[1],
                           mass_a_kg=1., mass_b_kg=1., radius_a_m=.5,
                           radius_b_m=.5, restitution=e, duration_s=2.,
                           sample_dt_s=.25))
    return result


def validate(s: dict) -> None:
    if not isinstance(s, dict) or set(s) != set(FIELDS):
        raise ValueError('schema mismatch')
    if not isinstance(s['world_id'], str):
        raise ValueError('world ID')
    for k in FIELDS:
        if k == 'world_id':
            continue
        if type(s[k]) not in (float, int) or not math.isfinite(s[k]):
            raise ValueError(f'nonfinite/bad {k}')
    if (s['mass_a_kg'] != 1 or s['mass_b_kg'] != 1 or
        s['radius_a_m'] != .5 or s['radius_b_m'] != .5 or
        s['restitution'] not in (1., .5) or s['duration_s'] != 2 or
        s['sample_dt_s'] != .25):
        raise ValueError('outside frozen v1 physics')
    if math.hypot(s['x_b_m'] - s['x_a_m'], s['y_b_m'] - s['y_a_m']) <= 1.:
        raise ValueError('initial touching or penetration')


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def _add(a, b, scale=1.):
    return (a[0] + scale * b[0], a[1] + scale * b[1])


def _toi(pa, pb, va, vb):
    r = (pb[0]-pa[0], pb[1]-pa[1])
    w = (vb[0]-va[0], vb[1]-va[1])
    a = _dot(w, w)
    if a == 0.:
        return None
    b = 2 * _dot(r, w)
    c = _dot(r, r) - 1.
    d = b*b - 4*a*c
    if 0 < abs(d) <= 1e-12 * max(1., abs(b*b), abs(4*a*c)):
        raise ValueError('ambiguous_geometry')
    if d < 0:
        return None
    if d == 0.:
        roots = (-b / (2*a),)
    else:
        q = -.5 * (b + math.copysign(math.sqrt(d), b))
        roots = tuple(sorted((q / a, c / q)))
    for t in roots:
        if 0 <= t <= 2.:
            if t <= 1e-12 or 2. - t <= 1e-12:
                raise ValueError('ambiguous horizon event')
            normal = _add(r, w, t)
            distance = math.hypot(*normal)
            n = (normal[0]/distance, normal[1]/distance)
            g = _dot(w, n)
            if g < 0 or d == 0.:
                return (t, n, g, d == 0.)
    return None


def simulate(s: dict):
    validate(s)
    pa = (s['x_a_m'], s['y_a_m'])
    pb = (s['x_b_m'], s['y_b_m'])
    va = (s['vx_a_mps'], s['vy_a_mps'])
    vb = (s['vx_b_mps'], s['vy_b_mps'])
    e = s['restitution']
    hit = _toi(pa, pb, va, vb)
    events = []
    if hit is not None:
        t, n, g, grazing = hit
        ca = _add(pa, va, t)
        cb = _add(pb, vb, t)
        if abs(math.hypot(cb[0]-ca[0], cb[1]-ca[1])-1.) > 1e-9:
            raise ArithmeticError('event contact gap')
        j = 0. if grazing else -(1+e)*g/2.
        aa = _add(va, n, -j)
        bb = _add(vb, n, j)
        event = dict(world_id=s['world_id'], event_index=0, time_s=t,
                     kind='grazing_zero_impulse' if grazing else 'impulse',
                     normal_x=n[0], normal_y=n[1], impulse_ns=j,
                     pre_x_a_m=ca[0], pre_y_a_m=ca[1],
                     pre_x_b_m=cb[0], pre_y_b_m=cb[1],
                     pre_vx_a_mps=va[0], pre_vy_a_mps=va[1],
                     pre_vx_b_mps=vb[0], pre_vy_b_mps=vb[1],
                     post_vx_a_mps=aa[0], post_vy_a_mps=aa[1],
                     post_vx_b_mps=bb[0], post_vy_b_mps=bb[1],
                     restitution=e)
        events.append(event)
    rows = []
    for idx, t in enumerate(SAMPLES):
        if hit is not None and t >= hit[0]:
            te = hit[0]
            qa = _add(_add(pa, va, te), aa, t-te)
            qb = _add(_add(pb, vb, te), bb, t-te)
            ua, ub = aa, bb
        else:
            qa, qb = _add(pa, va, t), _add(pb, vb, t)
            ua, ub = va, vb
        rows.append(dict(world_id=s['world_id'], sample_index=idx, time_s=t,
                         phase='post', x_a_m=qa[0], y_a_m=qa[1],
                         x_b_m=qb[0], y_b_m=qb[1], vx_a_mps=ua[0],
                         vy_a_mps=ua[1], vx_b_mps=ub[0], vy_b_mps=ub[1],
                         total_ke_j=.5*(_dot(ua,ua)+_dot(ub,ub))))
    return rows, events
