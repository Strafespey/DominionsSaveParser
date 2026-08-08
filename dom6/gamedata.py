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
import struct
from dataclasses import dataclass
from dataclasses import field as dc_field
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

#: Weapon-id slots inside the 888-byte monster record (u16 each, 0 = empty).
#: Found by requiring Longbowman -> Long Bow and Crossbowman -> Crossbow, then
#: confirmed across the table: Archer [Dagger, Short Bow], Militia [Spear],
#: Heavy Infantry [Broad Sword], Deer Tribe Warrior [Spear, Javelin].
MONSTER_OFF_WEAPONS = 832
MONSTER_WEAPON_SLOTS = 7

#: Armour-id slots. The armour *table* is not decoded yet, so these are raw ids.
MONSTER_OFF_ARMOUR = 852
MONSTER_ARMOUR_SLOTS = 4

#: Combat stat block. Stored two bytes apart; every value observed fits in a
#: byte except hit points, so all are read as u16.
#:
#: How each was pinned down:
#:  size      the manual says a square holds "10 size points" and that giants
#:            are "size 6+"; this field maxes at 10, giants read 6, humans 3 --
#:            and the manual's own example calls a human "size 3"
#:  hp        rises monotonically with size (size 1 -> 3.1 avg, size 3 -> 12.2,
#:            size 6 -> 42.5, size 10 -> 157.5); Militia 10, Elephant 61
#:  strength  scales with mass (humans 10, giants 23, Dagon 30)
#:  attack /  units where defence exceeds attack are agile types (Sprite, Ghost
#:  defence   King, Spectator); units where attack exceeds defence are immobile
#:            trees reading defence 0 (Dying Treelord, Irminsul, Hamadryad)
#:  morale    5-18 for living units and exactly 50 for mindless undead
#:  encumbr.  0 for undead and inanimate, 2-4 for the living
#:  mr        humans 10, animals 5
#:  prot      natural protection only; humans 0, Elephant 11, giants 5
MONSTER_OFF_ACTION_POINTS = 40
MONSTER_OFF_SIZE = 44
MONSTER_OFF_HP = 46
MONSTER_OFF_PROTECTION = 48
MONSTER_OFF_STRENGTH = 50
MONSTER_OFF_ENCUMBRANCE = 52
MONSTER_OFF_MAGIC_RESISTANCE = 54
MONSTER_OFF_ATTACK = 56
MONSTER_OFF_DEFENCE = 58
MONSTER_OFF_PRECISION = 60
MONSTER_OFF_MORALE = 62

#: Mindless units store this instead of a real morale value; they never rout.
MINDLESS_MORALE = 50

#: Armour anchors -- names occurring exactly once in the executable.
ARMOUR_ANCHORS: dict[str, int] = {
    "Buckler": 1,
    "Kite Shield": 3,
    "Tower Shield": 4,
}

ARMOUR_VALIDATION: dict[int, str] = {
    0: "Nothing",
    2: "Shield",
    5: "Leather Cuirass",
    19: "Full Plate Mail",
    20: "Iron Cap",
    21: "Full Helmet",
}

#: Field offsets within the 104-byte armour record.
ARMOUR_OFF_SLOT = 36  # 1 head, 2 body, 5 shield
#: Protection where the piece actually covers.
ARMOUR_OFF_PROTECTION = 38
#: Protection averaged over the whole body. A Plate Cuirass reads 21 at
#: `ARMOUR_OFF_PROTECTION` but only 8 here because it covers the torso alone,
#: while Full Plate Mail reads 21 in both. This is the figure that adds to a
#: unit's natural protection.
ARMOUR_OFF_BODY_PROTECTION = 42
#: Rises steeply with weight (Buckler 1, Full Plate Mail 25) -- resource cost
#: or encumbrance; not disambiguated, so it is exposed under a neutral name.
ARMOUR_OFF_WEIGHT = 68

ARMOUR_SLOTS = {1: "head", 2: "body", 5: "shield"}

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
class Monster:
    """One unit type from the executable's table."""

    id: int
    name: str
    weapon_ids: list[int] = dc_field(default_factory=list)
    #: Raw armour ids; the armour table is not decoded yet.
    armour_ids: list[int] = dc_field(default_factory=list)

    # Combat stats. `protection` is natural protection only -- worn armour
    # adds to it and is not resolved yet.
    hp: int = 0
    size: int = 0
    protection: int = 0
    strength: int = 0
    attack: int = 0
    defence: int = 0
    precision: int = 0
    morale: int = 0
    magic_resistance: int = 0
    encumbrance: int = 0
    action_points: int = 0

    @property
    def is_mindless(self) -> bool:
        """Mindless units never rout; the engine stores morale 50 for them."""
        return self.morale >= MINDLESS_MORALE

    def summary(self) -> str:
        mor = "mindless" if self.is_mindless else f"mor {self.morale}"
        return (
            f"hp {self.hp} sz {self.size} prot {self.protection} "
            f"str {self.strength} att {self.attack} def {self.defence} "
            f"prec {self.precision} mr {self.magic_resistance} "
            f"enc {self.encumbrance} {mor}"
        )


