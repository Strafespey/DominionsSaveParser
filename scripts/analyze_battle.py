"""Replay a past battle in the game and analyse the per-hit combat log.

    py scripts/analyze_battle.py <GameName>              # list battles, then capture
    py scripts/analyze_battle.py <GameName> --capture    # open the game and capture
    py scripts/analyze_battle.py --log log.txt           # analyse a log you already have
    py scripts/analyze_battle.py <GameName> --record-macro macro.json
    py scripts/analyze_battle.py <GameName> --capture --macro macro.json

Why a game window opens: the savegame stores a battle's setup plus an RNG
seed, not a narrative, and the engine only re-simulates a past battle when it
is opened in the replay viewer -- which needs a graphics context. There is no
headless route. What this script does do is configure the launch for you (no
Steam launch options needed), sandbox the savegame so nothing can be damaged,
preserve the game's own `log.txt`, and shut everything down when it has what
it needs.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dom6 import find_save_root, load  # noqa: E402
from dom6.combatlog import parse_file  # noqa: E402


def resolve_savegame(name: str) -> Path:
    """Accept a game name or a path to the savegame folder / .trn."""
    p = Path(name)
    if p.is_dir():
        return p
    if p.is_file():
        return p.parent
    root = find_save_root()
    if root is None:
        raise SystemExit("could not find the Dominions 6 savedgames folder")
    cand = Path(root) / name
    if not cand.is_dir():
        raise SystemExit(f"no savegame folder named {name!r} under {root}")
    return cand


def list_battles(save_dir: Path) -> None:
    """Print the battles in the turn file, so you know what you are opening."""
    trn = sorted(save_dir.glob("*.trn"))
    if not trn:
        print(f"no .trn in {save_dir}")
        return
    save = load(trn[0])
    print(f"{trn[0].name}: turn {save.header.turn}, {save.battle_count} battle(s)")
    for i, b in enumerate(save.battles, 1):
        where = b.battlefield or "?"
        print(f"  {i}. {where}")
    print()
    print("The viewer lists battles in the same order as the turn messages.")


def report(log, top: int) -> None:
    battles = log.split_battles()
    if len(battles) > 1:
        print(f"log contains {len(battles)} replayed battles\n")
    for i, b in enumerate(battles, 1):
        if len(battles) > 1:
            print(f"--- battle {i} ---")
        print(b.describe(top=top))
        print()
    print(
        f"[parsed {log.lines_matched} events from {log.lines_read} log lines]"
    )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("game", nargs="?", help="savegame name, folder, or .trn path")
    ap.add_argument("--log", help="analyse an existing log.txt instead of capturing")
    ap.add_argument(
        "--capture",
        action="store_true",
        help="launch the game and capture a replay",
    )
    ap.add_argument("--macro", help="input macro to open the battle automatically")
    ap.add_argument(
        "--record-macro",
        metavar="OUT",
        help="record the clicks/keys that open a battle, and save them",
    )
    ap.add_argument("--timeout", type=float, default=600.0)
    ap.add_argument(
        "--archive",
        metavar="PATH",
        help="where to keep the raw log (default: captures/<game>.log). "
        "A capture costs a game launch and a click, and any engine launch "
        "truncates the game's own log.txt, so it is archived by default.",
    )
    ap.add_argument("--top", type=int, default=8, help="rows per summary table")
    args = ap.parse_args()

    if args.log:
        report(parse_file(args.log), args.top)
        return

    if not args.game:
        ap.error("give a savegame name, or --log to analyse an existing log")

    save_dir = resolve_savegame(args.game)

    if args.record_macro:
        from dom6.engine import Engine
        from dom6.replay import ReplaySession, record_macro

        with ReplaySession(Engine(), save_dir) as sess:
            sess.launch()
            sess._await_window()
            print(
                "Game is open on a sandboxed copy. Open the battle you want,\n"
                "hold CTRL+SHIFT to record a click at the pointer, then press F12."
            )
            record_macro(args.record_macro)
        return

    if not args.capture:
        list_battles(save_dir)
        print("\nRe-run with --capture to open the game and record a replay.")
        return

    from dom6.engine import Engine
    from dom6.replay import ReplaySession, load_macro

    macro = load_macro(args.macro) if args.macro else None
    archive = Path(args.archive) if args.archive else (
        Path(__file__).resolve().parent.parent / "captures" / f"{save_dir.name}.log"
    )
    with ReplaySession(Engine(), save_dir) as sess:
        log = sess.capture(
            macro=macro,
            timeout=args.timeout,
            archive=archive,
            on_status=lambda m: print(f"[{m}]"),
        )
    print()
    report(log, args.top)


if __name__ == "__main__":
    main()
