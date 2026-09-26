"""Derived battle analysis: who fought, who did not come back.

Dominions does not store a casualty list. The replay records the state at
battle *start*, and the post-battle result is produced by re-simulating -- so
there is no "killed" flag to read (differencing casualties against survivors
finds no field that separates them).

Losses are therefore *inferred*: a unit that was engaged in a battle and is not
observed afterwards did not come back. That inference is sound for your own
army and unreliable for the enemy's, and this module keeps the distinction
explicit rather than presenting one number as if both were equally solid.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from .save import SaveFile
from .vcr import VcrSection, VcrUnit, find_unit_arrays


@dataclass
class SideOutcome:
    """One side's participation in a battle."""

    nation: int
    engaged: list[VcrUnit] = field(default_factory=list)
    lost: list[VcrUnit] = field(default_factory=list)
    #: True when this is the turn-file owner's own nation, where survivors are
    #: directly observable and the loss count is trustworthy.
    observable: bool = False

    @property
    def survived(self) -> int:
        return len(self.engaged) - len(self.lost)

    @property
    def lost_troops(self) -> list[VcrUnit]:
        """Losses the survivor scan can actually vouch for."""
        return [u for u in self.lost if not u.is_commander]

    @property
    def lost_commanders(self) -> list[VcrUnit]:
        """Commanders not found afterwards -- **not** confirmed dead.

        ⚠️ Commanders standing on the map are not stored as the 173-byte unit
        records `find_unit_arrays` scans for, so a surviving commander is
        routinely invisible to it and reads as a casualty. Measured on the
        turn-28 Nardago battle: 23 of 25 engaged commanders have their unit
        number present outside the replay bodies, yet the array scan vouched
        for only 10 and an identity-triple search for 3. The player confirmed
        that a commander this reported as lost -- a White Tiger of the West --
        survived the battle.

        Treat this list as "not seen afterwards, cause unknown". Mapping the
        commander records properly is tracked in docs/ROADMAP.md.
        """
        return [u for u in self.lost if u.is_commander]

    @property
    def losses_by_type(self) -> Counter:
        """Confirmed troop losses only; see `lost_commanders`."""
        return Counter(u.type_id for u in self.lost_troops)

    @property
    def loss_fraction(self) -> float:
        """Troop losses over troops engaged.

        Commanders are excluded on both sides of the ratio deliberately: they
        cannot be counted reliably (see `lost_commanders`), and folding an
        unreliable count into the headline percentage is what made an earlier
        report state a surviving pretender as dead.
        """
        troops = [u for u in self.engaged if not u.is_commander]
        return len(self.lost_troops) / len(troops) if troops else 0.0

    @property
    def caveat(self) -> str | None:
        if self.observable:
            return None
        return (
            "enemy survivors are not visible in your turn file, so this counts "
            "units you can no longer see, not confirmed kills"
        )


@dataclass
class BattleOutcome:
    battle: VcrSection
    sides: list[SideOutcome] = field(default_factory=list)

    @property
    def province(self) -> str | None:
        return self.battle.battlefield

    def side(self, nation: int) -> SideOutcome | None:
        return next((s for s in self.sides if s.nation == nation), None)


def _known_monster_ids() -> set[int] | None:
    """Real monster ids, for rejecting garbage unit arrays.

    Optional: the ids come from tables extracted from the game executable,
    which is not always present. Without them the array scan falls back to a
    weaker structural test, so this returns None rather than failing.
    """
    try:
        from .gamedata import monsters

        return set(monsters().monsters)
    except Exception:
        return None


def battle_outcomes(save: SaveFile) -> list[BattleOutcome]:
    """Infer per-battle losses from a turn file.

    A unit counts as lost in battle *i* when it fought there and appears
    neither in any later battle of the same turn nor among the units still
    standing on the map afterwards. Checking later battles matters: without it
    a unit that survived the first fight and died in the second would be
    charged to both.
    """
    battles = save.battles
    if not battles:
        return []

    spans = [(b.offset, b.end_offset or len(save.data)) for b in battles]
    alive: set[int] = set()
    for off, units in find_unit_arrays(
        save.data,
        min_length=2,
        known_types=_known_monster_ids(),
        exclude_spans=spans,
    ):
        if any(a <= off < b for a, b in spans):
            continue
        alive.update(u.unit_number for u in units)

    # Unit numbers seen in each battle, so later battles can vouch for a unit.
    seen_in = [{u.unit_number for u in b.units} for b in battles]

    out: list[BattleOutcome] = []
    for i, battle in enumerate(battles):
        later: set[int] = set()
        for j in range(i + 1, len(battles)):
            later |= seen_in[j]
        outcome = BattleOutcome(battle=battle)
        for nation in sorted({u.owner for u in battle.units}):
            engaged = [u for u in battle.units if u.owner == nation]
            lost = [
                u
                for u in engaged
                if u.unit_number not in alive and u.unit_number not in later
            ]
            outcome.sides.append(
                SideOutcome(
                    nation=nation,
                    engaged=engaged,
                    lost=lost,
                    observable=nation == save.header.nation,
                )
            )
        out.append(outcome)
    return out