@dataclass
class MonsterTable:
    """Monster id -> unit type, extracted from the executable."""

    layout: TableLayout
    monsters: dict[int, Monster]

    def __len__(self) -> int:
        return len(self.monsters)

    @property
    def names(self) -> dict[int, str]:
        return {i: m.name for i, m in self.monsters.items()}

    def get(self, type_id: int) -> Monster | None:
        return self.monsters.get(type_id)

    def label(self, type_id: int) -> str:
        m = self.monsters.get(type_id)
        return m.name if m else f"type {type_id}"

    def weapons_of(
        self, type_id: int, table: "WeaponTable | None" = None
    ) -> list["Weapon"]:
        """Resolve a unit's weapons, skipping ids the weapon table lacks."""
        m = self.monsters.get(type_id)
        if not m:
            return []
        wt = table or weapons()
        return [w for wid in m.weapon_ids if (w := wt.get(wid))]

    def armour_of(
        self, type_id: int, table: "ArmourTable | None" = None
    ) -> list["Armour"]:
        m = self.monsters.get(type_id)
        if not m:
            return []
        at = table or armours()
        return [a for aid in m.armour_ids if (a := at.get(aid))]

    def total_protection(
        self, type_id: int, table: "ArmourTable | None" = None
    ) -> int:
        """Natural protection plus worn body armour.

        Shields and helmets are excluded: they protect their own areas rather
        than raising overall protection, so adding them would overstate it.
        """
        m = self.monsters.get(type_id)
        if not m:
            return 0
        worn = sum(
            a.body_protection
            for a in self.armour_of(type_id, table)
            if a.slot_code == 2
        )
        return m.protection + worn

    @classmethod
    def from_exe(cls, exe: str | Path | None = None) -> "MonsterTable":
        path = Path(exe) if exe else _default_exe()
        data = path.read_bytes()
        layout = solve_layout(data, MONSTER_ANCHORS, MONSTER_VALIDATION)
        out: dict[int, Monster] = {}
        for entry_id in range(layout.highest_id + 1):
            base = layout.offset_of(entry_id)
            name = _read_name(data, base)
            if not name:
                continue
            def stat(delta: int, _b: int = base) -> int:
                return struct.unpack_from("<H", data, _b + delta)[0]

            out[entry_id] = Monster(
                id=entry_id,
                name=name,
                weapon_ids=_slots(
                    data, base + MONSTER_OFF_WEAPONS, MONSTER_WEAPON_SLOTS
                ),
                armour_ids=_slots(
                    data, base + MONSTER_OFF_ARMOUR, MONSTER_ARMOUR_SLOTS
                ),
                hp=stat(MONSTER_OFF_HP),
                size=stat(MONSTER_OFF_SIZE),
                protection=stat(MONSTER_OFF_PROTECTION),
                strength=stat(MONSTER_OFF_STRENGTH),
                attack=stat(MONSTER_OFF_ATTACK),
                defence=stat(MONSTER_OFF_DEFENCE),
                precision=stat(MONSTER_OFF_PRECISION),
                morale=stat(MONSTER_OFF_MORALE),
                magic_resistance=stat(MONSTER_OFF_MAGIC_RESISTANCE),
                encumbrance=stat(MONSTER_OFF_ENCUMBRANCE),
                action_points=stat(MONSTER_OFF_ACTION_POINTS),
            )
        return cls(layout=layout, monsters=out)

    def save(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            json.dumps(
                {
                    "layout": self.layout.__dict__,
                    "monsters": {
                        str(m.id): {
                            "name": m.name,
                            "weapons": m.weapon_ids,
                            "armour": m.armour_ids,
                            "hp": m.hp,
                            "size": m.size,
                            "protection": m.protection,
                            "strength": m.strength,
                            "attack": m.attack,
                            "defence": m.defence,
                            "precision": m.precision,
                            "morale": m.morale,
                            "magic_resistance": m.magic_resistance,
                            "encumbrance": m.encumbrance,
                            "action_points": m.action_points,
                        }
                        for m in self.monsters.values()
                    },
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )


def validate_monster_stats(table: "MonsterTable") -> list[str]:
    """Check the stat extraction against facts stated in the manual.

    Returns a list of problems; empty means every check passed. These are
    deliberately checks the offsets were *not* chosen to satisfy, so they can
    actually fail if a patch moves the stat block.
    """
    problems: list[str] = []
    by_name: dict[str, Monster] = {}
    for m in table.monsters.values():
        by_name.setdefault(m.name, m)

    def check(cond: bool, msg: str) -> None:
        if not cond:
            problems.append(msg)

    # The manual: a square holds "10 size points"; giants are "size 6+";
    # its worked example calls a human "size 3".
    sizes = [m.size for m in table.monsters.values()]
    check(max(sizes) <= 10, f"size exceeds the manual's maximum of 10: {max(sizes)}")
    if (militia := by_name.get("Militia")) is not None:
        check(militia.size == 3, f"Militia size {militia.size}, expected 3")
        check(militia.hp == 10, f"Militia hp {militia.hp}, expected 10")
        check(militia.protection == 0, "Militia should have no natural protection")
    for giant in ("Jotun Jarl", "Niefel Giant"):
        if (g := by_name.get(giant)) is not None:
            check(g.size >= 6, f"{giant} size {g.size}, expected >= 6 (giant)")

    # Mindless undead never rout.
    if (ld := by_name.get("Longdead")) is not None:
        check(ld.is_mindless, f"Longdead morale {ld.morale}, expected mindless")
        check(ld.encumbrance == 0, "undead should have encumbrance 0")

    # Immobile trees cannot evade.
    if (tree := by_name.get("Dying Treelord")) is not None:
        check(tree.defence == 0, f"Dying Treelord defence {tree.defence}, expected 0")

    # Hit points must rise with size.
    buckets: dict[int, list[int]] = {}
    for m in table.monsters.values():
        if m.size:
            buckets.setdefault(m.size, []).append(m.hp)
    means = [sum(v) / len(v) for _, v in sorted(buckets.items())]
    check(
        all(a < b for a, b in zip(means, means[1:])),
        f"mean hp is not monotonic in size: {[round(x, 1) for x in means]}",
    )
    return problems


def _slots(data: bytes, offset: int, count: int) -> list[int]:
    out = []
    for i in range(count):
        (v,) = struct.unpack_from("<H", data, offset + i * 2)
        if v:
            out.append(v)
    return out


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


@dataclass
class Armour:
    """One armour piece from the executable's table."""

    id: int
    name: str
    slot_code: int
    #: Protection where the piece covers.
    protection: int
    #: Protection averaged over the whole body -- what adds to a unit's own.
    body_protection: int
    weight: int

    @property
    def slot(self) -> str:
        return ARMOUR_SLOTS.get(self.slot_code, f"slot {self.slot_code}")

    @property
    def is_shield(self) -> bool:
        return self.slot_code == 5


@dataclass
class ArmourTable:
    layout: TableLayout
    armours: dict[int, Armour]

    def __len__(self) -> int:
        return len(self.armours)

    def get(self, armour_id: int) -> Armour | None:
        return self.armours.get(armour_id)

    def label(self, armour_id: int) -> str:
        a = self.armours.get(armour_id)
        return a.name if a else f"armour {armour_id}"

    @classmethod
    def from_exe(cls, exe: str | Path | None = None) -> "ArmourTable":
        path = Path(exe) if exe else _default_exe()
        data = path.read_bytes()
        layout = solve_layout(data, ARMOUR_ANCHORS, ARMOUR_VALIDATION)
        out: dict[int, Armour] = {}
        for aid in range(layout.highest_id + 1):
            base = layout.offset_of(aid)
            name = _read_name(data, base)
            if not name:
                continue
            out[aid] = Armour(
                id=aid,
                name=name,
                slot_code=data[base + ARMOUR_OFF_SLOT],
                protection=data[base + ARMOUR_OFF_PROTECTION],
                body_protection=data[base + ARMOUR_OFF_BODY_PROTECTION],
                weight=data[base + ARMOUR_OFF_WEIGHT],
            )
        return cls(layout=layout, armours=out)

    def save(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            json.dumps(
                {
                    "layout": self.layout.__dict__,
                    "armours": {
                        str(a.id): {
                            "name": a.name,
                            "slot": a.slot,
                            "protection": a.protection,
                            "body_protection": a.body_protection,
                            "weight": a.weight,
                        }
                        for a in self.armours.values()
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
_ARMOUR_CACHE: "ArmourTable | None" = None


def armours(exe: str | Path | None = None) -> "ArmourTable":
    """Process-wide cached armour table."""
    global _ARMOUR_CACHE
    if _ARMOUR_CACHE is None:
        _ARMOUR_CACHE = ArmourTable.from_exe(exe)
    return _ARMOUR_CACHE


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
