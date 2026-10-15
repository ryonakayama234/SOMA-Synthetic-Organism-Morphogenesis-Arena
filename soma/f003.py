"""F003: two 1D cells and a massless, ideal rigid link (research world truth)."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from decimal import Decimal
from pathlib import Path
import csv
import hashlib
import json
import math
import subprocess
from typing import Any
from xml.sax.saxutils import escape
from soma.f001 import step as f001_step

SCHEMA = "f003.v1"
STATE_COLUMNS = ("time_s","attached","x_a_m","x_b_m","v_a_m_s","v_b_m_s",
 "force_a_n","force_b_n","link_force_a_n","link_force_b_n",
 "distance_constraint_error_m","velocity_constraint_error_m_s",
 "center_of_mass_m","center_of_mass_velocity_m_s")
EVENT_COLUMNS = ("time_s","kind","attached_before","attached_after",
 "x_a_before_m","x_a_after_m","x_b_before_m","x_b_after_m",
 "v_a_before_m_s","v_a_after_m_s","v_b_before_m_s","v_b_after_m_s",
 "link_force_before_n")

def numeric(value, name, positive=False, nonnegative=False):
    if type(value) not in (int,float) or not math.isfinite(value):
        raise ValueError(f"{name}: finite real number required")
    v=float(value)
    if positive and v<=0: raise ValueError(f"{name}: must be positive")
    if nonnegative and v<0: raise ValueError(f"{name}: must not be negative")
    return v

def steps_for(time, dt, name):
    n=Decimal(str(time))/Decimal(str(dt))
    if n!=n.to_integral_value(): raise ValueError(f"{name}: not an exact decimal multiple of dt_s")
    return int(n)

def exact_keys(row, expected, label):
    if not isinstance(row,dict) or set(row)!=set(expected):
        raise ValueError(f"{label}: expected exactly {sorted(expected)}")
    return row

def xml_safe(value):
    return all(c in ("\t","\n","\r") or
               (0x20<=ord(c)<=0xD7FF) or (0xE000<=ord(c)<=0xFFFD) or
               (0x10000<=ord(c)<=0x10FFFF) for c in value)

@dataclass(frozen=True)
class Cell:
    id: str
    mass_kg: float
    initial_x_m: float
    initial_v_m_s: float
    force_n: float

@dataclass(frozen=True)
class Config:
    experiment_id: str
    dt_s: float
    duration_s: float
    drag_per_s: float
    cells: tuple[Cell,Cell]
    initially_attached: bool
    length_m: float
    detach_time_s: float|None
    steps: int
    detach_step: int|None

    @classmethod
    def from_dict(cls, raw):
        d=exact_keys(raw, ("schema_version","experiment_id","seed","dt_s",
          "duration_s","drag_per_s","cells","link"),"config")
        if d["schema_version"]!=SCHEMA or d["seed"] is not None:
            raise ValueError("unsupported schema or non-null seed")
        name=d["experiment_id"]
        if type(name) is not str or not 1<=len(name)<=120 or not xml_safe(name):
            raise ValueError("invalid XML experiment_id")
        dt=numeric(d["dt_s"],"dt_s",positive=True)
        duration=numeric(d["duration_s"],"duration_s",positive=True)
        drag=numeric(d["drag_per_s"],"drag_per_s",nonnegative=True)
        if dt*drag>1: raise ValueError("unstable dt_s * drag_per_s")
        count=steps_for(duration,dt,"duration_s")
        if not 1<=count<=1000000: raise ValueError("step count out of range")
        if type(d["cells"]) is not list or len(d["cells"])!=2:
            raise ValueError("exactly two cells required")
        cells=[]
        for i,raw_cell in enumerate(d["cells"]):
            c=exact_keys(raw_cell, ("id","mass_kg","initial_x_m","initial_v_m_s","force_n"),"cell")
            if c["id"]!=("A" if i==0 else "B"): raise ValueError("ordered cell IDs A,B required")
            cells.append(Cell(c["id"],numeric(c["mass_kg"],"mass",positive=True),
                numeric(c["initial_x_m"],"x"), numeric(c["initial_v_m_s"],"v"),
                numeric(c["force_n"],"force")))
        link=exact_keys(d["link"], ("initially_attached","length_m","detach_time_s"),"link")
        if type(link["initially_attached"]) is not bool: raise ValueError("link flag must be boolean")
        length=numeric(link["length_m"],"length_m",positive=True)
        cut=link["detach_time_s"]
        if cut is None: cut_step=None
        else:
            cut=numeric(cut,"detach_time_s")
            if not link["initially_attached"] or not 0<cut<duration:
                raise ValueError("cut must be inside an attached run")
            cut_step=steps_for(cut,dt,"detach_time_s")
        if link["initially_attached"]:
            a,b=cells
            if b.initial_x_m-a.initial_x_m!=length or a.initial_v_m_s!=b.initial_v_m_s:
                raise ValueError("initial rigid constraint inconsistent; no silent snap")
        return cls(name,dt,duration,drag,(cells[0],cells[1]),
                   link["initially_attached"],length,cut,count,cut_step)

    @classmethod
    def from_json(cls,path: Path):
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def to_dict(self):
        return dict(schema_version=SCHEMA,experiment_id=self.experiment_id,seed=None,
          dt_s=self.dt_s,duration_s=self.duration_s,drag_per_s=self.drag_per_s,
          cells=[asdict(c) for c in self.cells],
          link=dict(initially_attached=self.initially_attached,length_m=self.length_m,
                    detach_time_s=self.detach_time_s))

def link_forces(cfg):
    a,b=cfg.cells
    fb=b.mass_kg*(a.force_n+b.force_n)/(a.mass_kg+b.mass_kg)-b.force_n
    return -fb,fb

def snapshot(cfg,k,xa,xb,va,vb,attached):
    a,b=cfg.cells
    ta,tb=link_forces(cfg) if attached else (0.,0.)
    total=a.mass_kg+b.mass_kg
    return dict(time_s=k*cfg.dt_s,attached=attached,x_a_m=xa,x_b_m=xb,
      v_a_m_s=va,v_b_m_s=vb,force_a_n=a.force_n,force_b_n=b.force_n,
      link_force_a_n=ta,link_force_b_n=tb,
      distance_constraint_error_m=(xb-xa-cfg.length_m) if attached else None,
      velocity_constraint_error_m_s=(vb-va) if attached else None,
      center_of_mass_m=(a.mass_kg*xa+b.mass_kg*xb)/total,
      center_of_mass_velocity_m_s=(a.mass_kg*va+b.mass_kg*vb)/total)

def event(t,kind,attached_before,attached_after,xa,xb,va,vb,before_force):
    return dict(time_s=t,kind=kind,attached_before=attached_before,
      attached_after=attached_after,x_a_before_m=xa,x_a_after_m=xa,
      x_b_before_m=xb,x_b_after_m=xb,v_a_before_m_s=va,v_a_after_m_s=va,
      v_b_before_m_s=vb,v_b_after_m_s=vb,link_force_before_n=before_force)

def simulate(cfg):
    a,b=cfg.cells
    xa,xb,va,vb=a.initial_x_m,b.initial_x_m,a.initial_v_m_s,b.initial_v_m_s
    attached=cfg.initially_attached
    events=[event(0.,"attach_initial",False,True,xa,xb,va,vb,0.)] if attached else []
    rows=[snapshot(cfg,0,xa,xb,va,vb,attached)]
    for k in range(1,cfg.steps+1):
        if attached:
            nx,nv=f001_step(xa,va,mass_kg=a.mass_kg+b.mass_kg,
                drag_per_s=cfg.drag_per_s,force_n=a.force_n+b.force_n,dt_s=cfg.dt_s)
            dx=nx-xa
            xa=nx
            xb+=dx
            va=vb=nv
        else:
            xa,va=f001_step(xa,va,mass_kg=a.mass_kg,
                drag_per_s=cfg.drag_per_s,force_n=a.force_n,dt_s=cfg.dt_s)
            xb,vb=f001_step(xb,vb,mass_kg=b.mass_kg,
                drag_per_s=cfg.drag_per_s,force_n=b.force_n,dt_s=cfg.dt_s)
        if not all(map(math.isfinite,(xa,xb,va,vb))):
            raise ValueError("non-finite world state")
        if attached and k==cfg.detach_step:
            events.append(event(k*cfg.dt_s,"detach",True,False,
                                xa,xb,va,vb,link_forces(cfg)[1]))
            attached=False
        rows.append(snapshot(cfg,k,xa,xb,va,vb,attached))
    return rows,events

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def provenance():
    root=Path(__file__).resolve().parent.parent
    try:
        commit=subprocess.run(["git","-C",str(root),"rev-parse","HEAD"],
                 check=True,capture_output=True,text=True,timeout=3).stdout.strip()
        dirty=bool(subprocess.run(["git","-C",str(root),"status","--porcelain"],
                 check=True,capture_output=True,text=True,timeout=3).stdout.strip())
    except (OSError,subprocess.SubprocessError):
        commit,dirty=None,None
    return dict(git_commit=commit,git_dirty=dirty,module_sha256=sha(Path(__file__)))

def plot_svg(rows,title):
    values=[r[f] for r in rows for f in ("x_a_m","x_b_m")]
    lo,hi=min(values),max(values)
    span=hi-lo or 1.
    stride=max(1,(len(rows)-1)//500)
    sampled=rows[::stride]
    if sampled[-1] is not rows[-1]: sampled.append(rows[-1])
    paths=[]
    for field,color in (("x_a_m","#2563eb"),("x_b_m","#059669")):
        points=" ".join(f"{70+590*r['time_s']/rows[-1]['time_s']:.2f},"
          f"{200-150*(r[field]-lo)/span:.2f}" for r in sampled)
        paths.append(f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{points}"/>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="720" height="250" viewBox="0 0 720 250">'
      '<rect width="720" height="250" fill="white"/><g font-family="Arial" fill="#334155">'
      f'<text x="70" y="25" font-size="16">{escape(title)}: A blue / B green</text>'
      '<path d="M70 40V200H660" fill="none" stroke="#888"/>'+''.join(paths)+'</g></svg>')

def save_run(cfg,path,*,provenance_data=None,suite_sha256=None):
    rows,events=simulate(cfg)  # no files until successful simulation
    identity=provenance_data if provenance_data is not None else provenance()
    path.mkdir(parents=True,exist_ok=False)
    (path/"config.json").write_text(json.dumps(cfg.to_dict(),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for fname,columns,data in (("states.csv",STATE_COLUMNS,rows),("events.csv",EVENT_COLUMNS,events)):
        with (path/fname).open("w",newline="",encoding="utf-8") as file:
            writer=csv.DictWriter(file,fieldnames=columns)
            writer.writeheader()
            writer.writerows(data)
    (path/"motion.svg").write_text(plot_svg(rows,cfg.experiment_id),encoding="utf-8")
    info=dict(schema_version=SCHEMA,experiment_id=cfg.experiment_id,
      model="1d_two_cell_ideal_link",integration="semi_implicit_euler",
      seed=None,seed_note="no randomness",samples=len(rows),events=len(events),
      **identity,suite_sha256=suite_sha256,
      artifacts={n:sha(path/n) for n in ("config.json","states.csv","events.csv","motion.svg")})
    (path/"manifest.json").write_text(json.dumps(info,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return info
