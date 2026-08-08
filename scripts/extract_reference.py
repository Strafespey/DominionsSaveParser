"""Extract Dominions 6 reference data from the game engine.

The engine exposes several undocumented, read-only dump switches. This script
runs them and writes normalised JSON into `data/reference/`.

    py scripts/extract_reference.py
    py scripts/extract_reference.py --out data/reference

None of these switches touch a savegame -- they print and exit.

Not covered yet: the monster/weapon/armour stat tables, which are compiled into
the executable rather than exposed by a switch. See docs/FILE_FORMAT.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dom6.engine import Engine, EngineError  # noqa: E402
from dom6.gamedata import GameDataError, MonsterTable  # noqa: E402

DEFAULT_OUT = Path(__file__).resolve().parent.parent / "data" / "reference"


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  wrote {path.relative_to(Path.cwd())} ({path.stat().st_size:,} bytes)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--exe", help="path to Dominions6.exe")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    try:
        engine = Engine(args.exe)
    except EngineError as exc:
        print(f"error: {exc}")
        return 1
    print(f"engine: {engine.exe}")

    print("\n--listnations")
    nations = engine.list_nations()
    write_json(args.out / "nations.json", nations)
    print(f"  {len(nations)} nations")

    print("\n--listspells")
    spells = engine.list_spells()
    write_json(args.out / "spells.json", spells)
    print(f"  {len(spells)} spells")

    print("\n--listevents")
    events = engine.list_events()
    write_json(args.out / "events.json", events)
    print(f"  {len(events)} events")

    print("\n--comsumrits")
    rits = engine.summon_rituals()
    write_json(args.out / "summon_rituals.json", rits)
    print(f"  {len(rits)} summon rituals")

    print("\nmonster table (extracted from the executable)")
    try:
        table = MonsterTable.from_exe(args.exe)
    except GameDataError as exc:
        print(f"  skipped: {exc}")
    else:
        table.save(args.out / "monsters.json")
        print(f"  {len(table)} monsters, ids 0..{table.layout.highest_id} "
              f"(stride {table.layout.stride})")
        print(f"  wrote {(args.out / 'monsters.json')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
