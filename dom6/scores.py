"""Empire-level statistics: the score-graph history stored in every save.

Dominions keeps the data behind the in-game score graphs as a flat array of
fixed 22-byte records, one per (turn, nation). It is present in `ftherlnd`
**and** in each player's `.trn`, so a player's own turn file already carries
the whole history of every nation they can see -- no hosting required.

The layout was established by known-plaintext search: host a copy of a
savegame with `--scoredump`, which makes the engine write its own
`scores.html`, then look for offsets whose values reproduce that table for all
nations at once. See `docs/FILE_FORMAT.md` section 7.

What the columns mean is the engine's own naming, taken from `scores.html`.
`income`, `gem_income` and `research` are per-turn rates; `provinces`,
`forts`, `dominion` and `army_size` are totals.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass

#: Bytes per record.
RECORD_SIZE = 22

#: Nation ids are small; a turn count beyond this is not a real game.
_MAX_NATION_ID = 250
_MAX_TURN = 2000

#: Reject short runs -- a handful of records can occur by coincidence in the
#: sparse zero/0xFF regions that make up most of a save.
_MIN_TURNS = 3

_REC = struct.Struct("<11H")


@dataclass(frozen=True)
class ScoreRecord:
    """One nation's standing at the end of one turn.

    Every field is verified against the engine's own `--scoredump` output for
    six nations simultaneously, except the two `unknown_*` fields, which have
    read 0 in every record seen so far. `scores.html` has one column with no
    home here -- Victory Points -- and it was 0 for all nations in the sample,
    so it is most likely one of those two.
    """

    turn: int
    nation: int
    provinces: int
    forts: int
    income: int  #: gold per turn
    gem_income: int  #: gems per turn, all paths summed
    research: int  #: research points per turn
    dominion: int  #: total dominion strength
    army_size: int  #: units, including mounts and commanders
    unknown_12: int = 0
    unknown_20: int = 0


def parse_record(data: bytes, offset: int) -> ScoreRecord:
    turn, nation, prov, forts, income, gems, u12, res, dom, army, u20 = _REC.unpack_from(
        data, offset
    )
    return ScoreRecord(
        turn=turn,
        nation=nation,
        provinces=prov,
        forts=forts,
        income=income,
        gem_income=gems,
        research=res,
        dominion=dom,
        army_size=army,
        unknown_12=u12,
        unknown_20=u20,
    )


def find_score_history(data: bytes) -> list[ScoreRecord]:
    """Locate and decode the score-graph array. Empty if it is not present.

    The array has no magic number, so it is identified by its own shape: the
    records cycle through a fixed set of nations in a fixed order, and the
    turn counter advances by exactly one each time the cycle wraps. That
    pattern is long and rigid enough that a byte-coincidence cannot imitate
    it -- the longest run wins.
    """
    best: list[ScoreRecord] = []
    limit = len(data) - RECORD_SIZE
    off = 0
    while off <= limit:
        run = _run_at(data, off)
        if len(run) > len(best):
            best = run
            # A genuine array cannot overlap another, so skip past it.
            off += len(run) * RECORD_SIZE
            continue
        off += 1
    return best


def _run_at(data: bytes, start: int) -> list[ScoreRecord]:
    """The longest valid record run beginning exactly at `start`."""
    first = _header(data, start)
    if first is None:
        return []
    turn0 = first[0]

    # The nations of the first turn define the cycle.
    order: list[int] = []
    off = start
    while True:
        head = _header(data, off)
        if head is None or head[0] != turn0:
            break
        if head[1] in order:
            break
        order.append(head[1])
        off += RECORD_SIZE
    group = len(order)
    if group < 2:
        return []

    out: list[ScoreRecord] = []
    index = 0
    while start + (index + 1) * RECORD_SIZE <= len(data):
        head = _header(data, start + index * RECORD_SIZE)
        if head is None:
            break
        if head[0] != turn0 + index // group or head[1] != order[index % group]:
            break
        out.append(parse_record(data, start + index * RECORD_SIZE))
        index += 1

    # Keep only whole turns, and only if the run is long enough to be real.
    turns = len(out) // group
    if turns < _MIN_TURNS:
        return []
    return out[: turns * group]


def _header(data: bytes, offset: int) -> tuple[int, int] | None:
    if offset + RECORD_SIZE > len(data):
        return None
    turn, nation = struct.unpack_from("<HH", data, offset)
    if turn > _MAX_TURN or not 0 < nation <= _MAX_NATION_ID:
        return None
    return turn, nation


def latest_by_nation(records: list[ScoreRecord]) -> dict[int, ScoreRecord]:
    """The most recent record for each nation, keyed by nation id."""
    out: dict[int, ScoreRecord] = {}
    for rec in records:
        if rec.nation not in out or rec.turn > out[rec.nation].turn:
            out[rec.nation] = rec
    return out


def history_for(records: list[ScoreRecord], nation: int) -> list[ScoreRecord]:
    """One nation's records, oldest turn first."""
    return sorted((r for r in records if r.nation == nation), key=lambda r: r.turn)
