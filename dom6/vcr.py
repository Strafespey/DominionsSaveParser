"""Locating and decoding battle replay ("VCR") sections in Dominions 6 saves.

A Dominions battle is NOT stored as a blow-by-blow log. The engine stores the
battle *setup* plus an RNG seed and per-round checksums, and re-simulates the
fight deterministically whenever you watch the replay -- which is exactly why
replays break across patches (`--useolddata  Try to preserve battle replays
after upgrading`) and why the engine has a
`Battle inconsistency, round %d (calc %d, loaded %d)` check.

Each replay is introduced in the byte stream by the literal 8-byte ASCII marker
`_vcr_VCR` (NOT obfuscated), which makes replays easy to find even though the
record layout after the header is still being mapped.

Layout relative to the marker, as observed in real .trn files:

    +0x00  8   b"_vcr_VCR"
    +0x08  i32 version (4)
    +0x0C  i32 constant 50 so far
    +0x10  i32 nation id of one side   (0 == independents)   [verified]
    +0x14  i32 nation id of other side                        [verified]
    +0x18  i32 constant 2 so far  -- maybe the number of sides
    +0x1C  i32 RNG seed                                       [probable]
    +0x20  ... further numeric fields, meaning unknown
    +0x41  obfuscated battlefield name, repeated twice

`nation_a`/`nation_b` were confirmed by cross-checking against
`--listnations`: a turn-9 Bandar Log .trn contained one battle 0 vs 68
(independents vs Bandar Log) and one 68 vs 77 (Bandar Log vs Phaeacia), in the
province "Trackless Woods" whose event text reads "Trackless Woods was
conquered by Bandar Log".
"""

from __future__ import annotations

import struct
from collections import Counter
from dataclasses import dataclass, field

from .obfuscation import read_cstring

MARKER = b"_vcr_VCR"

#: Version int32 that follows the marker in Dominions 6 saves observed so far.
KNOWN_VERSION = 4

_OFF_VERSION = 0x08
_OFF_FIELDS = 0x0C
_OFF_NATION_A = 0x10
_OFF_NATION_B = 0x14
_OFF_SEED = 0x1C
_OFF_NAMES = 0x41


@dataclass
class VcrSection:
    """One battle replay found in a save file."""

    index: int
    offset: int  #: byte offset of the `_vcr_VCR` marker
    version: int
    nation_a: int  #: verified -- 0 means independents
    nation_b: int  #: verified
    seed: int  #: probable
    raw_fields: list[int] = field(default_factory=list)  #: int32s from +0x0C
    names: list[str] = field(default_factory=list)
    end_offset: int | None = None  #: offset of the next marker, or EOF
    units: list[VcrUnit] = field(default_factory=list)
    units_offset: int | None = None

    def order_of_battle(self) -> dict[int, dict[str, object]]:
        """Per-nation breakdown: commander count and units grouped by type id."""
        out: dict[int, dict[str, object]] = {}
        for u in self.units:
            side = out.setdefault(
                u.owner, {"commanders": 0, "units": 0, "by_type": Counter()}
            )
            if u.is_commander:
                side["commanders"] = int(side["commanders"]) + 1  # type: ignore[call-overload]
            else:
                side["units"] = int(side["units"]) + 1  # type: ignore[call-overload]
            side["by_type"][u.type_id] += 1  # type: ignore[index]
        return out

    @property
    def size(self) -> int | None:
        """Bytes until the next replay marker -- an upper bound, not the true length."""
        if self.end_offset is None:
            return None
        return self.end_offset - self.offset

    @property
    def battlefield(self) -> str | None:
        return self.names[0] if self.names else None

    @property
    def nations(self) -> tuple[int, int]:
        return (self.nation_a, self.nation_b)

    def describe(self, nation_names: dict[int, str] | None = None) -> str:
        def nm(n: int) -> str:
            if n == 0:
                return "Independents"
            if nation_names and n in nation_names:
                return nation_names[n].split(",")[0]
            return f"nation {n}"

        return (
            f"VCR #{self.index} @0x{self.offset:08x} v{self.version} "
            f"{nm(self.nation_a)} vs {nm(self.nation_b)} "
            f"in {self.battlefield or '?'!r} seed={self.seed}"
        )


# ---------------------------------------------------------------------
# Unit records inside a replay
# ---------------------------------------------------------------------

#: Size of one combatant record inside a VCR body. Established by measuring the
#: dominant repeat distance of u16 values across a replay body (1860 votes for
#: 173, next candidate 210 votes).
UNIT_RECORD_SIZE = 173

