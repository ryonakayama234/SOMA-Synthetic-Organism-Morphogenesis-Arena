"""F002: deterministic, integer-microjoule accounting; NOT a powertrain model.

No motion model, physical connector, agent policy or battery electrochemistry lives here.
State is immutable, and rejected transactions cannot mutate any prior state.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any
from xml.sax.saxutils import escape

SCHEMA_VERSION = "f002.v1"
UJ_PER_J = 1_000_000
MAX_UJ = 10**15
MAX_CELLS = 100
MAX_EVENTS = 10_000
BPS_DENOM = 10_000
EVENT_COLUMNS = (
    "event_index", "kind", "source_id", "target_id", "amount_uj",
    "eta_bps", "received_uj", "loss_uj", "external_in_uj",
    "external_out_uj", "residual_uj",
)
BALANCE_COLUMNS = ("event_index", "cell_id", "balance_uj", "capacity_uj")


def _positive_int(value: object, name: str) -> int:
    if type(value) is not int or not 0 < value <= MAX_UJ:
        raise ValueError(f"{name} must be an integer in [1, {MAX_UJ}]")
    return value


def _cell_id(value: object) -> str:
    if not isinstance(value, str) or not value or len(value) > 80 or not value.isascii() or not all(ch.isalnum() or ch in "_-" for ch in value):
        raise ValueError("cell_id must have 1-80 ASCII letters, digits, '-' or '_'")
    return value


@dataclass(frozen=True)
class Cell:
    cell_id: str
    capacity_uj: int
    balance_uj: int

    def __post_init__(self) -> None:
        _cell_id(self.cell_id)
        _positive_int(self.capacity_uj, "capacity_uj")
        if type(self.balance_uj) is not int or not 0 <= self.balance_uj <= self.capacity_uj:
            raise ValueError("balance_uj must be an integer in [0, capacity_uj]")


@dataclass(frozen=True)
class LedgerState:
    cells: tuple[Cell, ...]
    initial_total_uj: int
    acquired_uj: int = 0
    spent_uj: int = 0
    loss_uj: int = 0
    event_index: int = 0

    def __post_init__(self) -> None:
        if not 1 <= len(self.cells) <= MAX_CELLS:
            raise ValueError("invalid cell count")
        ids = [c.cell_id for c in self.cells]
        if ids != sorted(set(ids)):
            raise ValueError("cells must have unique ids sorted ascending")
        for name in ("initial_total_uj", "acquired_uj", "spent_uj", "loss_uj", "event_index"):
            if type(getattr(self, name)) is not int or getattr(self, name) < 0:
                raise ValueError(f"{name} must be a nonnegative integer")
        if self.residual_uj != 0:
            raise ValueError(f"ledger conservation failed: residual {self.residual_uj} µJ")

    @property
    def residual_uj(self) -> int:
        return self.initial_total_uj + self.acquired_uj - (
            sum(c.balance_uj for c in self.cells) + self.spent_uj + self.loss_uj
        )

    def cell(self, cell_id: str) -> Cell:
        for cell in self.cells:
            if cell.cell_id == cell_id:
                return cell
        raise ValueError(f"unknown cell_id: {cell_id}")


def new_ledger(cells: list[Cell]) -> LedgerState:
    ordered = tuple(sorted(cells, key=lambda x: x.cell_id))
    return LedgerState(ordered, sum(c.balance_uj for c in ordered))


@dataclass(frozen=True)
class Event:
    kind: str
    amount_uj: int
    source_id: str | None = None
    target_id: str | None = None
    eta_bps: int | None = None


@dataclass(frozen=True)
class Entry:
    event_index: int
    kind: str
    source_id: str | None
    target_id: str | None
    amount_uj: int
    eta_bps: int | None
    received_uj: int
    loss_uj: int
    external_in_uj: int
    external_out_uj: int
    residual_uj: int


def apply_event(state: LedgerState, event: Event) -> tuple[LedgerState, Entry]:
    """Validate then atomically return *new* immutable state and accounting entry."""
    amount = _positive_int(event.amount_uj, "amount_uj")
    kind = event.kind
    if kind not in ("acquire", "spend", "transfer"):
        raise ValueError("kind must be acquire/spend/transfer")
    if kind == "acquire":
        if event.source_id is not None or event.target_id is None or event.eta_bps is not None:
            raise ValueError("acquire requires target_id only")
    elif kind == "spend":
        if event.target_id is not None or event.source_id is None or event.eta_bps is not None:
            raise ValueError("spend requires source_id only")
    elif kind == "transfer":
        if event.source_id is None or event.target_id is None or event.source_id == event.target_id:
            raise ValueError("transfer requires two distinct cells")
        if type(event.eta_bps) is not int or not 0 <= event.eta_bps <= BPS_DENOM:
            raise ValueError("eta_bps must be an integer in [0, 10000]")
    source = state.cell(_cell_id(event.source_id)) if event.source_id is not None else None
    target = state.cell(_cell_id(event.target_id)) if event.target_id is not None else None
    received = amount * event.eta_bps // BPS_DENOM if kind == "transfer" else 0
    loss = amount - received if kind == "transfer" else 0
    incoming = amount if kind == "acquire" else 0
    outgoing = amount if kind == "spend" else 0
    if source is not None and source.balance_uj < amount:
        raise ValueError("insufficient balance")
    if target is not None and target.balance_uj + (received if kind == "transfer" else amount) > target.capacity_uj:
        raise ValueError("target capacity exceeded")
    next_cells = tuple(
        Cell(c.cell_id, c.capacity_uj,
             c.balance_uj - (amount if source is not None and c.cell_id == source.cell_id else 0)
             + ((received if kind == "transfer" else amount) if target is not None and c.cell_id == target.cell_id else 0))
        for c in state.cells
    )
    next_state = LedgerState(
        cells=next_cells, initial_total_uj=state.initial_total_uj,
        acquired_uj=state.acquired_uj + incoming,
        spent_uj=state.spent_uj + outgoing,
        loss_uj=state.loss_uj + loss,
        event_index=state.event_index + 1,
    )
    entry = Entry(next_state.event_index, kind, event.source_id, event.target_id,
                  amount, event.eta_bps, received, loss, incoming, outgoing,
                  next_state.residual_uj)
    return next_state, entry


def _exact_keys(obj: object, required: set[str], optional: set[str] = frozenset()) -> dict[str, Any]:
    if not isinstance(obj, dict) or required - obj.keys() or obj.keys() - (required | optional):
        raise ValueError(f"fields must be exactly {sorted(required)} plus optional {sorted(optional)}")
    return obj


def parse_config(config: object) -> tuple[LedgerState, list[Event]]:
    c = _exact_keys(config, {"schema_version", "experiment_id", "seed", "cells", "events"})
    if c["schema_version"] != SCHEMA_VERSION or not isinstance(c["experiment_id"], str) or not c["experiment_id"] or len(c["experiment_id"]) > 120:
        raise ValueError("invalid schema_version or experiment_id")
    if type(c["seed"]) is not int:
        raise ValueError("seed must be integer")
    if not isinstance(c["cells"], list) or not 1 <= len(c["cells"]) <= MAX_CELLS:
        raise ValueError("invalid cells list")
    if not isinstance(c["events"], list) or len(c["events"]) > MAX_EVENTS:
        raise ValueError("invalid events list")
    cells = [Cell(**_exact_keys(x, {"cell_id", "capacity_uj", "balance_uj"})) for x in c["cells"]]
    events = [Event(**_exact_keys(x, {"kind", "amount_uj"}, {"source_id", "target_id", "eta_bps"})) for x in c["events"]]
    return new_ledger(cells), events


def run(config: dict[str, Any]) -> tuple[LedgerState, list[Entry], list[LedgerState]]:
    state, events = parse_config(config)
    snapshots = [state]
    entries = []
    for event in events:
        state, entry = apply_event(state, event)
        entries.append(entry)
        snapshots.append(state)
    return state, entries, snapshots


def _git_revision() -> str | None:
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], text=True, capture_output=True, check=True, timeout=2)
        return result.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plot_svg(snapshots: list[LedgerState], experiment_id: str) -> str:
    """Human inspection only; CSV integer values are the authoritative evidence."""
    cells = snapshots[0].cells
    highest = max(c.capacity_uj for c in cells)
    height = 95 + len(cells) * 44
    chunks = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 {height}" width="640" height="{height}">',
              '<rect width="100%" height="100%" fill="white"/>',
              '<g font-family="Arial,sans-serif" fill="#273449">',
              f'<text x="20" y="30" font-size="18">{escape(experiment_id)}: stored energy [J]</text>',
              '<text x="265" y="52" font-size="12">initial (gray) / final (blue)</text>']
    for i, c in enumerate(cells):
        final = snapshots[-1].cell(c.cell_id)
        y = 72 + 44 * i
        chunks.append(f'<text x="20" y="{y+16}" font-size="13">{escape(c.cell_id)}</text>')
        chunks.append(f'<rect x="110" y="{y}" width="{450*c.balance_uj/highest:.3f}" height="10" fill="#9ca3af"/>')
        chunks.append(f'<rect x="110" y="{y+12}" width="{450*final.balance_uj/highest:.3f}" height="10" fill="#2563eb"/>')
        chunks.append(f'<text x="570" y="{y+19}" font-size="10">{final.balance_uj / UJ_PER_J:g}</text>')
    chunks.append('</g></svg>')
    return "".join(chunks)


def save_run(config: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    state, entries, snapshots = run(config)  # Validate before creating directory.
    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / "config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (output_dir / "events.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, EVENT_COLUMNS)
        w.writeheader()
        w.writerows(asdict(entry) for entry in entries)
    with (output_dir / "balances.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(BALANCE_COLUMNS)
        for snapshot in snapshots:
            for cell in snapshot.cells:
                w.writerow((snapshot.event_index, cell.cell_id, cell.balance_uj, cell.capacity_uj))
    (output_dir / "energy.svg").write_text(plot_svg(snapshots, config["experiment_id"]), encoding="utf-8")
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": config["experiment_id"],
        "model": "integer_microjoule_ledger",
        "python_code_git_commit": _git_revision(),
        "seed": config["seed"],
        "seed_note": "no randomness in this experiment",
        "event_count": len(entries),
        "final_balances_uj": {c.cell_id: c.balance_uj for c in state.cells},
        "acquired_uj": state.acquired_uj,
        "spent_uj": state.spent_uj,
        "loss_uj": state.loss_uj,
        "residual_uj": state.residual_uj,
        "artifacts": {name: _sha256(output_dir / name) for name in ("config.json", "events.csv", "balances.csv", "energy.svg")},
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="SOMA F002 energy accounting experiment")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    manifest = save_run(config, args.output_dir)
    print(json.dumps({"output_dir": str(args.output_dir), "residual_uj": manifest["residual_uj"], "final_balances_uj": manifest["final_balances_uj"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
