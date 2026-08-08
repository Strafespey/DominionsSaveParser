"""Per-battle report for a turn file: order of battle, stats, and losses.

    py scripts/battle_report.py <GameName>
    py scripts/battle_report.py <path-to-.trn>
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dom6 import find_save_root, load, load_savegame  # noqa: E402
from dom6.analysis import battle_outcomes  # noqa: E402

_M = None
_W = None
_N: dict[int, str] = {}


def tables():
    global _M, _W, _N
    if _M is None:
        try:
            from dom6.gamedata import monsters, weapons

            _M, _W = monsters(), weapons()
        except Exception:  # noqa: BLE001 - game data is optional
            _M, _W = False, False
        try:
            from dom6.engine import Engine

            _N = Engine().list_nations()
        except Exception:  # noqa: BLE001
            _N = {}
    return _M, _W


def nation(n: int) -> str:
    if n == 0:
        return "Independents"
    return _N.get(n, f"nation {n}").split(",")[0]


def unit_line(type_id: int, count: int, indent: str) -> list[str]:
    m, w = tables()
    if not m:
        return [f"{indent}{count:4d} x type {type_id}"]
    mon = m.get(type_id)
    if not mon:
        return [f"{indent}{count:4d} x type {type_id}"]
    mor = "MINDLESS" if mon.is_mindless else f"mor{mon.morale}"
    arms = []
    for x in m.weapons_of(type_id, w) if w else []:
        arms.append(
            f"{x.name} rng {x.range}" if x.is_missile
            else f"{x.name} len {x.effective_length}"
        )
    return [
        f"{indent}{count:4d} x {mon.name}",
        f"{indent}       hp{mon.hp} sz{mon.size} prot{mon.protection} "
        f"att{mon.attack} def{mon.defence} {mor}"
        + (f" | {', '.join(arms)}" if arms else ""),
    ]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target")
    args = ap.parse_args()

    p = Path(args.target)
    if not p.is_file():
        root = find_save_root()
        cand = (root / args.target) if root else None
        if not cand or not cand.is_dir():
            print(f"not found: {args.target}")
            return 1
        sg = load_savegame(cand)
        if not sg.turn_files:
            print(f"no .trn in {cand}")
            return 1
        p = sg.turn_files[0]

    save = load(p)
    tables()
    print(f"{p.name}: turn {save.header.turn}, "
          f"{nation(save.header.nation)}, {save.battle_count} battle(s)")

    for oc in battle_outcomes(save):
        b = oc.battle
        print(f"\n=== {b.battlefield} — "
              f"{' vs '.join(nation(n) for n in b.nations)} ===")
        for side in oc.sides:
            mark = " (you)" if side.observable else ""
            print(f"\n  {nation(side.nation)}{mark}: {len(side.engaged)} engaged, "
                  f"{side.survived} survived, {len(side.lost)} lost "
                  f"({side.loss_fraction:.0%})")
            if side.caveat:
                print(f"    note: {side.caveat}")
            squads: dict[int, list] = {}
            for u in side.engaged:
                squads.setdefault(u.link, []).append(u)
            for sid, members in sorted(squads.items()):
                pos = members[0].position
                tag = "commanders" if sid == 0xFFFF else f"squad {sid}"
                at = f" at {pos}" if pos else ""
                print(f"    {tag} ({len(members)}){at}")
                for t, n in Counter(u.type_id for u in members).most_common():
                    for line in unit_line(t, n, "      "):
                        print(line)
            if side.lost:
                print("    losses:")
                m, _ = tables()
                for t, n in side.losses_by_type.most_common():
                    label = m.label(t) if m else f"type {t}"
                    print(f"      -{n:3d} {label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
