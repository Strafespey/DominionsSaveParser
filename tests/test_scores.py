"""Golden tests for the score-graph history parser.

The expected values are not hand-derived: they are the engine's own
`scores.html`, produced by hosting a copy of this savegame with `--scoredump`
(see `docs/ENGINE_TOOLING.md`). All 42 values below -- six nations across
seven metrics -- were checked against that file and matched exactly.

This fixture is the turn-9 Bandar Log game, which is finished and therefore
stable. Its layout was *not* used to derive the record format; that came from
a different game (MA T'ien Ch'i), so this doubles as the holdout that shows
the format generalises across games and nation sets.

Run directly (`py tests/test_scores.py`) or under pytest.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import dom6
from dom6.scores import RECORD_SIZE, find_score_history, history_for, latest_by_nation

FIXTURE = Path(__file__).parent / "fixtures" / "mid_bandarlog.trn"

#: nation id -> (provinces, forts, income, gem_income, research, dominion, army)
#: at turn 8, the newest turn this file carries. Source: engine `scores.html`.
EXPECTED_TURN_8 = {
    52: (3, 1, 437, 5, 43, 48, 92),  # Pangaea
    57: (5, 1, 887, 10, 48, 108, 95),  # Man
    60: (7, 1, 872, 6, 28, 46, 71),  # Ulm
    68: (8, 1, 949, 5, 53, 89, 118),  # Bandar Log
    73: (2, 1, 578, 5, 16, 40, 116),  # Mictlan
    77: (2, 1, 515, 5, 19, 44, 61),  # Phaeacia
}

FIELDS = (
    "provinces",
    "forts",
    "income",
    "gem_income",
    "research",
    "dominion",
    "army_size",
)


def test_history_shape():
    records = find_score_history(FIXTURE.read_bytes())
    nations = {r.nation for r in records}
    turns = {r.turn for r in records}
    assert nations == set(EXPECTED_TURN_8)
    assert turns == set(range(9)), "a turn-9 file should carry turns 0..8"
    assert len(records) == len(nations) * len(turns), "every nation, every turn"


def test_values_match_engine_scoredump():
    records = find_score_history(FIXTURE.read_bytes())
    latest = latest_by_nation(records)
    for nation, expected in EXPECTED_TURN_8.items():
        rec = latest[nation]
        assert rec.turn == 8
        got = tuple(getattr(rec, f) for f in FIELDS)
        assert got == expected, f"nation {nation}: {got} != {expected}"


def test_history_is_ordered_and_monotone_in_turn():
    records = find_score_history(FIXTURE.read_bytes())
    for nation in EXPECTED_TURN_8:
        rows = history_for(records, nation)
        assert [r.turn for r in rows] == list(range(9))


def test_exposed_on_savefile_and_cached():
    save = dom6.load(FIXTURE)
    first = save.scores()
    assert first and save.scores() is first, "result should be cached"


def test_orders_file_has_no_history():
    """A .2h carries orders only. Returning [] beats returning noise."""
    assert find_score_history(b"\x00" * (RECORD_SIZE * 40)) == []


def test_rejects_short_coincidental_runs():
    """Two turns of records is below the minimum and must not be reported."""
    import struct

    blob = b"".join(
        struct.pack("<11H", turn, nation, 1, 1, 1, 1, 0, 1, 1, 1, 0)
        for turn in range(2)
        for nation in (10, 20)
    )
    assert find_score_history(blob) == []


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
