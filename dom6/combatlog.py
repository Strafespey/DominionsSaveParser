"""Parse the engine's per-hit combat log (`log.txt`).

The savegame provably contains no blow-by-blow record (`docs/FILE_FORMAT.md`
§4) — it stores the battle setup plus an RNG seed and re-simulates on replay.
The narrative only exists while the engine is running with `--vcrdebug -d -d -d`,
and it is written to **`log.txt` in the game directory**, not to stdout.

This module turns that text into structured events.

The line grammar below was taken from the engine's own format strings rather
than from samples, so it covers cases the sample logs happen not to contain
(shield hits, trample, repel failures, individual rout checks)::

    %s hit %s in %s with %s for %d points of damage %s
    %s hit %s on the shield and %s with %s for %d points of damage %s
    %s missed %s
    %s trampled %s for %d points of damage
    %s attacks with %s
    %s casts %s
    %s repels %s (%s repelling %s)
    %s missed to repel %s (%d vs %d)
    %s's attack with %s was repelled by %s
    %s failed an individual rout check. (%d+%d vs %d+%d)
    Army rout (%d) for %s

⚠️ Units are identified **by name only**. The log does not carry unit ids, so
two Red Guards in the same battle are indistinguishable. Per-unit-type totals
are reliable; "this particular soldier" is not.

⚠️ Every message the viewer puts on screen is *also* written to the log a
second time, wrapped in the renderer's text-cache chatter::

    creating new text tex 'Red Guard hit Gladiator in body with Lance for 12
    points of damage (target was killed)' (482*15) forcep2 0
    puttextincache f8 'Red Guard hit Gladiator in body ...'

Those echoes are duplicates of a plain line, verified against a real 798k-line
capture: 110 of the 112 echoed payloads matched a plain line byte for byte.
Parsing them counts every on-screen event two or three times, so they are
dropped before matching. The narrow exception is that the echo is the only
place some modifier text appears, which is why the blunt-damage bonus below is
matched inside the quotes as well.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field

__all__ = [
    "Hit",
    "Miss",
    "Repel",
    "RoutCheck",
    "ArmyRout",
    "Cast",
    "Attack",
    "Environmental",
    "CombatLog",
    "parse",
    "parse_lines",
    "parse_file",
]


# --------------------------------------------------------------------------
# events
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Hit:
    """One landed attack.

    `damage` is what actually got through, after protection and after the
    hit-area cap. `capped_from` is set when the engine reported reducing the
    damage because it exceeded what the struck area can take — a rule the
    manual does not state, and the reason limb hits from heavy cavalry land so
    softly.
    """

    attacker: str
    target: str
    location: str | None
    weapon: str | None
    damage: int
    killed: bool = False
    ranged: bool = False
    shield_hit: bool = False
    shield_reduction: int | None = None
    capped_from: int | None = None
    blunt_bonus: int | None = None
    damage_roll: tuple[int, int] | None = None
    prot_roll: tuple[int, int] | None = None
    line_no: int = 0
    round_no: int | None = None

    @property
    def blocked(self) -> bool:
        """True when the attack connected but did no damage."""
        return self.damage <= 0


@dataclass(frozen=True)
class Miss:
    """An attack that connected with nothing (``%s missed %s``).

    Distinct from a landed hit for 0 damage: this one never touched the
    target, so it says something about attack-versus-defence, whereas a
    zero-damage hit says something about protection.
    """

    attacker: str
    target: str
    line_no: int = 0
    round_no: int | None = None


@dataclass(frozen=True)
class Repel:
    """A long-weapon repel (manual p.62-63)."""

    repeller: str
    attacker: str
    succeeded: bool
    weapon: str | None = None
    rolls: tuple[int, int] | None = None
    line_no: int = 0
    round_no: int | None = None


@dataclass(frozen=True)
class RoutCheck:
    unit: str
    passed: bool
    rolls: tuple[int, int, int, int] | None = None
    line_no: int = 0
    round_no: int | None = None


@dataclass(frozen=True)
class ArmyRout:
    nation: str
    value: int
    hp_rout: bool = False
    line_no: int = 0
    round_no: int | None = None


@dataclass(frozen=True)
class Cast:
    caster: str
    spell: str
    line_no: int = 0
    round_no: int | None = None


@dataclass(frozen=True)
class Attack:
    """An attack *attempt* (`%s attacks with %s`).

    Emitted whether or not the attack lands, so attempts minus landed hits is
    the miss count. Repelled attacks abort before resolving (manual p.62-63),
    so they show up here as attempts with no matching hit.
    """

    attacker: str
    weapon: str | None
    line_no: int = 0
    round_no: int | None = None


@dataclass(frozen=True)
class Environmental:
    """Damage from something other than a direct attack."""

    unit: str
    damage: int
    source: str  # burning, decay, maggots, lingering poison, excessive fatigue
    line_no: int = 0
    round_no: int | None = None


# --------------------------------------------------------------------------
# patterns
# --------------------------------------------------------------------------

_RE_HIT = re.compile(
    r"^(?P<attacker>.+?) hit (?P<target>.+?)"
    r"(?: on the shield and (?P<shieldloc>[\w ]+?))?"
    r"(?: with a ranged attack \((?P<rweapon>[^)]+)\))?"
    r"(?: in (?:the )?(?P<location>[\w ]+?))?"
    r"(?: with (?P<weapon>.+?))?"
    r" for (?P<damage>-?\d+)(?: points?(?: of damage)?)?"
    r"\s*(?P<tail>.*)$"
)

_RE_TRAMPLE = re.compile(
    r"^(?P<attacker>.+?) trampled (?P<target>.+?) for (?P<damage>-?\d+) points? of damage\s*(?P<tail>.*)$"
)

_RE_DAMAGE_ROLL = re.compile(
    r"^Damage roll (?P<da>-?\d+)\+(?P<db>-?\d+) vs prot roll of (?P<pa>-?\d+)\+(?P<pb>-?\d+)"
    r" of (?P<target>.+?) = (?P<result>-?\d+) points? of damage"
)

_RE_CAP = re.compile(
    r"^Damage exceeded maximum possible in hit area, reduced to (?P<to>-?\d+) points?"
)

_RE_SHIELD = re.compile(r"^Shield hit, incoming damage reduced by (?P<by>-?\d+)")

#: Blunt weapons hitting the head get a bonus the manual does not quantify.
#: Only ever seen inside the renderer echo, so it is matched there too.
_RE_BLUNT = re.compile(
    r"Damage increased by (?P<by>-?\d+) due to blunt hit in the (?P<where>\w+)"
)

#: The viewer writes every on-screen message to the log a second time, wrapped
#: in text-cache chatter. These are duplicates of a plain line and must be
#: dropped or every event is counted two or three times. See the module
#: docstring.
_RE_UI_ECHO = re.compile(r"^(?:creating new text tex|puttextincache(?: f\d+)?) '")

#: The engine writes the log from more than one buffer, so an echo's opening
#: is sometimes cut off mid-word and the line starts partway through a unit
#: name ("al Crossbowman hit ..."). What survives is the closing signature, so
#: that is what identifies them. Checked against a real capture: 19 of the 20
#: truncated combat echoes duplicated a plain line exactly. The 20th is simply
#: lost -- recovering a name from its own tail needs the battle roster, which
#: this module deliberately does not know about (see scripts/friendly_fire.py).
_RE_UI_ECHO_TAIL = re.compile(r"' \(\d+\*\d+\) forcep2 \d+\s*$")

_RE_REPEL_OK = re.compile(
    r"^(?P<repeller>.+?) repels (?P<attacker>.+?) \((?P<r2>.+?) repelling (?P<a2>.+?)\)\s*$"
)
_RE_REPEL_MISS = re.compile(
    r"^(?P<repeller>.+?) missed to repel (?P<attacker>.+?) \((?P<a>-?\d+) vs (?P<b>-?\d+)\)"
)
_RE_REPELLED = re.compile(
    r"^(?P<attacker>.+?)'s attack with (?P<weapon>.+?) was repelled by (?P<repeller>.+?)\s*$"
)

#: Must be tried only after the repel patterns -- "missed to repel" would
#: otherwise parse as a miss against a target called "to repel X".
_RE_MISS = re.compile(r"^(?P<attacker>.+?) missed (?P<target>.+?)\s*$")

_RE_ROUTCHK = re.compile(
    r"^(?P<unit>.+?) (?P<res>failed|passed) an individual rout check\. "
    r"\((?P<a>-?\d+)\+(?P<b>-?\d+) vs (?P<c>-?\d+)\+(?P<d>-?\d+)\)"
)
_RE_ARMYROUT = re.compile(r"^Army rout (?:\((?P<v1>-?\d+)\)|(?P<v2>-?\d+)) for (?P<nation>.+?)\s*(?P<tail>\(HP rout\))?\s*$")

_RE_CAST = re.compile(r"^(?P<caster>.+?) casts (?P<spell>.+?)\s*$")
_RE_ATTACKS_WITH = re.compile(r"^(?P<attacker>.+?) attacks with (?P<weapon>.+?)\s*$")

_RE_ENV = re.compile(
    r"^(?P<unit>.+?) took (?P<damage>-?\d+) points? of damage from (?P<source>.+?)\s*$"
)
_RE_FATIGUE_DMG = re.compile(
    r"^(?P<unit>.+?) (?:takes|took) (?P<damage>-?\d+) points? of damage from excessive fatigue"
)

# Round / battle delimiters. TickBattle advances the battle clock; Playvcr
# marks the start of a replayed battle.
_RE_TICK = re.compile(r"^TickBattle (?P<t>-?\d+)")
_RE_PLAYVCR = re.compile(r"^Playvcr lnr(?P<lnr>-?\d+)")

# Noise we deliberately drop.
_RE_NOISE = re.compile(r"^(hms \d+, crc \d+|\s*$)")

# A real log is ~1.5M lines and most of them are debug chatter that matches
# nothing below. One literal-alternation scan is far cheaper than trying every
# pattern in turn, so lines that cannot possibly be events are dropped first.
# Every needle here must appear in at least one of the patterns above.
_RE_INTERESTING = re.compile(
    r" hit | missed | attacks with |Damage roll |Damage exceeded|Shield hit,"
    r"| trampled | repel|rout check|Army rout | casts | of damage from "
    r"|excessive fatigue|Damage increased|TickBattle |Playvcr "
)


def _clean(s: str | None) -> str | None:
    if s is None:
        return None
    s = s.strip()
    return s or None


# --------------------------------------------------------------------------
# the log
# --------------------------------------------------------------------------


@dataclass
class CombatLog:
    """Structured view of one `log.txt`.

    A single log may contain more than one battle if more than one replay was
    watched (or if the run hosted a turn). `battle_index` on each event is not
    available — instead use :meth:`split_battles`, which cuts on the engine's
    own ``Playvcr`` markers.
    """

    hits: list[Hit] = field(default_factory=list)
    misses: list[Miss] = field(default_factory=list)
    repels: list[Repel] = field(default_factory=list)
    rout_checks: list[RoutCheck] = field(default_factory=list)
    army_routs: list[ArmyRout] = field(default_factory=list)
    casts: list[Cast] = field(default_factory=list)
    attacks: list[Attack] = field(default_factory=list)
    environmental: list[Environmental] = field(default_factory=list)
    playvcr_lines: list[int] = field(default_factory=list)
    tick_lines: list[int] = field(default_factory=list)
    ticks: int = 0
    lines_read: int = 0
    lines_matched: int = 0

    # -- aggregate views ---------------------------------------------------

    @property
    def rounds(self) -> int:
        """Number of battle ticks seen. The engine ticks faster than once per
        'round' in the manual's sense, so treat this as a duration proxy."""
        return self.ticks

    def damage_dealt(self) -> dict[str, int]:
        out: Counter[str] = Counter()
        for h in self.hits:
            out[h.attacker] += max(0, h.damage)
        return dict(out.most_common())

    def damage_taken(self) -> dict[str, int]:
        out: Counter[str] = Counter()
        for h in self.hits:
            out[h.target] += max(0, h.damage)
        for e in self.environmental:
            out[e.unit] += max(0, e.damage)
        return dict(out.most_common())

    def kills(self) -> dict[str, int]:
        out: Counter[str] = Counter()
        for h in self.hits:
            if h.killed:
                out[h.attacker] += 1
        return dict(out.most_common())

    def deaths(self) -> dict[str, int]:
        out: Counter[str] = Counter()
        for h in self.hits:
            if h.killed:
                out[h.target] += 1
        return dict(out.most_common())

    def hit_rate(self) -> dict[str, tuple[int, int, float]]:
        """Per attacker: (attempts, landed, rate).

        Attempts come from the engine's ``%s attacks with %s`` line, which
        fires whether or not the blow connects — so this separates *missing*
        from *failing to hurt*. Only populated for attackers that appear in
        both streams; a unit with attempts but no hits reads as 0%.
        """
        attempts: Counter[str] = Counter(a.attacker for a in self.attacks)
        landed: Counter[str] = Counter(h.attacker for h in self.hits)
        out: dict[str, tuple[int, int, float]] = {}
        for who, n in attempts.items():
            got = landed.get(who, 0)
            out[who] = (n, got, got / n if n else 0.0)
        return dict(sorted(out.items(), key=lambda kv: -kv[1][0]))

    def accuracy(self) -> dict[str, tuple[int, int, float]]:
        """Per attacker: (swings, landed, rate), from explicit miss lines.

        More trustworthy than :meth:`hit_rate`, which infers misses from
        attempts that produced no hit and so also absorbs repelled and
        interrupted attacks. Only attackers the engine actually reported
        missing with appear here.

        ⚠️ **Melee only.** The engine emits ``%s missed %s`` for melee but not
        for missile fire, so archers and crossbowmen come out at a spurious
        100%. A ranged unit's arrows that hit nothing are invisible here; use
        :meth:`blocked_ratio` to judge missile troops instead.
        """
        landed: Counter[str] = Counter(h.attacker for h in self.hits)
        missed: Counter[str] = Counter(m.attacker for m in self.misses)
        out: dict[str, tuple[int, int, float]] = {}
        for who in set(landed) | set(missed):
            got, lost = landed.get(who, 0), missed.get(who, 0)
            swings = got + lost
            out[who] = (swings, got, got / swings if swings else 0.0)
        return dict(sorted(out.items(), key=lambda kv: -kv[1][0]))

    def hit_locations(self) -> dict[str, int]:
        return dict(
            Counter(h.location for h in self.hits if h.location).most_common()
        )

    def weapon_usage(self) -> dict[str, int]:
        return dict(Counter(h.weapon for h in self.hits if h.weapon).most_common())

    def blocked_ratio(self) -> float:
        """Fraction of landed attacks that did zero damage — i.e. stopped by
        protection or by the hit-area cap. High values mean you were hitting
        something you cannot hurt."""
        if not self.hits:
            return 0.0
        return sum(1 for h in self.hits if h.blocked) / len(self.hits)

    def capped_damage(self) -> int:
        """Total damage lost to the hit-area cap."""
        return sum(
            (h.capped_from - h.damage)
            for h in self.hits
            if h.capped_from is not None and h.capped_from > h.damage
        )

    def repel_summary(self) -> dict[str, dict[str, int]]:
        out: dict[str, dict[str, int]] = defaultdict(lambda: {"repelled": 0, "missed": 0})
        for r in self.repels:
            key = r.repeller
            out[key]["repelled" if r.succeeded else "missed"] += 1
        return dict(out)

    def split_battles(self) -> list["CombatLog"]:
        """Cut the log into separate battles on the engine's Playvcr markers.

        Returns ``[self]`` when no marker was found (a hosted run, or a log
        that started mid-battle)."""
        if len(self.playvcr_lines) <= 1:
            return [self]
        bounds = self.playvcr_lines + [10**12]
        out = []
        for lo, hi in zip(bounds, bounds[1:]):
            sub = CombatLog(
                hits=[h for h in self.hits if lo <= h.line_no < hi],
                misses=[m for m in self.misses if lo <= m.line_no < hi],
                repels=[r for r in self.repels if lo <= r.line_no < hi],
                rout_checks=[r for r in self.rout_checks if lo <= r.line_no < hi],
                army_routs=[r for r in self.army_routs if lo <= r.line_no < hi],
                casts=[c for c in self.casts if lo <= c.line_no < hi],
                attacks=[a for a in self.attacks if lo <= a.line_no < hi],
                environmental=[e for e in self.environmental if lo <= e.line_no < hi],
                playvcr_lines=[lo],
                tick_lines=[t for t in self.tick_lines if lo <= t < hi],
            )
            sub.ticks = len(sub.tick_lines)
            out.append(sub)
        return out

    def describe(self, top: int = 8) -> str:
        """Human-readable summary, the shape the advisor actually quotes."""
        lines: list[str] = []
        add = lines.append
        add(
            f"{len(self.hits)} landed attacks, {sum(1 for h in self.hits if h.killed)} kills, "
            f"{self.ticks} battle ticks"
        )
        if self.hits:
            add(f"{self.blocked_ratio():.0%} of landed attacks did zero damage")
        capped = self.capped_damage()
        if capped:
            add(f"{capped} damage lost to the hit-area cap")

        def table(title: str, data: dict[str, int], unit: str) -> None:
            if not data:
                return
            add("")
            add(title)
            for k, v in list(data.items())[:top]:
                add(f"  {v:>6} {unit:<8} {k}")

        table("damage dealt", self.damage_dealt(), "dmg")
        table("damage taken", self.damage_taken(), "dmg")
        table("kills", self.kills(), "kills")
        table("losses", self.deaths(), "died")
        table("hit locations", self.hit_locations(), "hits")

        acc = self.accuracy()
        if acc:
            add("")
            add("accuracy (swings -> landed)")
            for k, (n, got, rate) in list(acc.items())[:top]:
                add(f"  {n:>6} -> {got:<5} {rate:>4.0%}  {k}")

        rs = self.repel_summary()
        if rs:
            add("")
            add("repels (manual p.62-63)")
            for k, v in sorted(rs.items(), key=lambda kv: -kv[1]["repelled"])[:top]:
                add(f"  {v['repelled']:>6} repelled, {v['missed']} missed  {k}")

        if self.army_routs:
            add("")
            for r in self.army_routs:
                why = " (75% hit points lost)" if r.hp_rout else ""
                add(f"army rout: {r.nation}{why}")

        return "\n".join(lines)