#: Byte +27 is identical across every record within one file (0x31 in a turn-10
#: .trn), which makes it a tempting anchor -- but it is NOT a constant magic:
#: a turn-9 .trn of the same game carries 50 there, and the same value appears
#: in the replay header. It tracks something game-global, so anchoring on a
#: hard-coded value silently finds nothing in other files. Records are located
#: by field plausibility instead.
_OFF_UNIT_TURNSTAMP = 27

_OFF_UNIT_LINK = 20  # u16, 0xFFFF on commanders
_OFF_UNIT_TYPE = 23  # u16, monster type id  [verified]
_OFF_UNIT_OWNER = 55  # u8, owning nation id [verified]
_OFF_UNIT_NUMBER = 164  # u16, per-game unit number


@dataclass
class VcrUnit:
    """One combatant in a battle replay.

    Field meanings were established by hosting a turn with `--dumpfights` to
    obtain a known roster, then matching the record array against it. For the
    battle in "The Mire of Mystery" the 145 records split exactly as
    Bandar Log 79 / Independents 66, and the type field grouped as
    30/24/12/12/1 and 26/22/15/3 -- matching the dumped roster of
    30 Atavi Infantry, 24 Vanara Infantry, 12 Tiger Rider (+12 mounts),
    1 commander, versus 26 Militia, 22 Light Infantry, 15 Archer, 3 Commander.

    `type_id` is a monster id; resolving it to a name needs the stat tables
    compiled into the executable, which are not extracted yet.
    """

    offset: int
    type_id: int
    owner: int  #: nation id; 0 == independents
    unit_number: int
    link: int  #: 0xFFFF on commanders; exact meaning unconfirmed
    raw: bytes = field(repr=False, default=b"")

    @property
    def is_commander(self) -> bool:
        """Commanders carry 0xFFFF in the link field.

        Verified: this selected exactly the 4 commanders (1 Bandar Log +
        3 Independent) that `--dumpfights` reported for the same battle.
        """
        return self.link == 0xFFFF


def find_unit_records(
    data: bytes,
    start: int,
    end: int,
    allowed_owners: set[int] | None = None,
) -> tuple[list[VcrUnit], int | None]:
    """Locate the combatant array within a replay body.

    Returns (units, array_offset). The array is found by taking the longest
    run of positions spaced `UNIT_RECORD_SIZE` apart that all carry the record
    signature byte, so it does not depend on knowing the size of the header
    that precedes it.

    `allowed_owners` (normally the replay's two nation ids) rejects candidate
    records whose owner field is not one of the battle's participants. Without
    it, a lone byte coincidence can outscore a genuine short array -- which is
    what happens on two-combatant assassination replays.
    """

    runs = _scan_runs(data, start, end, allowed_owners)
    if not runs:
        return [], None
    best_off, best_len = max(runs, key=lambda t: t[1])
    return _read_records(data, best_off, best_len), best_off


def _valid_record(data: bytes, off: int, allowed_owners: set[int] | None) -> bool:
    owner = data[off + _OFF_UNIT_OWNER]
    if allowed_owners is not None:
        if owner not in allowed_owners:
            return False
    elif owner > _MAX_NATION_ID:
        return False
    type_id = struct.unpack_from("<H", data, off + _OFF_UNIT_TYPE)[0]
    return 0 < type_id < _MAX_TYPE_ID


def _scan_runs(
    data: bytes, start: int, end: int, allowed_owners: set[int] | None
) -> list[tuple[int, int]]:
    """Maximal stride-spaced runs of records that share the +27 stamp.

    The stamp is derived from each run's first record instead of being
    hard-coded, because its value differs between files.
    """
    hits = {
        off
        for off in range(max(0, start), max(0, min(end, len(data)) - UNIT_RECORD_SIZE + 1))
        if _valid_record(data, off, allowed_owners)
    }
    runs: list[tuple[int, int]] = []
    for off in sorted(hits):
        stamp = data[off + _OFF_UNIT_TURNSTAMP]
        prev = off - UNIT_RECORD_SIZE
        if prev in hits and data[prev + _OFF_UNIT_TURNSTAMP] == stamp:
            continue  # not the head of a run
        n, p = 0, off
        while p in hits and data[p + _OFF_UNIT_TURNSTAMP] == stamp:
            n += 1
            p += UNIT_RECORD_SIZE
        runs.append((off, n))
    return runs


def _read_records(data: bytes, offset: int, count: int) -> list[VcrUnit]:
    units = []
    for i in range(count):
        o = offset + i * UNIT_RECORD_SIZE
        rec = data[o : o + UNIT_RECORD_SIZE]
        units.append(
            VcrUnit(
                offset=o,
                type_id=struct.unpack_from("<H", rec, _OFF_UNIT_TYPE)[0],
                owner=rec[_OFF_UNIT_OWNER],
                unit_number=struct.unpack_from("<H", rec, _OFF_UNIT_NUMBER)[0],
                link=struct.unpack_from("<H", rec, _OFF_UNIT_LINK)[0],
                raw=rec,
            )
        )
    return units


