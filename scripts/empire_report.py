"""Empire-level report: provinces, forts, income, gems, research, dominion.

Reads the score-graph history that every save carries, so it needs no hosting
and reveals nothing the player cannot already see in their own score graphs.

    py scripts/empire_report.py <GameName>
    py scripts/empire_report.py <path-to-.trn>
    py scripts/empire_report.py <GameName> --history      # your turn-by-turn trend
    py scripts/empire_report.py <GameName> --metric income
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dom6 import find_save_root, load, load_savegame  # noqa: E402
from dom6.scores import history_for, latest_by_nation  # noqa: E402

METRICS = [
    ("provinces", "prov", 6),
    ("forts", "forts", 6),
    ("income", "gold/t", 8),
    ("gem_income", "gems/t", 8),
    ("research", "res/t", 7),
    ("dominion", "dom", 6),
    ("army_size", "army", 7),
]


def nation_names() -> dict[int, str]:
    try:
        from dom6.engine import Engine

        return {i: n.split(",")[0] for i, n in Engine().list_nations().items()}
    except Exception:  # noqa: BLE001 - the engine is optional
        return {}


def resolve(target: str) -> Path | None:
    p = Path(target)
    if p.is_file():
        return p
    root = find_save_root()
    folder = (root / target) if root else None
    if not folder or not folder.is_dir():
        return None
    sg = load_savegame(folder)
    if sg.turn_files:
        return sg.turn_files[0]
    return sg.ftherlnd


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target", help="game name or path to a .trn / ftherlnd")
    ap.add_argument("--history", action="store_true",
                    help="turn-by-turn history for the file's own nation")
    ap.add_argument("--metric", help="one metric, all nations, turn by turn")
    args = ap.parse_args()

    path = resolve(args.target)
    if path is None:
        print(f"not found: {args.target}")
        return 1

    save = load(path)
    records = save.scores()
    if not records:
        print(f"{path.name}: no score history in this file "
              "(.2h order files do not carry one)")
        return 1

    names = nation_names()
    newest = max(r.turn for r in records)
    me = save.header.nation

    def label(nid: int) -> str:
        name = names.get(nid, f"nation {nid}")
        return f"{name}*" if nid == me else name

    print(f"{path.name}: turn {save.header.turn}, "
          f"scores through turn {newest}"
          + (f", playing {names.get(me, me)}" if me >= 0 else ""))
    print("(the newest score row lags the turn number by one -- it is written "
          "when the host generates the next turn)\n")

    if args.metric:
        return trend_table(records, args.metric, label, newest)
    if args.history:
        return own_history(records, me, label)

    header = "  " + f"{'nation':<14}" + "".join(f"{h:>{w}}" for _, h, w in METRICS)
    print(header)
    print("  " + "-" * (len(header) - 2))
    latest = latest_by_nation(records)
    for nid, rec in sorted(latest.items(), key=lambda kv: -kv[1].provinces):
        row = "".join(f"{getattr(rec, attr):>{w}}" for attr, _, w in METRICS)
        print(f"  {label(nid):<14}{row}")
    print("\n  * = the nation whose turn file this is")
    return 0


def own_history(records, me, label) -> int:
    rows = history_for(records, me)
    if not rows:
        print("this file has no history for its own nation")
        return 1
    print(f"  {label(me)} turn by turn")
    header = "  " + f"{'turn':<6}" + "".join(f"{h:>{w}}" for _, h, w in METRICS)
    print(header)
    print("  " + "-" * (len(header) - 2))
    for rec in rows:
        row = "".join(f"{getattr(rec, attr):>{w}}" for attr, _, w in METRICS)
        print(f"  {rec.turn:<6}{row}")
    return 0


def trend_table(records, metric, label, newest) -> int:
    valid = [attr for attr, _, _ in METRICS]
    if metric not in valid:
        print(f"unknown metric {metric!r}; pick one of {', '.join(valid)}")
        return 1
    nations = sorted({r.nation for r in records})
    print(f"  {metric} by turn\n")
    print("  turn  " + "".join(f"{label(n):>13}" for n in nations))
    for turn in range(min(r.turn for r in records), newest + 1):
        cells = []
        for n in nations:
            rec = next((r for r in records if r.nation == n and r.turn == turn), None)
            cells.append(f"{getattr(rec, metric) if rec else '-':>13}")
        print(f"  {turn:<6}" + "".join(cells))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
