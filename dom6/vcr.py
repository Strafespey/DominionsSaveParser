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
    return sections


def find_battles_in_file(path) -> list[VcrSection]:
    with open(path, "rb") as fh:
        return find_battles(fh.read())
