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
_A = None
_N: dict[int, str] = {}


def tables():
    global _M, _W, _A, _N
    if _M is None:
        try:
            from dom6.gamedata import armours, monsters, weapons

            _M, _W, _A = monsters(), weapons(), armours()
        except Exception:  # noqa: BLE001 - game data is optional
            _M, _W, _A = False, False, False
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


def held_by(save, battlefield: str | None) -> str:
    """Who holds the province after the turn -- the only real outcome signal.

    Inferred casualties cannot decide a battle: enemy survivors are invisible
    in a turn file, so a defeat reads as enemy annihilation. Province ownership
    is read from the save instead. It can be unknown, and says so.
    """
    from dom6.provinces import INDEPENDENT, owner_of

    owner = owner_of(save, battlefield) if battlefield else None
    if owner is None:
        return "outcome: UNKNOWN (province record not found -- do not assume a win)"
    if owner == save.header.nation:
        return f"after this turn {battlefield} is HELD BY YOU"
    if owner == INDEPENDENT:
        return (f"after this turn {battlefield} is NOT yours "
                f"(independent, or a province you cannot see)")
    return f"after this turn {battlefield} is held by {nation(owner)}"


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
    prot = m.total_protection(type_id, _A) if _A else mon.protection
    shield = ""
    if _A and any(a.is_shield for a in m.armour_of(type_id, _A)):
        shield = " +shield"
    return [
        f"{indent}{count:4d} x {mon.name}",
        f"{indent}       hp{mon.hp} sz{mon.size} prot{prot}{shield} "
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
        print(f"  {held_by(save, b.battlefield)}")
        for side in oc.sides:
            mark = " (you)" if side.observable else ""
            if side.observable:
                print(f"\n  {nation(side.nation)}{mark}: {len(side.engaged)} engaged, "
                      f"{side.survived} survived, {len(side.lost)} lost "
                      f"({side.loss_fraction:.0%})")
            else:
                # Never print a loss percentage for a side we cannot see. A
                # defeat hides the whole enemy army and would read as 100%.
                print(f"\n  {nation(side.nation)}: {len(side.engaged)} engaged, "
                      f"{len(side.lost)} no longer visible to you")
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
