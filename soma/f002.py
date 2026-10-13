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


def _xml10_safe(value: str) -> bool:
    """XML 1.0 Char production: other controls, surrogates and U+FFFE/U+FFFF are forbidden.

    xml.sax.saxutils.escape only escapes XML markup; it does not filter invalid chars.
    """
    return all(
        ord(ch) in (0x09, 0x0A, 0x0D)
        or 0x20 <= ord(ch) <= 0xD7FF
        or 0xE000 <= ord(ch) <= 0xFFFD
        or 0x10000 <= ord(ch) <= 0x10FFFF
        for ch in value
    )


def parse_config(config: object) -> tuple[LedgerState, list[Event]]:
    c = _exact_keys(config, {"schema_version", "experiment_id", "seed", "cells", "events"})
    experiment_id = c["experiment_id"]
    if (c["schema_version"] != SCHEMA_VERSION or not isinstance(experiment_id, str)
            or not experiment_id or len(experiment_id) > 120
            or not _xml10_safe(experiment_id)):
        raise ValueError("invalid schema_version or experiment_id (XML 1.0 characters required)")
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


def _git_provenance() -> tuple[str | None, bool | None]:
    """Find the Git repo that owns THIS module, not the caller's cwd.

    A dirty checkout is recorded explicitly; SHA alone does not identify modified code.
    Generated runs/ are excluded by the repository's .gitignore.
    """
    root = Path(__file__).resolve().parents[1]
    try:
        def git(*args: str) -> str:
            return subprocess.run(
                ["git", "-C", str(root), *args], text=True, capture_output=True,
                check=True, timeout=3,
            ).stdout.strip()

        if Path(git("rev-parse", "--show-toplevel")).resolve() != root:
            return None, None
        return git("rev-parse", "HEAD"), bool(git("status", "--porcelain", "--untracked-files=all"))
    except (OSError, subprocess.SubprocessError, ValueError):
        return None, None


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def plot_svg(snapshots: list[LedgerState], experiment_id: str) -> str:
    """Show the event-time trace AND the accounted disposition of energy.

    This is an inspection aid; integer CSV/manifest values remain the evidence.
    For large runs, limit plot points to roughly 400; the CSV retains every event.
    """
    final = snapshots[-1]
    n = len(snapshots) - 1
    width = 850
    shown = min(len(snapshots), 9)
    height = 420 + 21 * shown
    palette = ("#2563eb", "#dc2626", "#059669", "#7c3aed", "#d97706")
    top, plot_bottom, left, right = 98, 280, 94, 785
    ceiling = max(c.capacity_uj for c in final.cells)
    sampled = sorted(set([0, n] + list(range(0, n + 1, max(1, n // 400)))))
    chunks = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
              '<rect width="100%" height="100%" fill="white"/>',
              '<g font-family="Arial,sans-serif" fill="#243044">',
              f'<text x="18" y="28" font-size="18">{escape(experiment_id)}: energy ledger</text>',
              '<text x="18" y="50" font-size="13">Cell balances by accepted event; units: microjoules (µJ)</text>',
              f'<path d="M {left} {top} V {plot_bottom} H {right}" fill="none" stroke="#64748b"/>',
              f'<text x="18" y="{top+10}" font-size="12">{ceiling}</text>',
              f'<text x="{left-10}" y="{plot_bottom+17}" font-size="12">0</text>',
              f'<text x="{right-55}" y="{plot_bottom+17}" font-size="12">event {n}</text>']
    for j, cell in enumerate(final.cells):
        color = palette[j % len(palette)]
        points = " ".join(
            f"{left + (right-left)*idx/max(1,n):.3f},{plot_bottom-(plot_bottom-top)*snapshots[idx].cell(cell.cell_id).balance_uj/ceiling:.3f}"
            for idx in sampled
        )
        if n == 0:
            points += " " + points
        chunks.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2"/>')
        if j < 8:
            chunks.append(f'<text x="{left+(j%4)*174}" y="{65+(j//4)*16}" font-size="12" fill="{color}">'
                          f'{escape(cell.cell_id)}: {cell.balance_uj} µJ</text>')
    # Integer accounting closure in the same diagram, not an inferred physical energy.
    total = sum(c.balance_uj for c in final.cells)
    chunks.extend([
        '<text x="18" y="331" font-size="14">Accounting breakdown (microjoules)</text>',
        f'<text x="18" y="353" font-size="12">Initial stores: {final.initial_total_uj} + external acquired: {final.acquired_uj}</text>',
        f'<text x="18" y="371" font-size="12">= final stores: {total} + spent: {final.spent_uj} + transfer loss: {final.loss_uj}</text>',
        f'<text x="18" y="389" font-size="12">Conservation residual: {final.residual_uj} microjoules</text>',
        '<text x="18" y="416" font-size="12">Exact event trace (first 8 snapshots, full trace in balances.csv):</text>',
    ])
    for k, state in enumerate(snapshots[:shown]):
        row = ", ".join(f"{c.cell_id}={c.balance_uj}" for c in state.cells[:5])
        suffix = " ..." if len(state.cells) > 5 else ""
        chunks.append(f'<text x="18" y="{438+21*k}" font-size="12">event {state.event_index}: {escape(row)}{suffix}; loss={state.loss_uj}</text>')
    chunks.append("</g></svg>")
    return "".join(chunks)

def save_run(config: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    state, entries, snapshots = run(config)  # Validate before creating directory.
    revision, dirty = _git_provenance()  # Snapshot provenance before writing artifacts.
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
        "python_code_git_commit": revision,
        "python_code_git_dirty": dirty,
        "python_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
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