# --------------------------------------------------------------------------
# parsing
# --------------------------------------------------------------------------


def parse(text: str) -> CombatLog:
    """Parse `log.txt` contents into a :class:`CombatLog`."""
    return parse_lines(text.splitlines())


def parse_lines(lines) -> CombatLog:
    """Parse an iterable of log lines.

    Takes an iterable rather than a string so a multi-megabyte `log.txt` can be
    streamed off disk instead of held in memory twice.
    """
    log = CombatLog()
    tick: int | None = None

    # Modifier lines (Damage roll / cap / shield) precede the hit line they
    # describe, so they are buffered and attached to the next hit.
    pending_roll: tuple[tuple[int, int], tuple[int, int]] | None = None
    pending_cap: int | None = None
    pending_shield: int | None = None
    pending_result: int | None = None
    pending_blunt: int | None = None

    for i, raw in enumerate(lines):
        log.lines_read += 1
        if not _RE_INTERESTING.search(raw):
            continue
        line = raw.strip()
        if not line or _RE_NOISE.match(line):
            continue

        # The viewer echoes each on-screen message into the renderer's text
        # cache. Those lines duplicate a plain one, so they are dropped --
        # except that the blunt-damage note appears nowhere else, so it is
        # harvested on the way past.
        if _RE_UI_ECHO.match(line) or _RE_UI_ECHO_TAIL.search(line):
            if m := _RE_BLUNT.search(line):
                pending_blunt = int(m.group("by"))
            continue

        if m := _RE_TICK.match(line):
            log.ticks += 1
            log.tick_lines.append(i)
            tick = int(m.group("t"))
            continue
        if _RE_PLAYVCR.match(line):
            log.playvcr_lines.append(i)
            continue

        if m := _RE_DAMAGE_ROLL.match(line):
            pending_roll = (
                (int(m.group("da")), int(m.group("db"))),
                (int(m.group("pa")), int(m.group("pb"))),
            )
            pending_result = int(m.group("result"))
            log.lines_matched += 1
            continue
        if m := _RE_CAP.match(line):
            pending_cap = pending_result
            pending_result = int(m.group("to"))
            log.lines_matched += 1
            continue
        if m := _RE_SHIELD.match(line):
            pending_shield = int(m.group("by"))
            log.lines_matched += 1
            continue
        if m := _RE_BLUNT.match(line):
            pending_blunt = int(m.group("by"))
            log.lines_matched += 1
            continue

        if m := _RE_TRAMPLE.match(line):
            log.hits.append(
                Hit(
                    attacker=_clean(m.group("attacker")) or "?",
                    target=_clean(m.group("target")) or "?",
                    location=None,
                    weapon="Trample",
                    damage=int(m.group("damage")),
                    killed="killed" in (m.group("tail") or ""),
                    blunt_bonus=pending_blunt,
                    line_no=i,
                    round_no=tick,
                )
            )
            pending_roll = pending_cap = pending_shield = pending_result = None
            pending_blunt = None
            log.lines_matched += 1
            continue

        if m := _RE_HIT.match(line):
            tail = m.group("tail") or ""
            weapon = _clean(m.group("weapon")) or _clean(m.group("rweapon"))
            log.hits.append(
                Hit(
                    attacker=_clean(m.group("attacker")) or "?",
                    target=_clean(m.group("target")) or "?",
                    location=_clean(m.group("location")) or _clean(m.group("shieldloc")),
                    weapon=weapon,
                    damage=int(m.group("damage")),
                    killed="killed" in tail,
                    ranged=bool(m.group("rweapon")),
                    shield_hit=bool(m.group("shieldloc")) or pending_shield is not None,
                    shield_reduction=pending_shield,
                    capped_from=pending_cap,
                    blunt_bonus=pending_blunt,
                    damage_roll=pending_roll[0] if pending_roll else None,
                    prot_roll=pending_roll[1] if pending_roll else None,
                    line_no=i,
                    round_no=tick,
                )
            )
            pending_roll = pending_cap = pending_shield = pending_result = None
            pending_blunt = None
            log.lines_matched += 1
            continue

        if m := _RE_REPEL_OK.match(line):
            log.repels.append(
                Repel(
                    repeller=_clean(m.group("repeller")) or "?",
                    attacker=_clean(m.group("attacker")) or "?",
                    succeeded=True,
                    line_no=i,
                    round_no=tick,
                )
            )
            log.lines_matched += 1
            continue
        if m := _RE_REPEL_MISS.match(line):
            log.repels.append(
                Repel(
                    repeller=_clean(m.group("repeller")) or "?",
                    attacker=_clean(m.group("attacker")) or "?",
                    succeeded=False,
                    rolls=(int(m.group("a")), int(m.group("b"))),
                    line_no=i,
                    round_no=tick,
                )
            )
            log.lines_matched += 1
            continue
        if m := _RE_REPELLED.match(line):
            log.repels.append(
                Repel(
                    repeller=_clean(m.group("repeller")) or "?",
                    attacker=_clean(m.group("attacker")) or "?",
                    succeeded=True,
                    weapon=_clean(m.group("weapon")),
                    line_no=i,
                    round_no=tick,
                )
            )
            log.lines_matched += 1
            continue

        # After the repel patterns on purpose: "missed to repel" is a repel.
        if m := _RE_MISS.match(line):
            log.misses.append(
                Miss(
                    attacker=_clean(m.group("attacker")) or "?",
                    target=_clean(m.group("target")) or "?",
                    line_no=i,
                    round_no=tick,
                )
            )
            log.lines_matched += 1
            continue

        if m := _RE_ROUTCHK.match(line):
            log.rout_checks.append(
                RoutCheck(
                    unit=_clean(m.group("unit")) or "?",
                    passed=m.group("res") == "passed",
                    rolls=(
                        int(m.group("a")),
                        int(m.group("b")),
                        int(m.group("c")),
                        int(m.group("d")),
                    ),
                    line_no=i,
                    round_no=tick,
                )
            )
            log.lines_matched += 1
            continue

        if m := _RE_ARMYROUT.match(line):
            v = m.group("v1") or m.group("v2") or "0"
            log.army_routs.append(
                ArmyRout(
                    nation=_clean(m.group("nation")) or "?",
                    value=int(v),
                    hp_rout=bool(m.group("tail")),
                    line_no=i,
                    round_no=tick,
                )
            )
            log.lines_matched += 1
            continue

        if m := _RE_FATIGUE_DMG.match(line):
            log.environmental.append(
                Environmental(
                    unit=_clean(m.group("unit")) or "?",
                    damage=int(m.group("damage")),
                    source="excessive fatigue",
                    line_no=i,
                    round_no=tick,
                )
            )
            log.lines_matched += 1
            continue
        if m := _RE_ENV.match(line):
            log.environmental.append(
                Environmental(
                    unit=_clean(m.group("unit")) or "?",
                    damage=int(m.group("damage")),
                    source=_clean(m.group("source")) or "?",
                    line_no=i,
                    round_no=tick,
                )
            )
            log.lines_matched += 1
            continue

        if m := _RE_ATTACKS_WITH.match(line):
            log.attacks.append(
                Attack(
                    attacker=_clean(m.group("attacker")) or "?",
                    weapon=_clean(m.group("weapon")),
                    line_no=i,
                    round_no=tick,
                )
            )
            log.lines_matched += 1
            continue

        if m := _RE_CAST.match(line):
            log.casts.append(
                Cast(
                    caster=_clean(m.group("caster")) or "?",
                    spell=_clean(m.group("spell")) or "?",
                    line_no=i,
                    round_no=tick,
                )
            )
            log.lines_matched += 1
            continue

    return log


def parse_file(path, encoding: str = "utf-8") -> CombatLog:
    """Parse a `log.txt` from disk.

    A real log runs to tens of megabytes, so it is streamed line by line rather
    than read whole, and decoded with errors replaced rather than strictly --
    the engine writes UTF-8 but the file can be truncated mid-write if the
    game is killed.
    """
    with open(path, "r", encoding=encoding, errors="replace") as fh:
        return parse_lines(fh)
