"""Tests for the per-hit combat log parser.

The sample lines below are **not** invented. Each one is an instantiation of a
format string extracted from `Dominions6.exe`'s own string table, which is how
the grammar in `dom6/combatlog.py` was derived:

    %s hit %s in %s with %s for %d points of damage %s
    %s hit %s on the shield and %s with %s for %d points of damage %s
    %s trampled %s for %d points of damage
    %s attacks with %s
    %s casts %s
    %s repels %s (%s repelling %s)
    %s missed to repel %s (%d vs %d)
    %s's attack with %s was repelled by %s
    %s failed an individual rout check. (%d+%d vs %d+%d)
    Army rout (%d) for %s
    Army rout 50 for %s (HP rout)
    %s took %d points of damage from the lingering poison
    %s takes %d points of damage from false damage overload

plus the observed-in-the-wild lines quoted in `docs/ENGINE_TOOLING.md`.

Run directly (`py tests/test_combatlog.py`) or under pytest.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dom6.combatlog import parse, parse_lines  # noqa: E402

# Two battles, so split_battles() has something to cut on.
SAMPLE = """\
Playvcr lnr12 def5 att0 incstle0 seed9189 checksums79
TickBattle 77940 +10 (bcs -183356030)
Red Guard attacks with Lance
Red Guard attacks with Lance
Red Guard attacks with Lance
Damage roll 18+13 vs prot roll of 13+9 of Einhere = 9 points of damage
Damage exceeded maximum possible in hit area, reduced to 6 points of damage
Longdead Horseman hit Einhere in arm with Light Lance for 6 points of damage
Einhere hit Skeletal Horse in body with Broad Sword for 11 points (target was killed)
Longdead Velite hit Cataphracted War Horse with a ranged attack (Javelin) in the leg for 0
Shield hit, incoming damage reduced by 7
Red Guard hit Emerald Guard on the shield and arm with Lance for 3 points of damage
Imperial Elephant trampled Militia for 14 points of damage (target was killed)
Ministry Footman attacks with Spear
Ministry Footman repels Barbarian (Spear repelling Great Sword)
Barbarian missed to repel Red Guard (7 vs 12)
Red Guard's attack with Lance was repelled by Emerald Guard
Militia failed an individual rout check. (8+3 vs 10+6)
Emerald Guard passed an individual rout check. (14+7 vs 9+4)
Theurg casts Communion Master
Red Guard took 5 points of damage from the lingering poison
Ministry Footman takes 3 points of damage from excessive fatigue
hms 44, crc 45
Army rout (50) for Pythium
TickBattle 77950 +10 (bcs -1833)
Playvcr lnr44 def2 att1 incstle0 seed1234 checksums12
TickBattle 80000 +10 (bcs -1)
Imperial Crossbowman hit Theurg in head with Crossbow for 12 points (target was killed)
Army rout 50 for Pythium (HP rout)
"""


def check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def test_hits():
    log = parse(SAMPLE)
    check(len(log.hits) == 6, f"expected 6 hits, got {len(log.hits)}")

    by_attacker = {h.attacker: h for h in log.hits}

    h = by_attacker["Longdead Horseman"]
    check(h.target == "Einhere", f"bad target {h.target!r}")
    check(h.location == "arm", f"bad location {h.location!r}")
    check(h.weapon == "Light Lance", f"bad weapon {h.weapon!r}")
    check(h.damage == 6, f"bad damage {h.damage}")
    check(h.damage_roll == (18, 13), f"bad damage roll {h.damage_roll}")
    check(h.prot_roll == (13, 9), f"bad prot roll {h.prot_roll}")
    # The engine reported 9, then capped it to 6 for the hit area.
    check(h.capped_from == 9, f"expected capped_from 9, got {h.capped_from}")

    check(by_attacker["Einhere"].killed, "kill flag not set")

    r = by_attacker["Longdead Velite"]
    check(r.ranged, "ranged attack not flagged")
    check(r.weapon == "Javelin", f"bad ranged weapon {r.weapon!r}")
    check(r.location == "leg", f"bad ranged location {r.location!r}")
    check(r.damage == 0 and r.blocked, "zero-damage hit should read as blocked")

    s = by_attacker["Red Guard"]
    check(s.shield_hit, "shield hit not flagged")
    check(s.shield_reduction == 7, f"bad shield reduction {s.shield_reduction}")

    t = by_attacker["Imperial Elephant"]
    check(t.weapon == "Trample" and t.killed, "trample not parsed")


def test_repels():
    log = parse(SAMPLE)
    check(len(log.repels) == 3, f"expected 3 repels, got {len(log.repels)}")
    summary = log.repel_summary()
    check(summary["Ministry Footman"]["repelled"] == 1, "footman repel missing")
    check(summary["Barbarian"]["missed"] == 1, "barbarian miss missing")
    check(summary["Emerald Guard"]["repelled"] == 1, "emerald guard repel missing")


def test_rout():
    log = parse(SAMPLE)
    check(len(log.rout_checks) == 2, f"expected 2 rout checks, got {len(log.rout_checks)}")
    failed = [r for r in log.rout_checks if not r.passed]
    check(len(failed) == 1 and failed[0].unit == "Militia", "failed rout check wrong")
    check(failed[0].rolls == (8, 3, 10, 6), f"bad rolls {failed[0].rolls}")

    check(len(log.army_routs) == 2, f"expected 2 army routs, got {len(log.army_routs)}")
    hp = [a for a in log.army_routs if a.hp_rout]
    check(len(hp) == 1, "HP rout variant not distinguished")
    check(hp[0].nation == "Pythium", f"bad nation {hp[0].nation!r}")


def test_environmental_and_casts():
    log = parse(SAMPLE)
    sources = {e.source: e for e in log.environmental}
    check("the lingering poison" in sources, f"missing poison, got {list(sources)}")
    check("excessive fatigue" in sources, f"missing fatigue, got {list(sources)}")
    check(sources["excessive fatigue"].damage == 3, "bad fatigue damage")
    check(len(log.casts) == 1 and log.casts[0].spell == "Communion Master", "cast wrong")


def test_hit_rate():
    log = parse(SAMPLE)
    rates = log.hit_rate()
    # Red Guard swings three times and connects once. The two that produced no
    # hit line are a miss and a repelled attack -- a repel aborts the attack
    # before it resolves (manual p.62-63), so it costs an attempt and yields
    # no hit. That is exactly the distinction this metric exists to surface.
    check("Red Guard" in rates, "Red Guard missing from hit rate")
    attempts, landed, rate = rates["Red Guard"]
    check(attempts == 3, f"expected 3 attempts, got {attempts}")
    check(landed == 1, f"expected 1 landed, got {landed}")
    check(abs(rate - 1 / 3) < 1e-9, f"bad rate {rate}")

    # A unit that swings and never connects must still appear, at 0%.
    check(rates["Ministry Footman"][1] == 0, "non-connecting attacker missing")


def test_aggregates():
    log = parse(SAMPLE)
    check(log.damage_dealt()["Imperial Elephant"] == 14, "damage dealt wrong")
    # 5 poison + 3 hit from the shield line's target is not Red Guard; only the
    # poison lands on it.
    check(log.damage_taken()["Red Guard"] == 5, "environmental damage not counted")
    check(log.kills()["Einhere"] == 1, "kill tally wrong")
    check(log.deaths()["Militia"] == 1, "death tally wrong")
    check(log.capped_damage() == 3, f"cap loss wrong: {log.capped_damage()}")
    check(log.hit_locations()["arm"] == 2, "hit location tally wrong")


def test_split_battles():
    log = parse(SAMPLE)
    battles = log.split_battles()
    check(len(battles) == 2, f"expected 2 battles, got {len(battles)}")
    check(len(battles[1].hits) == 1, "second battle should have one hit")
    check(battles[1].hits[0].attacker == "Imperial Crossbowman", "wrong split")
    check(battles[1].army_routs[0].hp_rout, "HP rout landed in the wrong battle")
    # Ticks must be split too, not left at zero on the sub-logs.
    check(battles[0].ticks == 2, f"battle 1 ticks {battles[0].ticks}")
    check(battles[1].ticks == 1, f"battle 2 ticks {battles[1].ticks}")
    check(
        sum(b.ticks for b in battles) == log.ticks,
        "split ticks do not sum to the whole",
    )


def test_noise_is_ignored():
    """Debug chatter must not produce phantom events."""
    noise = "\n".join(
        [
            "hms 44, crc 45",
            "bcs -183356030 unr12 spec0x4 ba7",
            "getbattlecountfromvcr",
            "readvcr: got land 12, own 3, frtown 3, pd 0, ass 0",
            "",
            "   ",
        ]
    )
    log = parse(noise)
    check(not log.hits, f"noise produced hits: {log.hits}")
    check(not log.casts, f"noise produced casts: {log.casts}")
    check(log.lines_matched == 0, f"noise matched {log.lines_matched} lines")


#: Lines quoted verbatim from a real 798k-line capture of the turn-22 battle
#: in `MATC_Awake_Expander`. The viewer writes every on-screen message to the
#: log a second time wrapped in text-cache chatter; parsing those echoes
#: counted each event up to three times.
ECHO_SAMPLE = """\
Red Guard hit Gladiator in body with Lance for 12 points of damage (target was killed)
creating new text tex 'Red Guard hit Gladiator in body with Lance for 12 points of damage (target was killed)' (482*15) forcep2 0
puttextincache f8 'Red Guard hit Gladiator in body with Lance for 12 points of damage (target was killed)' (482*15) forcep2 0
Red Guard missed Battle Vestal
creating new text tex 'Red Guard missed Battle Vestal' (180*15) forcep2 0
Imperial Crossbowman hit Hastatus in leg with Crossbow for 3 points of damage
al Crossbowman hit Hastatus in leg with Crossbow for 3 points of damage' (582*15) forcep2 0
"""


def test_ui_echo_is_not_double_counted():
    log = parse(ECHO_SAMPLE)
    check(len(log.hits) == 2, f"expected 2 hits, got {len(log.hits)} (echo counted)")
    check(len(log.misses) == 1, f"expected 1 miss, got {len(log.misses)}")
    check(
        log.damage_dealt() == {"Red Guard": 12, "Imperial Crossbowman": 3},
        f"echo inflated the totals: {log.damage_dealt()}",
    )
    # The echo must not invent a unit called "creating new text tex 'Red Guard",
    # nor a truncated one called "al Crossbowman".
    check(
        all("text tex" not in h.attacker for h in log.hits),
        "renderer chatter leaked into a unit name",
    )
    check(
        "al Crossbowman" not in log.damage_dealt(),
        "a truncated echo tail leaked in as its own unit",
    )


def test_misses():
    log = parse(SAMPLE + "Archer missed Hastatus\n")
    names = [(m.attacker, m.target) for m in log.misses]
    check(("Archer", "Hastatus") in names, f"miss not parsed: {names}")
    # "missed to repel" is a repel, not a miss -- SAMPLE contains one.
    check(
        all(not t.startswith("to repel") for _, t in names),
        f"'missed to repel' parsed as a miss: {names}",
    )
    swings, landed, rate = log.accuracy()["Archer"]
    check((swings, landed, rate) == (1, 0, 0.0), f"bad accuracy {swings, landed, rate}")


def test_blunt_bonus():
    log = parse(
        "Damage increased by 4 due to blunt hit in the head\n"
        "Red Guard hit Gladiator in head with Maul for 15 points of damage\n"
    )
    check(len(log.hits) == 1, f"expected 1 hit, got {len(log.hits)}")
    check(log.hits[0].blunt_bonus == 4, f"bad blunt bonus {log.hits[0].blunt_bonus}")


def test_streaming_matches_string_parse():
    """parse_file streams line by line; it must agree with parse()."""
    a = parse(SAMPLE)
    b = parse_lines(iter(SAMPLE.splitlines(keepends=True)))
    check(len(a.hits) == len(b.hits), "streaming lost hits")
    check(a.damage_dealt() == b.damage_dealt(), "streaming changed totals")
    check(len(a.repels) == len(b.repels), "streaming lost repels")


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  ok   {t.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"  FAIL {t.__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
