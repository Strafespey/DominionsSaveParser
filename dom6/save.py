"""Top-level Dominions 6 savegame parsing.

Only the parts that have been verified against real files are decoded into
named fields. Everything else is deliberately left as raw bytes/offsets rather
than being guessed at -- see docs/FILE_FORMAT.md for the open questions.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from .obfuscation import deobfuscate, read_cstring
from .reader import Cursor
from .scores import ScoreRecord, find_score_history
from .vcr import VcrSection, find_battles

MAGIC = b"DOM"
MAGIC_OFFSET = 3
PREAMBLE = bytes((0x01, 0x02, 0x04))

#: Version short at offset 6. 6001 == Dominions 6.
VERSION_DOM6 = 6001


class SaveFormatError(ValueError):
    pass


#: Byte offset of the obfuscated game-name string. Verified across
#: ftherlnd/.trn/.2h files from three different games.
GAME_NAME_OFFSET = 0x26


@dataclass
class SaveHeader:
    """Decoded save header.

    Verified fields: `version`, `turn`, `nation`. The `unknown_*` fields are
    real values at known offsets whose *meaning* is still unproven -- the
    leading hypotheses are noted on each.
    """

    preamble: bytes
    version: int  #: 6001 for Dominions 6
    turn: int  #: offset 0x0E -- verified (9 / 1 / 0 across known games)
    nation: int  #: offset 0x1A -- verified: owning nation id, -1 in ftherlnd
    game_name: str | None = None

    unknown_08: int = 0  #: u16, always 2 so far
    unknown_0a: int = 0  #: per-game constant (627, 636) -- maybe province count
    unknown_12: int = 0  #: 1 in ftherlnd/.trn, 0 in .2h
    unknown_16: int = 0  #: per-game constant (11036, 20847) -- maybe map seed
    unknown_1e: int = 0  #: 1 in .2h only
    unknown_22: int = 0  #: nonzero only in .2h -- maybe an orders checksum

    @property
    def is_dominions6(self) -> bool:
        return self.version == VERSION_DOM6

    @property
    def is_master(self) -> bool:
        """ftherlnd carries nation == -1."""
        return self.nation < 0

    @property
    def unknown_words(self) -> list[int]:
        return [
            self.unknown_08,
            self.unknown_0a,
            self.unknown_12,
            self.unknown_16,
            self.unknown_1e,
            self.unknown_22,
        ]


@dataclass
class SaveFile:
    path: Path
    data: bytes
    header: SaveHeader
    battles: list[VcrSection] = field(default_factory=list)
    _scores: list[ScoreRecord] | None = field(default=None, repr=False)

    @property
    def kind(self) -> str:
        if self.path.name == "ftherlnd":
            return "master"
        return {".trn": "turn", ".2h": "orders"}.get(self.path.suffix, "unknown")

    @property
    def battle_count(self) -> int:
        return len(self.battles)

    def scores(self) -> list[ScoreRecord]:
        """The score-graph history: one record per nation per turn.

        Present in `ftherlnd` and `.trn` files; a `.2h` carries orders only,
        so this returns an empty list for one. The newest record lags the
        header turn by one, because the array is appended to when the host
        generates the following turn.

        The scan is not free (~0.2s on a turn file), so the result is cached.
        """
        cached = self._scores
        if cached is None:
            cached = find_score_history(self.data)
            self._scores = cached
        return cached

    def strings(
        self,
        min_len: int = 4,
        limit: int | None = None,
        clean: bool = True,
    ) -> list[tuple[int, str]]:
        """Every obfuscated string in the file, as (offset, text).

        This is an *exploration* aid, not a structural parser. Numeric bytes
        frequently decode to printable characters, so a scan like this always
        reports some false positives. `clean=True` applies a word-shaped
        heuristic to suppress the worst of them; pass `clean=False` to see
        everything.
        """
        data = self.data
        out: list[tuple[int, str]] = []
        pos = 0
        while True:
            end = data.find(_TERMINATOR, pos)
            if end < 0:
                break
            pos = end + 1
            start = _walk_back(data, end)
            if end - start < min_len:
                continue
            text = deobfuscate(data[start:end]).decode("utf-8", errors="replace")
            if clean and not _word_shaped(text):
                continue
            out.append((start, text))
            if limit and len(out) >= limit:
                break
        return out

    def describe(self) -> str:
        return (
            f"{self.path.name} [{self.kind}] "
            f"v{self.header.version} game={self.header.game_name!r} "
            f"battles={self.battle_count} size={len(self.data)}"
        )


#: A string ends at a raw 0x4F byte (0x00 ^ 0x4F).
_TERMINATOR = bytes((0x4F,))

#: Conservative alphabet a real game string is built from.
_TEXT_CHARS = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    " '.,!?:;()/&_-+#"
)

#: Three consecutive raw 0x00 bytes are padding, not the letter 'O'.
_MAX_ZERO_RUN = 3


def _walk_back(data: bytes, end: int) -> int:
    """Find the plausible start of the string terminating at `end`.

    Walks backwards while bytes decode into the conservative text alphabet,
    stopping at a run of raw 0x00 padding, then trims any leading padding.
    """
    start = end
    zeros = 0
    while start > 0:
        b = data[start - 1]
        if chr(b ^ 0x4F) not in _TEXT_CHARS:
            break
        zeros = zeros + 1 if b == 0x00 else 0
        if zeros >= _MAX_ZERO_RUN:
            break
        start -= 1
    while start < end and data[start] in (0x00, 0xFF):
        start += 1
    return start


def _word_shaped(text: str) -> bool:
    """Heuristic: does this look like real game text rather than decoded noise?

    Requires a run of at least three consecutive letters and a majority of
    letters/spaces/common punctuation.
    """
    run = best = 0
    for ch in text:
        run = run + 1 if ch.isalpha() else 0
        best = max(best, run)
    if best < 3:
        return False
    ok = sum(ch.isalnum() or ch in " .,'!?:;()/-_" for ch in text)
    return ok / len(text) >= 0.75


def parse_header(data: bytes) -> SaveHeader:
    if data[MAGIC_OFFSET : MAGIC_OFFSET + 3] != MAGIC:
        raise SaveFormatError(
            f"missing 'DOM' magic at offset {MAGIC_OFFSET}; "
            f"got {data[:8]!r} -- not a Dominions savegame?"
        )
    cur = Cursor(data)
    preamble = cur.raw(3)
    cur.skip(3)  # "DOM"
    version = cur.u16()
    unknown_08 = cur.u16()  # 0x08
    unknown_0a = cur.i32()  # 0x0A
    turn = cur.i32()  # 0x0E
    unknown_12 = cur.i32()  # 0x12
    unknown_16 = cur.i32()  # 0x16
    nation = cur.i32()  # 0x1A
    unknown_1e = cur.i32()  # 0x1E
    unknown_22 = cur.i32()  # 0x22

    try:
        game_name, _ = read_cstring(data, GAME_NAME_OFFSET, max_len=128)
    except (ValueError, IndexError):
        game_name = None

    return SaveHeader(
        preamble=preamble,
        version=version,
        turn=turn,
        nation=nation,
        game_name=game_name,
        unknown_08=unknown_08,
        unknown_0a=unknown_0a,
        unknown_12=unknown_12,
        unknown_16=unknown_16,
        unknown_1e=unknown_1e,
        unknown_22=unknown_22,
    )


def load(path: str | os.PathLike) -> SaveFile:
    """Load and parse the understood parts of a Dominions 6 save file."""
    p = Path(path)
    data = p.read_bytes()
    header = parse_header(data)
    return SaveFile(path=p, data=data, header=header, battles=find_battles(data))
