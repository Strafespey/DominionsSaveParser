"""Measure friendly fire in a battle.

    py scripts/friendly_fire.py <GameName> --log log.txt [--battle N]

The combat log identifies units **by name only** (`dom6/combatlog.py`), so it
cannot say which side anyone was on. The side map has to come from the turn
file, which stores every unit in the battle as (type_id, owner). Joining the
two on the monster name is what makes "who shot whom" answerable.

That join is only sound when a name belongs to exactly one side. When both
armies field the same unit type -- common in a civil war or with independents
-- those names are reported as ambiguous and excluded rather than guessed at,
because counting them either way would be wrong.

Mounts matter here: a `Cataphracted War Horse` is a separate entry in the
roster from its rider, so cavalry appear twice. That inflates unit counts but
not damage, since the log attributes each blow to whichever body took it.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dom6 import find_save_root, load  # noqa: E402
from dom6.combatlog import parse_file  # noqa: E402
from dom6.engine import Engine  # noqa: E402
from dom6.gamedata import monsters  # noqa: E402


def resolve_savegame(name: str) -> Path:
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


def side_map(battle, mons) -> tuple[dict[str, int], set[str], dict[int, int]]:
    """name -> owner, plus the names that are ambiguous and a roster count.

    A name maps to a side only if every unit carrying it has the same owner.
    """
    owners: dict[str, set[int]] = defaultdict(set)
    roster: Counter[int] = Counter()
    for u in battle.units:
        m = mons.get(u.type_id)
        name = getattr(m, "name", None) or f"#{u.type_id}"
        owners[name].add(u.owner)
        roster[u.owner] += 1
    clean = {n: next(iter(o)) for n, o in owners.items() if len(o) == 1}
    ambiguous = {n for n, o in owners.items() if len(o) > 1}
    return clean, ambiguous, dict(roster)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("game", help="savegame name, folder, or .trn path")
    ap.add_argument("--log", required=True, help="log.txt captured from a replay")
    ap.add_argument("--battle", type=int, default=1, help="1-based battle index")
    ap.add_argument("--top", type=int, default=10)
    args = ap.parse_args()

    save_dir = resolve_savegame(args.game)
    trn = sorted(save_dir.glob("*.trn"))
    if not trn:
        raise SystemExit(f"no .trn in {save_dir}")
    save = load(trn[0])
    if not save.battles:
        raise SystemExit("that turn file records no battles")
    battle = save.battles[args.battle - 1]

    # Read the log *before* anything launches the engine. `Engine.run` now
    # preserves log.txt across a launch, but reading first means the analysis
    # never depends on that holding.
    log = parse_file(args.log)

    names = Engine().list_nations()

    def nation(nid: int) -> str:
        return names.get(nid, str(nid)).split(",")[0]

    mons = monsters()
    sides, ambiguous, roster = side_map(battle, mons)

    battles = log.split_battles()
    log = battles[min(args.battle - 1, len(battles) - 1)] if len(battles) > 1 else log

    print(
        f"{battle.battlefield}: {nation(battle.nation_a)} vs {nation(battle.nation_b)}"
    )
    print(
        f"roster: "
        + ", ".join(f"{nation(k)} {v}" for k, v in sorted(roster.items()))
        + f"   |   log: {len(log.hits)} landed attacks"
    )

    # -- classify ----------------------------------------------------------
    ff_dmg: Counter[str] = Counter()          # by attacker
    ff_taken: Counter[str] = Counter()        # by victim
    ff_pairs: Counter[tuple[str, str]] = Counter()
    ff_weapon: Counter[str] = Counter()
    ff_kills: Counter[str] = Counter()
    ff_deaths: Counter[str] = Counter()
    side_dmg: Counter[int] = Counter()        # enemy damage dealt, by side
    side_ff: Counter[int] = Counter()
    taken_total: Counter[str] = Counter()
    unknown: Counter[str] = Counter()
    ff_hits = enemy_hits = 0

    for h in log.hits:
        a, t = sides.get(h.attacker), sides.get(h.target)
        if h.attacker not in sides:
            unknown[h.attacker] += 1
        if h.target not in sides:
            unknown[h.target] += 1
        dmg = max(0, h.damage)
        if h.target in sides:
            taken_total[h.target] += dmg
        if a is None or t is None:
            continue
        if a == t:
            ff_hits += 1
            side_ff[a] += dmg
            ff_dmg[h.attacker] += dmg
            ff_taken[h.target] += dmg
            ff_pairs[(h.attacker, h.target)] += dmg
            if h.weapon:
                ff_weapon[h.weapon] += dmg
            if h.killed:
                ff_kills[h.attacker] += 1
                ff_deaths[h.target] += 1
        else:
            enemy_hits += 1
            side_dmg[a] += dmg

    total_ff = sum(side_ff.values())
    total_enemy = sum(side_dmg.values())
    grand = total_ff + total_enemy

    print()
    print("=== friendly fire ===")
    if not grand:
        print("no attributable damage in this log")
        return
    print(
        f"{ff_hits} of {ff_hits + enemy_hits} attributable landed attacks "
        f"({ff_hits / (ff_hits + enemy_hits):.1%}) hit an ally, "
        f"for {total_ff} of {grand} damage ({total_ff / grand:.1%})"
    )
    for s in sorted(set(side_ff) | set(side_dmg)):
        own = side_ff.get(s, 0)
        at_enemy = side_dmg.get(s, 0)
        tot = own + at_enemy
        if not tot:
            continue
        print(
            f"  {nation(s):<12} {at_enemy:>6} dmg to the enemy, "
            f"{own:>5} to its own troops ({own / tot:.1%} of its output)"
        )

    def table(title: str, data: Counter, unit: str, denom: Counter | None = None):
        if not data:
            return
        print()
        print(title)
        for k, v in data.most_common(args.top):
            share = ""
            if denom is not None and denom.get(k):
                share = f"  ({v / denom[k]:.0%} of all damage it took)"
            print(f"  {v:>6} {unit:<6} {k}{share}")

    table("dealt to allies, by attacker", ff_dmg, "dmg")
    table("taken from allies, by victim", ff_taken, "dmg", taken_total)
    table("allies killed, by attacker", ff_kills, "kills")
    table("killed by allies, by victim", ff_deaths, "died")
    table("weapons responsible", ff_weapon, "dmg")

    if ff_pairs:
        print()
        print("worst shooter -> victim pairs")
        for (a, t), v in ff_pairs.most_common(args.top):
            print(f"  {v:>6} dmg   {a} -> {t}")

    if ambiguous:
        print()
        print(
            "excluded, fielded by both sides so the log cannot attribute them: "
            + ", ".join(sorted(ambiguous))
        )
    if unknown:
        print()
        print("not in the turn file's roster (summons, or renamed commanders):")
        for k, v in unknown.most_common(args.top):
            print(f"  {v:>6} refs  {k}")


if __name__ == "__main__":
    main()
