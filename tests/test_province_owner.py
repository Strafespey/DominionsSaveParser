"""Regression test for the worst bug this tool has had: a defeat read as a win.

`battle_outcomes()` infers losses from which units are still visible afterwards.
Enemy survivors are never visible in a turn file, so every enemy side reads as
~100% destroyed -- and a *defeat* is the case where that reads most convincingly
like annihilation, because losing the province also loses sight of it.

Reported live: a turn-20 battle at Shamballac printed "Independents: 70 engaged,
1 survived, 69 lost (99%)" against "T'ien Ch'i: 90 lost (70%)", and was written
up as an expensive victory. The player had actually lost the province.

The fix is to stop inferring outcomes from casualties and read province
ownership instead. These tests pin both halves: the owner field decodes, and
the enemy-loss fraction is *not* usable as an outcome signal.

Run directly (`py tests/test_province_owner.py`) or under pytest.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import dom6
from dom6.analysis import battle_outcomes
from dom6.provinces import find_provinces, owner_of
from dom6.scores import latest_by_nation

FIXTURE = Path(__file__).parent / "fixtures" / "mid_bandarlog.trn"


def test_owner_counts_do_not_exceed_the_score_record():
    """Enumeration is incomplete, so it may undercount -- never overcount.

    An overcount would mean the owner offset is decoding something else.
    """
    save = dom6.load(FIXTURE)
    truth = {n: r.provinces for n, r in latest_by_nation(save.scores()).items()}
    found: dict[int, int] = {}
    for prov in find_provinces(save):
        found[prov.owner] = found.get(prov.owner, 0) + 1
    me = save.header.nation
    assert found.get(me, 0) <= truth[me]
    assert found.get(me, 0) >= truth[me] - 2, "should find most of the player's provinces"


def test_owner_of_returns_none_for_unknown_province():
    """None means 'cannot tell', and must never be confused with 'nobody'."""
    save = dom6.load(FIXTURE)
    assert owner_of(save, "No Such Province At All") is None


def test_battlefields_resolve_to_a_province_record():
    save = dom6.load(FIXTURE)
    for oc in battle_outcomes(save):
        name = oc.battle.battlefield
        if name:
            assert owner_of(save, name) is not None, f"no province record for {name}"


def test_enemy_loss_fraction_is_not_an_outcome_signal():
    """The bug, stated as a test: unobservable sides always look wiped out.

    If this ever stops holding, the caveat can be softened -- until then, no
    report may present an enemy loss percentage as evidence of a victory.
    """
    save = dom6.load(FIXTURE)
    for oc in battle_outcomes(save):
        for side in oc.sides:
            if not side.observable:
                assert side.loss_fraction > 0.9, (
                    "unobservable sides read as near-total losses regardless of "
                    "the real result -- that is exactly why it cannot be trusted"
                )
                assert side.caveat, "an unobservable side must carry its caveat"


def test_provinces_exclude_battle_replays():
    """Replays store the province name twice too, and must not be counted."""
    save = dom6.load(FIXTURE)
    names = [p.name for p in find_provinces(save)]
    assert len(names) == len(set(names)), f"duplicate province records: {names}"


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"ok    {name}")
            except AssertionError as exc:
                failures += 1
                print(f"FAIL  {name}: {exc}")
    raise SystemExit(1 if failures else 0)
