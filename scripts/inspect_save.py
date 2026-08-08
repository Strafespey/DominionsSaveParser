"""Inspect Dominions 6 savegames: header, battles, strings.

Usage:
    py scripts/inspect_save.py                       # list all savegames
    py scripts/inspect_save.py <game-name>           # summarise one game
    py scripts/inspect_save.py <path-to-file>        # inspect one save file
    py scripts/inspect_save.py <file> --strings 40   # dump decoded strings
    py scripts/inspect_save.py <file> --battles      # detail battle replays
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dom6 import find_save_root, list_savegames, load, load_savegame  # noqa: E402

_NATIONS: dict[int, str] | None = None
_MONSTERS = None


def monster_label(type_id: int) -> str:
    """Monster name from the executable, falling back to the raw id."""
    global _MONSTERS
    if _MONSTERS is None:
        try:
            from dom6.gamedata import monsters

            _MONSTERS = monsters()
        except Exception:  # noqa: BLE001 - the executable is optional
            _MONSTERS = False
    if _MONSTERS:
        return _MONSTERS.label(type_id)
    return f"type {type_id}"


def loadout(type_id: int) -> str:
    """Weapons a unit type carries, with reach and range."""
    if _MONSTERS is None:
        monster_label(type_id)
    if not _MONSTERS:
        return ""
    try:
        from dom6.gamedata import weapons

        ws = _MONSTERS.weapons_of(type_id, weapons())
    except Exception:  # noqa: BLE001
        return ""
    if not ws:
        return ""
    parts = []
    for w in ws:
        if w.is_missile:
            parts.append(f"{w.name} rng {w.range}")
        else:
            parts.append(f"{w.name} len {w.effective_length}")
    return " | " + ", ".join(parts)


def stats(type_id: int) -> str:
    """Compact combat stats for a unit type."""
    if _MONSTERS is None:
        monster_label(type_id)
    if not _MONSTERS:
        return ""
    m = _MONSTERS.get(type_id)
    if not m or not m.hp:
        return ""
    mor = "MINDLESS" if m.is_mindless else f"mor{m.morale}"
    return (
        f"hp{m.hp} sz{m.size} prot{m.protection} "
        f"att{m.attack} def{m.defence} {mor} enc{m.encumbrance}"
    )


def nation_names() -> dict[int, str]:
    """Nation id -> name, queried once from the engine. Empty if unavailable."""
    global _NATIONS
    if _NATIONS is None:
        try:
            from dom6.engine import Engine

            _NATIONS = Engine().list_nations()
        except Exception:  # noqa: BLE001 - the engine is optional
            _NATIONS = {}
    return _NATIONS


def cmd_list() -> int:
    root = find_save_root()
    if not root:
        print("No savedgames folder found. Set DOM6_SAVE or install Dominions 6.")
        return 1
    print(f"savedgames root: {root}\n")
    games = list_savegames(root)
    if not games:
        print("(no savegames)")
        return 0
    for sg in games:
        print(f"  {sg.describe()}")
    return 0


def summarise_game(folder: Path) -> int:
    sg = load_savegame(folder)
    print(f"=== {sg.name} ===")
    files = ([sg.ftherlnd] if sg.ftherlnd else []) + sg.turn_files + sg.order_files
    for f in files:
        try:
            save = load(f)
        except Exception as exc:  # noqa: BLE001 - report and continue
            print(f"  {f.name}: FAILED ({exc})")
            continue
        print(f"  {save.describe()}")
        for b in save.battles:
            print(f"      {b.describe(nation_names())}")
    return 0


def inspect_file(path: Path, args) -> int:
    save = load(path)
    h = save.header
    nations = nation_names()
    who = nations.get(h.nation, "master state" if h.is_master else f"id {h.nation}")
    print(f"file      : {save.path}")
    print(f"kind      : {save.kind}")
    print(f"size      : {len(save.data)} bytes")
    print(f"preamble  : {h.preamble.hex(' ')}")
    print(f"version   : {h.version} ({'Dominions 6' if h.is_dominions6 else 'unknown'})")
    print(f"game name : {h.game_name!r}")
    print(f"turn      : {h.turn}")
    print(f"nation    : {h.nation} ({who})")
    print(f"hdr words : {h.unknown_words}")
    print(f"battles   : {save.battle_count}")

    if args.battles or save.battles:
        for b in save.battles:
            print(f"\n  --- {b.describe(nations)} ---")
            print(f"      span to next marker : {b.size} bytes")
            print(f"      names in header     : {b.names}")
            print(f"      int32 fields        : {b.raw_fields}")
            if b.units:
                print(f"      combatants          : {len(b.units)} "
                      f"@0x{b.units_offset or 0:08x}")
                squads = b.squads()
                for owner, side in sorted(b.order_of_battle().items()):
                    label = nations.get(owner, "Independents" if owner == 0 else f"nation {owner}")
                    print(f"        {label.split(',')[0]} "
                          f"({side['commanders']} cmd, {side['units']} units)")
                    for (o, sid), members in squads.items():
                        if o != owner:
                            continue
                        tag = "commanders" if sid == 0xFFFF else f"squad {sid}"
                        pos = members[0].position
                        at = f" at {pos}" if pos else ""
                        print(f"          {tag} ({len(members)}){at}:")
                        counts = Counter(m.type_id for m in members)
                        for t, n in counts.most_common():
                            print(f"            {n:4d} x {monster_label(t)}")
                            print(f"                 {stats(t)}{loadout(t)}")
            else:
                print("      combatants          : none found "
                      "(assassination replays are not decoded yet)")
            if args.battles:
                from dom6.reader import Cursor

                print(Cursor(save.data).hexdump(160, base=b.offset - 16))

    if args.strings:
        print(f"\n--- first {args.strings} strings ---")
        for off, text in save.strings(min_len=4, limit=args.strings):
            print(f"  @{off:08x}  {text[:100]}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target", nargs="?", help="savegame name, folder, or file")
    ap.add_argument("--strings", type=int, default=0, metavar="N",
                    help="dump the first N decoded strings")
    ap.add_argument("--battles", action="store_true",
                    help="hexdump around each battle replay marker")
    args = ap.parse_args()

    if not args.target:
        return cmd_list()

    p = Path(args.target)
    if p.is_file():
        return inspect_file(p, args)
    if p.is_dir():
        return summarise_game(p)

    root = find_save_root()
    if root and (root / args.target).is_dir():
        return summarise_game(root / args.target)

    print(f"Not found: {args.target}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
