"""Regression tests for unit-array phase selection.

Two defects lived here, and both were silent: they returned well-formed,
confident, wrong answers rather than raising. A turn-3 T'ien Ch'i .trn reported
a battle as "145 Acolytes of Eldregate led by a Wailing Lady", one-sided, when
the real fight was 83 Lion Tribe independents against 62 T'ien Ch'i troops.
Nothing in the output looked broken.

1. `find_unit_records` chose the *longest* candidate run. A byte-shifted alias
   of the real array parses as plausible and is often the same length or
   longer, so the true roster lost on a tiebreak.
2. `find_unit_arrays(min_length=2)` admitted byte coincidences, because the
   unit-number uniqueness test has no statistical power over two or three
   records. Those false unit numbers then vouched for units that had died.

The fixture is the turn-9 Bandar Log file the README uses as its worked
example. It is a finished game, so it is stable ground truth -- unlike an
in-progress save, which changes under you every time the turn is hosted.

Run directly (`py tests/test_vcr_regression.py`) or under pytest.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import dom6
from dom6 import vcr
from dom6.analysis import _known_monster_ids, battle_outcomes

FIXTURE = Path(__file__).parent / "fixtures" / "mid_bandarlog.trn"

#: Ground truth for the two battles in the fixture, as (owner, type_id) counts.
#: Type ids rather than names, so the test does not need the monster tables
#: extracted from the game executable.
EXPECTED = [
    {
        "nations": (0, 68),
        "battlefield": "Trackless Woods",
        "seed": 115,
        "units_offset": 207414,
        "roster": {
            (0, 29): 20,  # Light Infantry
            (0, 36): 3,  # Commander
            (0, 40): 11,  # Heavy Infantry
            (0, 48): 9,  # Crossbowman
            (68, 1120): 10,  # Markata Archer
            (68, 1122): 1,  # Atavi Infantry
            (68, 1136): 1,  # Bandar Noble
            (68, 1141): 14,  # Tiger Rider
            (68, 1146): 1,  # Brahmin
            (68, 3550): 14,  # Armored Sacred Tiger
        },
        "commanders": 5,
    },
    {
        "nations": (68, 77),
        "battlefield": "Trackless Woods",
        "seed": 9187,
        "units_offset": 271396,
        "roster": {
            (68, 1120): 10,
            (68, 1122): 1,
            (68, 1136): 1,
            (68, 1141): 13,
            (68, 1146): 1,
            (68, 3550): 13,
            (77, 55): 49,  # Longbowman
            (77, 291): 1,  # Captain
        },
        "commanders": 3,
    },
]


def _load():
    assert FIXTURE.exists(), f"missing fixture: {FIXTURE}"
    return dom6.load(FIXTURE)


def _roster(units):
    counts: dict[tuple[int, int], int] = {}
    for u in units:
        counts[(u.owner, u.type_id)] = counts.get((u.owner, u.type_id), 0) + 1
    return counts


def test_battle_rosters_are_exact():
    """Both battles decode to the documented order of battle."""
    save = _load()
    assert len(save.battles) == len(EXPECTED)

    for battle, want in zip(save.battles, EXPECTED):
        assert battle.nations == want["nations"]
        assert battle.battlefield == want["battlefield"]
        assert battle.seed == want["seed"]
        assert battle.units_offset == want["units_offset"]
        assert _roster(battle.units) == want["roster"]
        assert sum(u.is_commander for u in battle.units) == want["commanders"]


def test_both_sides_are_present():
    """A replay holds two sides.

    The phase bug's signature was collapsing a battle to a single apparent
    owner, so assert the split directly rather than only via exact counts.
    """
    for battle in _load().battles:
        owners = {u.owner for u in battle.units}
        assert owners == set(battle.nations), (
            f"{battle.battlefield}: expected both sides {set(battle.nations)}, "
            f"got {owners}"
        )


def test_true_run_outranks_its_length_tied_aliases():
    """The fix itself, not just its outcome.

    Battle 0 has four candidate runs of identical length. Ranking by length
    picks among them arbitrarily; only the real one has distinct unit numbers
    and both participants.
    """
    save = _load()
    data = save.data
    checked_a_tie = False

    for battle in save.battles:
        owners = {battle.nation_a, battle.nation_b}
        end = battle.end_offset or len(data)
        runs = vcr._scan_runs(data, battle.offset, end, owners)
        chosen = max(runs, key=lambda r: vcr._run_score(data, r[0], r[1], owners))
        assert chosen[0] == battle.units_offset

        tied = [r for r in runs if r[1] == chosen[1] and r[0] != chosen[0]]
        if tied:
            checked_a_tie = True
        best = vcr._run_score(data, chosen[0], chosen[1], owners)
        for off, n in tied:
            alias = vcr._run_score(data, off, n, owners)
            assert alias < best, f"alias at {off} outranks the real array"
            # The decisive component: unit numbers are identifiers, so the
            # real array has ~no duplicates and an alias is full of them.
            assert best[0] is True and alias[0] is False

    assert checked_a_tie, "fixture no longer exercises a length tie"


def _record(owner: int, type_id: int, unit_number: int, stamp: int = 0x31) -> bytearray:
    """One synthetic unit record, valid enough for the scanner to accept."""
    rec = bytearray(b"\x00" * vcr.UNIT_RECORD_SIZE)
    rec[vcr._OFF_UNIT_TYPE : vcr._OFF_UNIT_TYPE + 2] = type_id.to_bytes(2, "little")
    rec[vcr._OFF_UNIT_TURNSTAMP] = stamp
    rec[vcr._OFF_UNIT_OWNER] = owner
    rec[vcr._OFF_UNIT_NUMBER : vcr._OFF_UNIT_NUMBER + 2] = unit_number.to_bytes(
        2, "little"
    )
    return rec


def test_longer_alias_does_not_win():
    """The turn-3 failure mode, pinned synthetically.

    That save is gone -- it was an in-progress game and has since been hosted
    several times -- and the Bandar Log fixture only ever produces aliases of
    *equal* length, which the old length ranking happened to resolve correctly
    by iteration order. So the actual defect (a **longer** alias beating the
    real array, 146 records against 145) is reproduced here directly.

    Ranking by length picks the alias. Ranking by coherence picks the truth.
    """
    pad = bytearray(b"\xff" * 512)  # owner 0xFF is out of range: no stray runs
    real = bytearray()
    for i, (owner, type_id) in enumerate(
        [(0, 55), (69, 291), (69, 1120), (0, 29), (69, 40)]
    ):
        real += _record(owner, type_id, unit_number=i + 1)

    alias = bytearray()
    for _ in range(6):  # longer, single-owner, duplicate unit numbers
        alias += _record(0, 256, unit_number=7)

    data = bytes(pad + real + pad + alias + pad)
    real_off = len(pad)
    alias_off = len(pad) * 2 + len(real)
    owners = {0, 69}

    runs = dict(vcr._scan_runs(data, 0, len(data), owners))
    assert runs.get(real_off) == 5 and runs.get(alias_off) == 6, (
        f"synthetic arrays not detected as expected: {runs}"
    )

    # The old behaviour, kept explicit so the test states what it prevents.
    by_length = max(runs.items(), key=lambda r: r[1])[0]
    assert by_length == alias_off, "fixture no longer reproduces the defect"

    units, offset = vcr.find_unit_records(data, 0, len(data), allowed_owners=owners)
    assert offset == real_off, "longer alias beat the real array"
    assert len(units) == 5
    assert {u.owner for u in units} == owners


def test_map_arrays_belong_to_one_nation():
    """Armies on the map are single-nation; only replays hold two sides.

    This is the guard that keeps byte coincidences out of the alive-set at
    min_length=2, where unit-number uniqueness cannot discriminate.
    """
    save = _load()
    spans = [(b.offset, b.end_offset or len(save.data)) for b in save.battles]

    arrays = vcr.find_unit_arrays(save.data, min_length=2, exclude_spans=spans)
    outside = [
        (off, units)
        for off, units in arrays
        if not any(a <= off < b for a, b in spans)
    ]
    assert outside, "expected to find armies standing on the map"
    for off, units in outside:
        owners = {u.owner for u in units}
        assert len(owners) == 1, f"map array at {off} spans nations {owners}"


def test_known_types_filters_and_recovers_arrays():
    """Rejecting unresolvable type ids both removes noise and recovers arrays.

    The recovery half is the subtle one: a genuine array can be displaced
    during greedy overlap resolution by a longer garbage run sitting across
    it. Dropping the garbage lets the real array through. That is the class a
    surviving commander's post-battle record fell into.
    """
    known = _known_monster_ids()
    if not known:
        print("   (skipped: monster tables not extracted)")
        return

    save = _load()
    spans = [(b.offset, b.end_offset or len(save.data)) for b in save.battles]

    def alive(**kwargs) -> set[int]:
        return {
            u.unit_number
            for off, units in vcr.find_unit_arrays(save.data, min_length=2, **kwargs)
            if not any(a <= off < b for a, b in spans)
            for u in units
        }

    unguarded = alive()
    guarded = alive(known_types=known, exclude_spans=spans)
    assert unguarded - guarded, "should reject arrays of unresolvable type ids"
    assert guarded - unguarded, "should recover displaced genuine arrays"


def test_default_scan_still_finds_two_sided_replay_arrays():
    """The single-nation rule must not leak into the no-spans default.

    Without `exclude_spans` the caller has not said where the replays are, so
    every offset must be allowed two owners. Applying the map rule everywhere
    silently rejected every two-sided battle array -- the exact arrays this
    function exists to find.
    """
    save = _load()
    spans = [(b.offset, b.end_offset or len(save.data)) for b in save.battles]

    def two_sided(**kwargs) -> int:
        return sum(
            len({u.owner for u in units}) > 1
            for off, units in vcr.find_unit_arrays(save.data, min_length=2, **kwargs)
            if any(a <= off < b for a, b in spans)
        )

    assert two_sided() > 0, "default scan lost every two-sided replay array"
    assert two_sided(exclude_spans=spans) > 0


def test_own_losses_are_marked_observable():
    """Loss inference is trustworthy for the turn owner and not for the enemy."""
    save = _load()
    outcomes = battle_outcomes(save)
    assert len(outcomes) == len(save.battles)

    for outcome in outcomes:
        own = outcome.side(save.header.nation)
        assert own is not None and own.observable
        assert own.caveat is None
        for side in outcome.sides:
            assert 0 <= len(side.lost) <= len(side.engaged)
            if side.nation != save.header.nation:
                assert not side.observable
                assert side.caveat


def test_own_army_survives_across_both_battles():
    """Bandar Log fought twice and was not wiped out.

    A regression that loses the owner's post-battle records makes survivors
    look dead -- which is exactly how a live General was reported killed.
    """
    save = _load()
    for outcome in battle_outcomes(save):
        own = outcome.side(save.header.nation)
        assert own is not None
        assert own.survived > 0, f"{outcome.province}: own army reported annihilated"
        assert own.loss_fraction < 0.5, (
            f"{outcome.province}: implausible {own.loss_fraction:.0%} own losses"
        )


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in tests:
        try:
            fn()
        except AssertionError as exc:
            failed += 1
            print(f"FAIL {fn.__name__}: {exc}")
        else:
            print(f"ok   {fn.__name__}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)
