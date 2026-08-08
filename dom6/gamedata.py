"""Extracting the compiled game database from Dominions6.exe.

Unit, weapon and armour stats are not exposed by any command-line switch and
are not in the `data/` folder (which is art assets only). They are compiled
into the executable as an array of fixed-size structs with the names stored
**inline**, not behind pointers.

The monster table was located by cross-referencing type ids proven from real
savegames: a battle whose roster was known from `--dumpfights` established
that type 1122 is "Atavi Infantry", 1141 is "Tiger Rider", and so on. Finding
those strings in the executable and dividing the gaps by the id differences
gives the record stride and the array base.

Rather than hard-coding those addresses -- which would silently break on the
next patch -- the table is re-derived at run time from the anchors below and
then checked against ids that were *not* used to derive it. If validation
fails the extraction is refused rather than returning wrong names.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .paths import find_game_dir

#: Unique monster names whose ids were proven from savegame battle records.
#: Used to solve for (base, stride). Each must occur exactly once in the exe.
MONSTER_ANCHORS: dict[str, int] = {
    "Atavi Infantry": 1122,
    "Vanara Infantry": 1125,
    "Tiger Rider": 1141,
}

#: Ids deliberately NOT used to derive the layout, checked afterwards.
#: All were confirmed against `--dumpfights` rosters.
MONSTER_VALIDATION: dict[int, str] = {
    17: "Archer",
    28: "Light Infantry",
    30: "Militia",
    40: "Heavy Infantry",
    428: "Assassin",
    1135: "Bandar Commander",
    1594: "Deer Tribe Warrior",
    3550: "Armored Sacred Tiger",
}

#: Weapon anchors -- names that occur exactly once in the executable.
#: Ids follow Dominions' documented weapon numbering (1 = Spear).
WEAPON_ANCHORS: dict[str, int] = {
    "Quarterstaff": 7,
    "Long Bow": 24,
    "Crossbow": 25,
}

WEAPON_VALIDATION: dict[int, str] = {
    0: "Nothing",
    1: "Spear",
    2: "Pike",
    9: "Dagger",
    12: "Mace",
    18: "Battleaxe",
    26: "Arbalest",
}

#: Field offsets within the 152-byte weapon record.
#: `length` is confirmed by the manual, which states a mace has length 1 and a
#: pike is a long weapon; `range` by the classic bow/sling values.
WEAPON_OFF_LENGTH = 54
WEAPON_OFF_RANGE = 56

#: Natural weapons (claws, bites) store 0xFF here. The manual describes them as
#: "weapon length zero", so 0xFF is a sentinel, not a length of 255.
_NATURAL_LENGTH = 0xFF

#: Missile range sentinels: javelins and boulders derive range from strength.
_RANGE_SENTINELS = {0xFF, 0xFD}

_NAME_RE = re.compile(rb"^[\x20-\x7e]{1,63}\x00")
_MIN_STRIDE, _MAX_STRIDE = 64, 8192
_MAX_ID = 20000


class GameDataError(RuntimeError):
    pass


@dataclass
class TableLayout:
    """Where a struct array lives in the executable."""

    base: int  #: file offset of the name field for id 0
    stride: int
    highest_id: int

    def offset_of(self, entry_id: int) -> int:
        return self.base + entry_id * self.stride


def _read_name(data: bytes, off: int) -> str | None:
    if off < 0 or off + 64 > len(data):
        return None
    m = _NAME_RE.match(data[off : off + 64])
    return m.group()[:-1].decode("ascii") if m else None


def _unique_offset(data: bytes, name: str) -> int | None:
    """Offset of `name` if it appears exactly once as a NUL-delimited string."""
    needle = b"\x00" + name.encode("ascii") + b"\x00"
    first = data.find(needle)
    if first < 0 or data.find(needle, first + 1) >= 0:
        return None
    return first + 1


def solve_layout(
    data: bytes,
    anchors: dict[str, int],
    validation: dict[int, str],
) -> TableLayout:
    """Derive (base, stride) from anchors, then verify against other ids."""
    located = {
        name: off
        for name, entry_id in anchors.items()
        if (off := _unique_offset(data, name)) is not None
    }
    if len(located) < 2:
        raise GameDataError(
            f"need >=2 uniquely-locatable anchors, found {sorted(located)}. "
            "The executable may have changed; update MONSTER_ANCHORS."
        )

    names = sorted(located)
    candidates: set[tuple[int, int]] = set()
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            d_off = located[a] - located[b]
            d_id = anchors[a] - anchors[b]
            if d_id == 0 or d_off % d_id:
                continue
            stride = d_off // d_id
            if not _MIN_STRIDE <= stride <= _MAX_STRIDE:
                continue
            candidates.add((located[a] - anchors[a] * stride, stride))

    for base, stride in sorted(candidates):
        if base < 0:
            continue
        layout = TableLayout(base=base, stride=stride, highest_id=0)
        if all(
            _read_name(data, layout.offset_of(i)) == want
            for i, want in validation.items()
        ):
            layout.highest_id = _find_highest_id(data, layout)
            return layout

    raise GameDataError(
        "derived a table layout but it failed validation against known ids; "
        "refusing to return names that would be wrong"
    )


def _find_highest_id(data: bytes, layout: TableLayout, tolerance: int = 64) -> int:
    highest, miss, entry_id = 0, 0, 0
    while miss < tolerance and entry_id < _MAX_ID:
        if layout.offset_of(entry_id) + 64 >= len(data):
            break
        if _read_name(data, layout.offset_of(entry_id)):
            highest, miss = entry_id, 0
        else:
            miss += 1
        entry_id += 1
    return highest


@dataclass
class MonsterTable:
    """Monster id -> name, extracted from the executable."""

    layout: TableLayout
    names: dict[int, str]

    def __len__(self) -> int:
        return len(self.names)

    def get(self, type_id: int, default: str | None = None) -> str | None:
        return self.names.get(type_id, default)

    def label(self, type_id: int) -> str:
        return self.names.get(type_id) or f"type {type_id}"

    @classmethod
    def from_exe(cls, exe: str | Path | None = None) -> "MonsterTable":
        path = Path(exe) if exe else _default_exe()
        data = path.read_bytes()
        layout = solve_layout(data, MONSTER_ANCHORS, MONSTER_VALIDATION)
        names = {}
        for entry_id in range(layout.highest_id + 1):
            name = _read_name(data, layout.offset_of(entry_id))
            if name:
                names[entry_id] = name
        return cls(layout=layout, names=names)

    @classmethod
    def load(cls, path: str | Path) -> "MonsterTable":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(
            layout=TableLayout(**raw["layout"]),
            names={int(k): v for k, v in raw["names"].items()},
        )

    def save(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            json.dumps(
                {"layout": self.layout.__dict__, "names": self.names},
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )


@dataclass
class Weapon:
    """One weapon from the executable's table."""

    id: int
    name: str
    #: Melee reach. `None` for natural weapons (claws, bites), which the manual
    #: treats as length zero and which are consequently easy to repel.
    length: int | None
    #: Missile range in map units, or `None` for melee / strength-derived range.
    range: int | None

    @property
    def is_missile(self) -> bool:
        return self.range is not None

    @property
    def effective_length(self) -> int:
        """Length for repel purposes; natural weapons count as zero."""
        return self.length or 0


