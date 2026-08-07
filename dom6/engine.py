"""Driving the Dominions 6 executable as a data source.

The game exposes several undocumented switches that dump internal data. Some
are safe read-only queries (`--listnations`, `--listspells`, ...); one of them,
`--dumpfights`, only takes effect while the engine *hosts* a turn, which
mutates the savegame. Hosting is therefore always done against a throwaway copy
in a temp directory, selected via the `DOM6_SAVE` environment variable.

Nothing in this module ever writes to the player's real savegame folder.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from .paths import ENV_SAVE, find_executable

#: Switches that read data and exit without touching a savegame.
SAFE_QUERY_SWITCHES = (
    "--listnations",
    "--listspells",
    "--listevents",
    "--comsumrits",
    "--help",
    "--version",
)

#: Always-on flags: no Steam handshake, no crash dialogs, no audio/GUI surprises.
BASE_FLAGS = ("--nosteam", "--nocrashbox")


class EngineError(RuntimeError):
    pass


@dataclass
class EngineResult:
    args: list[str]
    returncode: int | None
    stdout: str
    stderr: str
    timed_out: bool = False


class Engine:
    """Thin wrapper around the Dominions 6 executable."""

    def __init__(self, exe: str | os.PathLike | None = None):
        exe_path = Path(exe) if exe else find_executable()
        if not exe_path or not exe_path.exists():
            raise EngineError(
                "Could not locate the Dominions 6 executable. "
                "Pass one explicitly or install via Steam."
            )
        self.exe = exe_path
        self.game_dir = exe_path.parent

    def run(
        self,
        args: list[str],
        *,
        save_root: Path | None = None,
        timeout: float = 120.0,
    ) -> EngineResult:
        """Run the engine with stdout/stderr captured.

        The executable is a GUI-subsystem binary, but it writes to inherited
        redirected handles, so piping works.
        """
        argv = [str(self.exe), *BASE_FLAGS, *args]
        env = dict(os.environ)
        if save_root is not None:
            env[ENV_SAVE] = str(save_root)

        try:
            proc = subprocess.run(
                argv,
                cwd=str(self.game_dir),
                env=env,
                capture_output=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            return EngineResult(
                args=argv,
                returncode=None,
                stdout=_decode(exc.stdout),
                stderr=_decode(exc.stderr),
                timed_out=True,
            )
        return EngineResult(
            args=argv,
            returncode=proc.returncode,
            stdout=_decode(proc.stdout),
            stderr=_decode(proc.stderr),
        )

    # -- safe read-only queries ---------------------------------------
    def list_nations(self) -> dict[int, str]:
        """Nation id -> name, from `--listnations`. Grouped by era in the output."""
        out = self.run(["--listnations"]).stdout
        nations: dict[int, str] = {}
        for line in out.splitlines():
            m = re.match(r"\s*(\d+)\s+(.+?)\s*$", line)
            if m:
                nations[int(m.group(1))] = m.group(2)
        return nations

    def list_spells(self) -> dict[int, str]:
        out = self.run(["--listspells"]).stdout
        spells: dict[int, str] = {}
        for line in out.splitlines():
            m = re.match(r"\s*(\d+)\s+(.+?)\s*$", line)
            if m:
                spells[int(m.group(1))] = m.group(2)
        return spells

    def list_events(self) -> dict[int, str]:
        out = self.run(["--listevents"], timeout=180).stdout
        events: dict[int, str] = {}
        for line in out.splitlines():
            m = re.match(r"\s*(\d+)\s+(.*)$", line)
            if m:
                events[int(m.group(1))] = m.group(2).rstrip()
        return events

    def summon_rituals(self) -> list[dict]:
        """`--comsumrits`: tab-separated summon ritual table."""
        out = self.run(["--comsumrits"]).stdout
        rows = []
        for line in out.splitlines():
            parts = line.split("\t")
            if len(parts) >= 7:
                rows.append(
                    {
                        "path": parts[0].strip(),
                        "level": _int(parts[1]),
                        "cost": _int(parts[2]),
                        "a": _int(parts[3]),
                        "b": _int(parts[4]),
                        "unit": parts[5].strip(),
                        "spell": parts[6].strip(),
                    }
                )
        return rows


# ---------------------------------------------------------------------
# Battle roster dumping (--dumpfights)
# ---------------------------------------------------------------------


@dataclass
class FightRoster:
    """One side of a battle, as printed by `--dumpfights`."""

    commanders: list[tuple[int, int, str]] = field(default_factory=list)
    units: list[tuple[int, int, str]] = field(default_factory=list)

    @property
    def total_units(self) -> int:
        return sum(a for a, _, _ in self.units)


@dataclass
class DumpedFight:
    """One battle: its header line and the two sides' rosters.

    Ordering note: in the engine's raw output the roster blocks lag their
    header line by exactly one battle -- the first header is followed by empty
    rosters, and each later header is followed by the *previous* battle's
    roster. Confirmed across two hosts of the same turn that emitted the
    battles in different orders: a "Phaeacia attacking ..." header was followed
    by Ulm's units, which belonged to the preceding "Ulm attacking ..." battle.

    `parse_dumpfights(align=True)` (the default) undoes this shift, so
    `rosters` belongs to *this* battle. One consequence is unavoidable: the
    final battle's roster is never printed, so the last fight has no rosters
    and `rosters_missing` is set.
    """

    attacker: str
    defender: str
    province: str
    province_defence: int
    poptype: int | None
    attack_strength: int | None = None
    defence_strength: int | None = None
    pd_strength: int | None = None
    rosters: list[FightRoster] = field(default_factory=list)
    #: True if the header/roster pairing has not been realigned.
    rosters_may_be_offset: bool = True
    #: True if this battle's roster was never emitted by the engine.
    rosters_missing: bool = False

    @property
    def attacker_roster(self) -> FightRoster | None:
        return self.rosters[0] if self.rosters else None

    @property
    def defender_roster(self) -> FightRoster | None:
        return self.rosters[1] if len(self.rosters) > 1 else None


_HEADER_RE = re.compile(
    r"^(?P<att>.+?) attacking (?P<def>.+?) in (?P<prov>.+?) "
    r"with PD (?P<pd>-?\d+)(?: \(poptype (?P<pop>-?\d+)\))?\s*$"
)
_STR_RE = re.compile(
    r"^attstr (?P<att>-?\d+), defstr (?P<def>-?\d+)(?: \(PDstr (?P<pd>-?\d+)\))?\s*$"
)
_ENTRY_RE = re.compile(r"^\s*(?P<a>\d+)\+(?P<b>\d+)\s+(?P<name>.+?)\s*$")


def parse_dumpfights(text: str, align: bool = True) -> list[DumpedFight]:
    """Parse the stdout produced by `--dumpfights` during a host.

    With `align=True` the one-battle roster lag described on `DumpedFight` is
    corrected. Pass `align=False` to see the engine's raw pairing.
    """
    fights: list[DumpedFight] = []
    current: DumpedFight | None = None
    roster: FightRoster | None = None
    bucket: str | None = None

    for line in text.splitlines():
        if (m := _HEADER_RE.match(line)) is not None:
            current = DumpedFight(
                attacker=m.group("att"),
                defender=m.group("def"),
                province=m.group("prov"),
                province_defence=int(m.group("pd")),
                poptype=int(m.group("pop")) if m.group("pop") else None,
            )
            fights.append(current)
            roster, bucket = None, None
        elif (m := _STR_RE.match(line)) is not None and current is not None:
            current.attack_strength = int(m.group("att"))
            current.defence_strength = int(m.group("def"))
            current.pd_strength = int(m.group("pd")) if m.group("pd") else None
        elif line.strip() == "commanders:":
            roster = FightRoster()
            if current is not None:
                current.rosters.append(roster)
            bucket = "commanders"
        elif line.strip() == "units:":
            bucket = "units"
        elif (m := _ENTRY_RE.match(line)) is not None and roster is not None:
            entry = (int(m.group("a")), int(m.group("b")), m.group("name"))
            getattr(roster, bucket or "units").append(entry)

    if align and fights:
        # Roster blocks lag their header by one battle: shift each block back
        # onto the battle it actually describes.
        shifted = [f.rosters for f in fights][1:] + [[]]
        for fight, rosters in zip(fights, shifted):
            fight.rosters = rosters
            fight.rosters_may_be_offset = False
            fight.rosters_missing = not rosters
    return fights


class SandboxedHost:
    """Host a turn against a throwaway copy of a savegame.

    Hosting advances the game, so this always operates on a copy. The original
    folder is opened read-only (to copy it) and never written to.
    """

    def __init__(self, engine: Engine, savegame_dir: str | os.PathLike):
        self.engine = engine
        self.source = Path(savegame_dir)
        if not self.source.is_dir():
            raise EngineError(f"not a savegame folder: {self.source}")
        self._tmp: tempfile.TemporaryDirectory | None = None

    def __enter__(self) -> "SandboxedHost":
        self._tmp = tempfile.TemporaryDirectory(prefix="dom6sandbox_")
        self.save_root = Path(self._tmp.name) / "savedgames"
        self.save_root.mkdir(parents=True)
        shutil.copytree(self.source, self.save_root / self.source.name)
        return self

    def __exit__(self, *exc) -> None:
        if self._tmp:
            self._tmp.cleanup()
            self._tmp = None

    def dump_fights(self, timeout: float = 600.0) -> tuple[list[DumpedFight], EngineResult]:
        """Host one turn with `--dumpfights` and parse the battle rosters."""
        result = self.engine.run(
            [
                "--textonly",
                "--vcrdebug",
                "--dumpfights",
                "--host",
                self.source.name,
            ],
            save_root=self.save_root,
            timeout=timeout,
        )
        return parse_dumpfights(result.stdout), result


def _decode(raw: bytes | None) -> str:
    if not raw:
        return ""
    return raw.decode("utf-8", errors="replace")


def _int(s: str) -> int | None:
    try:
        return int(s.strip())
    except (ValueError, AttributeError):
        return None