#: Sanity bounds used when scanning for unit arrays without knowing the owners.
#: The owner field is one byte, so 0xFF (seen on phase-shifted false matches)
#: is out of range for a real nation.
_MAX_NATION_ID = 250
_MAX_TYPE_ID = 40000

#: A genuine unit array belongs to at most this many nations.
_MAX_OWNERS_PER_ARRAY = 2


def find_unit_arrays(
    data: bytes, min_length: int = 4
) -> list[tuple[int, list[VcrUnit]]]:
    """Find every unit array in a save file, not just those inside replays.

    The 173-byte record is not replay-specific: the same layout is used for
    armies standing on the map. In a turn-9 Bandar Log .trn this finds the
    battle array plus several map stacks (e.g. 24 records of type 1125 owned
    by nation 68 -- a squad of Vanara Infantry).

    Returns a list of (offset, units), longest first.

    Because a record has no magic number, a run one byte away from a real array
    also parses as "plausible". Overlapping candidates are therefore resolved
    greedily in favour of the longest, which discards those phase-shifted
    duplicates.
    """
    def coherent(off: int, n: int) -> bool:
        """A real array is owned by at most a couple of nations.

        A run shifted a few bytes off a genuine array still passes the
        per-field plausibility test, but its "owner" column is really some
        other field and scatters across many values. Genuine arrays seen so
        far carry one or two owners (a battle has exactly two sides).
        """
        owners = {data[off + i * UNIT_RECORD_SIZE + _OFF_UNIT_OWNER] for i in range(n)}
        return len(owners) <= _MAX_OWNERS_PER_ARRAY

    runs = [
        r
        for r in _scan_runs(data, 0, len(data), None)
        if r[1] >= min_length and coherent(*r)
    ]
    runs.sort(key=lambda t: (-t[1], t[0]))

    kept: list[tuple[int, int]] = []
    for off, n in runs:
        span = (off, off + n * UNIT_RECORD_SIZE)
        if any(span[0] < k_end and k_off < span[1] for k_off, k_end in kept):
            continue
        kept.append(span)
        if len(kept) > 4096:
            break
    kept.sort()
    out = [
        (off, _read_records(data, off, (end - off) // UNIT_RECORD_SIZE))
        for off, end in kept
    ]
    out.sort(key=lambda t: -len(t[1]))
    return out


def find_markers(data: bytes) -> list[int]:
    """Return byte offsets of every `_vcr_VCR` marker, in file order."""
    offsets, start = [], 0
    while True:
        i = data.find(MARKER, start)
        if i < 0:
            return offsets
        offsets.append(i)
        start = i + 1


def parse_section(data: bytes, offset: int, index: int = 0) -> VcrSection:
    """Decode the portion of a replay header that is currently understood."""

    def i32(delta: int) -> int:
        return struct.unpack_from("<i", data, offset + delta)[0]

    version = i32(_OFF_VERSION)

    avail = max(0, (len(data) - (offset + _OFF_FIELDS)) // 4)
    raw_fields = list(
        struct.unpack_from(f"<{min(14, avail)}i", data, offset + _OFF_FIELDS)
    )

    names: list[str] = []
    pos = offset + _OFF_NAMES
    for _ in range(2):
        try:
            text, pos = read_cstring(data, pos, max_len=128)
        except (ValueError, IndexError):
            break
        if not text:
            break
        names.append(text)

    return VcrSection(
        index=index,
        offset=offset,
        version=version,
        nation_a=i32(_OFF_NATION_A),
        nation_b=i32(_OFF_NATION_B),
        seed=i32(_OFF_SEED),
        raw_fields=raw_fields,
        names=names,
    )


def find_battles(data: bytes) -> list[VcrSection]:
    """Find and decode every battle replay section in a save file."""
    offsets = find_markers(data)
    sections = [parse_section(data, off, i) for i, off in enumerate(offsets)]
    for i, sec in enumerate(sections):
        sec.end_offset = offsets[i + 1] if i + 1 < len(offsets) else len(data)
        sec.units, sec.units_offset = find_unit_records(
            data,
            sec.offset,
            sec.end_offset,
            allowed_owners={sec.nation_a, sec.nation_b},
        )
    return sections


def find_battles_in_file(path) -> list[VcrSection]:
    with open(path, "rb") as fh:
        return find_battles(fh.read())
