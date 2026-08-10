"""Size accounting for battle replays: is there room for a per-hit log?

    py scripts/vcr_anatomy.py <GameName>
    py scripts/vcr_anatomy.py <path-to-.trn>

Splits each `_vcr_VCR` section into three parts and measures them:

  header       marker .. first combatant record
  units        the 173-byte combatant array (battle *setup*)
  tail         last record .. next replay or EOF

The question this answers is whether a blow-by-blow combat log could be
hiding in the unmapped parts. It cannot -- see docs/FILE_FORMAT.md section 4a.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dom6 import find_save_root, load, load_savegame  # noqa: E402

#: A minimal per-hit event (attacker, target, damage, flags) could not be
#: smaller than this, and a real format would be larger.
MIN_EVENT_BYTES = 6

#: Rough lower bound on rounds in a real battle, used only to show the
#: order of magnitude a log would need.
ASSUMED_ROUNDS = 30


def resolve(target: str) -> Path | None:
    p = Path(target)
    if p.is_file():
        return p
    root = find_save_root()
    folder = (root / target) if root else None
    if not folder or not folder.is_dir():
        return None
    sg = load_savegame(folder)
    return sg.turn_files[0] if sg.turn_files else sg.ftherlnd


def profile(chunk: bytes) -> str:
    if not chunk:
        return "empty"
    counts = Counter(chunk)
    return (f"{len(chunk):8,}B  zero {counts[0] / len(chunk):5.1%}  "
            f"0xff {counts[255] / len(chunk):5.1%}  distinct {len(counts):3d}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target")
    args = ap.parse_args()

    path = resolve(args.target)
    if path is None:
        print(f"not found: {args.target}")
        return 1

    save = load(path)
    if not save.battles:
        print(f"{path.name}: no battle replays in this file")
        return 1

    print(f"{path.name}: {len(save.data):,} bytes, {save.battle_count} replay(s)\n")
    for battle in save.battles:
        end = battle.end_offset or len(save.data)
        offsets = [u.offset for u in battle.units]
        if not offsets:
            print(f"  {battle.battlefield}: no combatant records found")
            continue
        first, last = min(offsets), max(offsets) + 173
        header, units, tail = (
            save.data[battle.offset:first],
            save.data[first:last],
            save.data[last:end],
        )
        needed = len(battle.units) * ASSUMED_ROUNDS * MIN_EVENT_BYTES

        print(f"  {battle.battlefield} — {len(battle.units)} combatants")
        print(f"    header  {profile(header)}")
        print(f"    units   {profile(units)}   ({len(battle.units)} x 173)")
        print(f"    tail    {profile(tail)}")
        print(f"    a per-hit log would need >= {needed:,}B "
              f"({len(battle.units)} units x {ASSUMED_ROUNDS} rounds x "
              f"{MIN_EVENT_BYTES}B); tail holds {len(tail):,}B "
              f"= {len(tail) / needed:.1%} of that\n")

    print("The header does not scale with combatant count and is mostly 0xFF "
          "sentinel\n(fixed-size, mostly-empty tables). The tail is the only "
          "part that scales, and\nit is one to two orders of magnitude too "
          "small to be a combat log.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