@dataclass
class WeaponTable:
    layout: TableLayout
    weapons: dict[int, Weapon]

    def __len__(self) -> int:
        return len(self.weapons)

    def get(self, weapon_id: int) -> Weapon | None:
        return self.weapons.get(weapon_id)

    def label(self, weapon_id: int) -> str:
        w = self.weapons.get(weapon_id)
        return w.name if w else f"weapon {weapon_id}"

    @classmethod
    def from_exe(cls, exe: str | Path | None = None) -> "WeaponTable":
        path = Path(exe) if exe else _default_exe()
        data = path.read_bytes()
        layout = solve_layout(data, WEAPON_ANCHORS, WEAPON_VALIDATION)
        weapons: dict[int, Weapon] = {}
        for wid in range(layout.highest_id + 1):
            off = layout.offset_of(wid)
            name = _read_name(data, off)
            if not name:
                continue
            raw_len = data[off + WEAPON_OFF_LENGTH]
            raw_rng = data[off + WEAPON_OFF_RANGE]
            weapons[wid] = Weapon(
                id=wid,
                name=name,
                length=None if raw_len == _NATURAL_LENGTH else raw_len,
                range=None if raw_rng in _RANGE_SENTINELS or raw_rng == 0 else raw_rng,
            )
        return cls(layout=layout, weapons=weapons)

    def save(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            json.dumps(
                {
                    "layout": self.layout.__dict__,
                    "weapons": {
                        str(w.id): {
                            "name": w.name,
                            "length": w.length,
                            "range": w.range,
                        }
                        for w in self.weapons.values()
                    },
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )


def _default_exe() -> Path:
    game = find_game_dir()
    if not game:
        raise GameDataError("could not locate the Dominions 6 install")
    for name in ("Dominions6.exe", "dom6_amd64", "dom6_mac"):
        if (game / name).exists():
            return game / name
    raise GameDataError(f"no Dominions 6 executable in {game}")


_MONSTER_CACHE: MonsterTable | None = None
_WEAPON_CACHE: WeaponTable | None = None


def monsters(exe: str | Path | None = None) -> MonsterTable:
    """Process-wide cached monster table."""
    global _MONSTER_CACHE
    if _MONSTER_CACHE is None:
        _MONSTER_CACHE = MonsterTable.from_exe(exe)
    return _MONSTER_CACHE


def weapons(exe: str | Path | None = None) -> WeaponTable:
    """Process-wide cached weapon table."""
    global _WEAPON_CACHE
    if _WEAPON_CACHE is None:
        _WEAPON_CACHE = WeaponTable.from_exe(exe)
    return _WEAPON_CACHE
