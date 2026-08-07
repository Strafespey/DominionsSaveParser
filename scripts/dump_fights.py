"""Dump battle rosters by hosting a turn against a throwaway copy of a savegame.

    py scripts/dump_fights.py <GameName>
    py scripts/dump_fights.py <GameName> --raw

Hosting ADVANCES the game, so this never runs against your real save: the
folder is copied to a temp directory and DOM6_SAVE is redirected there. Your
savedgames folder is only ever read.

Note the roster/header pairing caveat documented in docs/ENGINE_TOOLING.md --
rosters may lag their header line by one battle.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dom6 import find_save_root  # noqa: E402
from dom6.engine import Engine, EngineError, SandboxedHost  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("game", help="savegame folder name or path")
    ap.add_argument("--exe", help="path to Dominions6.exe")
    ap.add_argument("--raw", action="store_true", help="print raw engine stdout")
    ap.add_argument("--timeout", type=float, default=600.0)
    args = ap.parse_args()

    folder = Path(args.game)
    if not folder.is_dir():
        root = find_save_root()
        if not root or not (root / args.game).is_dir():
            print(f"savegame not found: {args.game}")
            return 1
        folder = root / args.game

    try:
        engine = Engine(args.exe)
    except EngineError as exc:
        print(f"error: {exc}")
        return 1

    print(f"engine   : {engine.exe}")
    print(f"savegame : {folder}  (copied; original untouched)")

    with SandboxedHost(engine, folder) as box:
        print(f"sandbox  : {box.save_root}")
        fights, result = box.dump_fights(timeout=args.timeout)

    if result.timed_out:
        print("\n!! engine timed out")
    if result.stderr.strip():
        print(f"\nstderr:\n{result.stderr.strip()}")

    if args.raw:
        print("\n----- raw stdout -----")
        print(result.stdout)
        return 0

    if not fights:
        print("\nNo battles were fought when hosting this turn.")
        return 0

    print(f"\n{len(fights)} battle(s):\n")
    for i, f in enumerate(fights):
        print(f"[{i}] {f.attacker} attacking {f.defender} in {f.province}")
        print(
            f"     strength  att={f.attack_strength} def={f.defence_strength} "
            f"PD={f.province_defence}"
        )
        sides = [("attacker", f.attacker_roster), ("defender", f.defender_roster)]
        for label, roster in sides:
            if roster is None:
                continue
            coms = ", ".join(f"{a}x {n}" for a, _, n in roster.commanders) or "-"
            units = ", ".join(f"{a}x {n}" for a, _, n in roster.units) or "-"
            print(f"     {label}: commanders: {coms}")
            print(f"               units     : {units} (total {roster.total_units})")
        if f.rosters_missing:
            print("     (engine emits no roster for the final battle of a host)")
        if f.rosters_may_be_offset:
            print("     ^ roster/header pairing unaligned (see docs)")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
