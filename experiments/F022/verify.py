"""Independent saved-artifact physics oracle; MUST NOT import soma.f022 or run_suite.

Reconstructs frozen scenario roster and impact dynamics from independently
implemented closest-approach geometry; refuses tampering even after rehash.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

FROZEN = '3984e9dcb2cb420abab5ca92b4d029b31b5173f8'
SCHEMA = 'f022.archive.v1'
ERROR = 1e-9


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_one(p):
    original = p.read_bytes()
    obj = json.loads(original.decode('utf-8'), parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    if original != (canonical(obj)+'\n').encode('utf-8'):
        raise AssertionError(f'noncanonical JSON: {p.name}')
    return obj


def read_lines(p):
    data = p.read_bytes()
    rows = [json.loads(x, parse_constant=lambda y: (_ for _ in ()).throw(ValueError(y)))
            for x in data.decode('utf-8').splitlines()]
    if data != (''.join(canonical(r)+'\n' for r in rows)).encode('utf-8'):
        raise AssertionError(f'noncanonical JSONL: {p.name}')
    return rows


def same(a, b, path='root'):
    if isinstance(a, bool) or isinstance(b, bool) or type(a) is not type(b):
        raise AssertionError(f'{path}: wrong type')
    if isinstance(a, dict):
        if set(a) != set(b):
            raise AssertionError(f'{path}: fields')
        for k in a:
            same(a[k], b[k], f'{path}.{k}')
    elif isinstance(a, list):
        if len(a) != len(b):
            raise AssertionError(f'{path}: row count')
        for i,(aa,bb) in enumerate(zip(a,b)):
            same(aa,bb,f'{path}[{i}]')
    elif type(a) in (int,float):
        if not (math.isfinite(a) and math.isfinite(b)) or abs(a-b)>ERROR*max(1,abs(b)):
            raise AssertionError(f'{path}: expected {b}, got {a}')
    elif a != b:
        raise AssertionError(f'{path}: expected {b}, got {a}')


def expected_roster():
    worlds=[]
    for idx in range(1,14):
        y={3:.6,4:.6,5:1.01,6:.99,7:1.,9:.6,11:.6}.get(idx,0.)
        posA=[-1.,0.];posB=[1.,y]
        velA=[1.,0.];velB=[-1.,0.]
        if idx==8:velA=[-1.,0.];velB=[1.,0.]
        if idx==9:velB=[1.,0.]
        if idx==10:posA=[9.,-7.];posB=[11.,-7.]
        if idx==11:
            posA,posB,velA,velB=([-v[1],v[0]] for v in (posA,posB,velA,velB))
        if idx==12:posA,posB,velA,velB=posB,posA,velB,velA
        if idx==13:posA=[-10.,0.];posB=[10.,0.];velA=[100.,0.];velB=[-100.,0.]
        worlds.append({'world_id':f'C{idx:02d}', 'x_a_m':posA[0], 'y_a_m':posA[1],
                       'x_b_m':posB[0], 'y_b_m':posB[1], 'vx_a_mps':velA[0],
                       'vy_a_mps':velA[1], 'vx_b_mps':velB[0], 'vy_b_mps':velB[1],
                       'mass_a_kg':1.,'mass_b_kg':1.,'radius_a_m':.5,'radius_b_m':.5,
                       'restitution':.5 if idx in (2,4) else 1.,
                       'duration_s':2., 'sample_dt_s':.25})
    return worlds


def oracle(s):
    pa=(s['x_a_m'],s['y_a_m']);pb=(s['x_b_m'],s['y_b_m'])
    va=(s['vx_a_mps'],s['vy_a_mps']);vb=(s['vx_b_mps'],s['vy_b_mps'])
    r=(pb[0]-pa[0],pb[1]-pa[1]);w=(vb[0]-va[0],vb[1]-va[1])
    a=w[0]*w[0]+w[1]*w[1]
    hit=None
    if a:
        closest=-(r[0]*w[0]+r[1]*w[1])/a
        h=(r[0]+w[0]*closest,r[1]+w[1]*closest)
        gap2=1.-(h[0]**2+h[1]**2)
        if gap2>=0. and closest>=0.:
            dt=math.sqrt(gap2/a)
            t=closest-dt
            if 0<t<2.:
                ca=(pa[0]+va[0]*t,pa[1]+va[1]*t)
                cb=(pb[0]+vb[0]*t,pb[1]+vb[1]*t)
                n0=(cb[0]-ca[0],cb[1]-ca[1])
                nn=math.hypot(*n0)
                n=(n0[0]/nn,n0[1]/nn)
                g=w[0]*n[0]+w[1]*n[1]
                graze=gap2==0.
                if g<0 or graze:
                    j=0. if graze else -(1+s['restitution'])*g/2.
                    aa=(va[0]-j*n[0],va[1]-j*n[1])
                    bb=(vb[0]+j*n[0],vb[1]+j*n[1])
                    hit=dict(world_id=s['world_id'],event_index=0,time_s=t,
                             kind='grazing_zero_impulse' if graze else 'impulse',
                             normal_x=n[0],normal_y=n[1],impulse_ns=j,
                             pre_x_a_m=ca[0],pre_y_a_m=ca[1],pre_x_b_m=cb[0],pre_y_b_m=cb[1],
                             pre_vx_a_mps=va[0],pre_vy_a_mps=va[1],
                             pre_vx_b_mps=vb[0],pre_vy_b_mps=vb[1],
                             post_vx_a_mps=aa[0],post_vy_a_mps=aa[1],
                             post_vx_b_mps=bb[0],post_vy_b_mps=bb[1],
                             restitution=s['restitution'])
    frames=[]
    for k in range(9):
        t=k*.25
        if hit is not None and t+1e-12>=hit['time_s']:
            htime=hit['time_s']
            ca=(pa[0]+va[0]*htime,pa[1]+va[1]*htime)
            cb=(pb[0]+vb[0]*htime,pb[1]+vb[1]*htime)
            ua=(hit['post_vx_a_mps'],hit['post_vy_a_mps'])
            ub=(hit['post_vx_b_mps'],hit['post_vy_b_mps'])
            qa=(ca[0]+ua[0]*(t-htime),ca[1]+ua[1]*(t-htime))
            qb=(cb[0]+ub[0]*(t-htime),cb[1]+ub[1]*(t-htime))
        else:
            ua,ub=va,vb
            qa=(pa[0]+va[0]*t,pa[1]+va[1]*t)
            qb=(pb[0]+vb[0]*t,pb[1]+vb[1]*t)
        frames.append(dict(world_id=s['world_id'],sample_index=k,time_s=t,phase='post',
                           x_a_m=qa[0],y_a_m=qa[1],x_b_m=qb[0],y_b_m=qb[1],
                           vx_a_mps=ua[0],vy_a_mps=ua[1],vx_b_mps=ub[0],vy_b_mps=ub[1],
                           total_ke_j=.5*sum(v*v for v in ua+ub)))
    return frames,hit


def verify(root: Path, *, expected_source_sha=None):
    root=Path(root)
    files={'config_sha256':'scenario.json','states_sha256':'states.jsonl',
           'contacts_sha256':'contacts.jsonl','audit_sha256':'audit.json'}
    manifest=read_one(root/'manifest.json')
    if set(manifest)!={'schema_version','frozen_protocol_commit_sha','implementation_commit_sha',
                       'python_version','platform',*files} or manifest['schema_version']!=SCHEMA:
        raise AssertionError('manifest schema')
    if manifest['frozen_protocol_commit_sha']!=FROZEN:
        raise AssertionError('wrong frozen protocol')
    source=manifest['implementation_commit_sha']
    if type(source) is not str or len(source)!=40 or any(c not in '0123456789abcdef' for c in source):
        raise AssertionError('invalid implementation commit')
    if expected_source_sha is not None and source!=expected_source_sha:
        raise AssertionError('wrong implementation SHA')
    for key,name in files.items():
        if manifest[key]!=sha(root/name):
            raise AssertionError(f'{name}: hash mismatch')
    scenario=read_one(root/'scenario.json')
    reference=expected_roster()
    same(scenario,{'schema_version':SCHEMA,'worlds':reference},'frozen scenario')
    states=read_lines(root/'states.jsonl')
    contacts=read_lines(root/'contacts.jsonl')
    predicted_frames=[];predicted_events=[];result=[]
    for scene in reference:
        f,e=oracle(scene)
        predicted_frames.extend(f)
        if e is not None: predicted_events.append(e)
        initial_ke=.5*sum(scene[k]**2 for k in
                            ('vx_a_mps','vy_a_mps','vx_b_mps','vy_b_mps'))
        result.append({'world_id':scene['world_id'],
                       'contact_count':int(e is not None),
                       'classification':e['kind'] if e else 'none',
                       'ke_before_j':initial_ke,'ke_after_j':f[-1]['total_ke_j']})
    same(states,predicted_frames,'saved states')
    same(contacts,predicted_events,'saved contacts')
    audit=read_one(root/'audit.json')
    same(audit,{'schema_version':SCHEMA,'world_results':result,
                'invalid_probe_results':{f'J{i:02d}':'rejected' for i in range(1,6)}},'audit')
    # Fixed analytical canaries independent of producer; no silently shifted physics.
    contact={e['world_id']:e for e in contacts}
    if not math.isclose(contact['C13']['time_s'],.095,abs_tol=1e-9):
        raise AssertionError('C13 missing high-speed TOI')
    for world,impulse,ke in [('C03',1.6,1.),('C04',1.2,.52)]:
        if not math.isclose(contact[world]['impulse_ns'],impulse,abs_tol=1e-9):
            raise AssertionError('frozen analytic impulse wrong')
        if not math.isclose(next(x for x in result if x['world_id']==world)['ke_after_j'],ke,abs_tol=1e-9):
            raise AssertionError('frozen analytic energy wrong')
    if contact['C07']['kind']!='grazing_zero_impulse' or contact['C07']['impulse_ns']!=0.:
        raise AssertionError('tangent event wrong')
    return {'worlds':len(reference),'states':len(states),'contacts':len(contacts),
            'invalid_probes':5,'verified':'independent_analytic_saved_data'}


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--expected-source-sha',default=None)
    args=p.parse_args()
    print(canonical(verify(args.root,expected_source_sha=args.expected_source_sha)))
