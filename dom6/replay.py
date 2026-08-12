"""Drive the game's replay viewer and capture the per-hit combat log.

Why this exists: the `.trn` stores a battle's *setup* plus an RNG seed, not a
narrative (`docs/FILE_FORMAT.md` §4). The blow-by-blow only exists while the
engine re-simulates, and the engine only re-simulates a **past** battle when
that battle is opened in the replay viewer — which needs an OpenGL context.
So there is no headless route: something has to open the window.

What this module automates around that:

* launches the game already configured (`--vcrdebug -d -d -d`, windowed, no
  sound), so you never touch Steam launch options;
* points `DOM6_SAVE` at a **throwaway copy** of the savegame, so nothing you
  do in the window can damage the real game;
* preserves and restores any pre-existing `log.txt`, which the engine
  truncates on every launch and which lives outside the sandbox;
* watches `log.txt` and returns as soon as a replay has actually been played
  and stopped growing;
* shuts the game down and hands back a parsed :class:`dom6.combatlog.CombatLog`.

Two modes:

``ReplaySession.capture(...)``
    Semi-automatic. Opens the game, waits for you to click the battle, detects
    the log, closes up. Reliable — the only step it cannot do is the click.

``ReplaySession.capture(macro=...)``
    Fully automatic. Replays a recorded input macro to open the battle. See
    :func:`record_macro`; a macro is tied to the window size this module
    forces, so it stays valid between runs.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

from .combatlog import CombatLog, parse_file
from .engine import BASE_FLAGS, Engine, EngineError

__all__ = ["ReplaySession", "MacroStep", "record_macro", "DEFAULT_RES"]

ENV_SAVE = "DOM6_SAVE"

#: Window size the session forces. Recorded macros are only valid for the size
#: they were recorded at, so pinning it is what makes them reusable.
DEFAULT_RES = (1024, 768)

#: Flags that make the viewer scriptable: windowed, quiet, fast to draw, and
#: emitting the combat log. `-d` is repeatable and the log needs level 3.
VIEWER_FLAGS = ["-w", "--nosound", "--fastgrx", "--vcrdebug", "-d", "-d", "-d"]

#: Lines that only appear once a battle has actually been replayed. Presence of
#: any of these is how the session knows the click landed.
_COMBAT_MARKERS = (" points of damage", "Damage roll ", "Playvcr ")


@dataclass
class MacroStep:
    """One recorded input event, replayed with pyautogui."""

    kind: str  # "click" | "key" | "wait"
    x: int | None = None
    y: int | None = None
    key: str | None = None
    delay: float = 0.4

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}

    @classmethod
    def from_dict(cls, d: dict) -> "MacroStep":
        return cls(**d)


@dataclass
class ReplaySession:
    """A sandboxed run of the game with the combat log captured.

    ``savegame_dir`` is copied, never written to. The copy is deleted when the
    session exits.
    """

    engine: Engine
    savegame_dir: Path
    res: tuple[int, int] = DEFAULT_RES
    _tmp: tempfile.TemporaryDirectory | None = field(default=None, repr=False)
    _proc: subprocess.Popen | None = field(default=None, repr=False)
    _log_backup: Path | None = field(default=None, repr=False)

    def __init__(
        self,
        engine: Engine,
        savegame_dir: str | os.PathLike,
        res: tuple[int, int] = DEFAULT_RES,
    ):
        self.engine = engine
        self.savegame_dir = Path(savegame_dir)
        if not self.savegame_dir.is_dir():
            raise EngineError(f"not a savegame folder: {self.savegame_dir}")
        self.res = res
        self._tmp = None
        self._proc = None
        self._log_backup = None

    # -- lifecycle ---------------------------------------------------------

    @property
    def log_path(self) -> Path:
        return self.engine.game_dir / "log.txt"

    def __enter__(self) -> "ReplaySession":
        self._tmp = tempfile.TemporaryDirectory(prefix="dom6replay_")
        self.save_root = Path(self._tmp.name) / "savedgames"
        self.save_root.mkdir(parents=True)
        shutil.copytree(
            self.savegame_dir, self.save_root / self.savegame_dir.name
        )
        # log.txt is truncated on every debug launch and lives in the game
        # directory, which DOM6_SAVE does not protect. Preserve it.
        if self.log_path.exists():
            self._log_backup = Path(self._tmp.name) / "log.txt.bak"
            shutil.copy2(self.log_path, self._log_backup)
        return self

    def __exit__(self, *exc) -> None:
        self.stop()
        if self._log_backup and self._log_backup.exists():
            shutil.copy2(self._log_backup, self.log_path)
        if self._tmp:
            self._tmp.cleanup()
            self._tmp = None

    def launch(self) -> subprocess.Popen:
        """Start the game windowed, pointed at the sandboxed save copy."""
        argv = [
            str(self.engine.exe),
            *BASE_FLAGS,
            *VIEWER_FLAGS,
            "--res",
            str(self.res[0]),
            str(self.res[1]),
            self.savegame_dir.name,
        ]
        env = dict(os.environ)
        env[ENV_SAVE] = str(self.save_root)
        self._proc = subprocess.Popen(
            argv,
            cwd=str(self.engine.game_dir),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return self._proc

    def stop(self) -> None:
        if self._proc and self._proc.poll() is None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                self._proc.kill()
        self._proc = None

    # -- capture -----------------------------------------------------------

    def _log_state(self) -> tuple[int, bool]:
        """(size, has_combat_lines). Cheap enough to poll once a second."""
        if not self.log_path.exists():
            return 0, False
        size = self.log_path.stat().st_size
        if size == 0:
            return 0, False
        # Only sniff the tail; the file reaches tens of megabytes.
        with open(self.log_path, "rb") as fh:
            fh.seek(max(0, size - 262_144))
            tail = fh.read().decode("utf-8", errors="replace")
        return size, any(m in tail for m in _COMBAT_MARKERS)

    def capture(
        self,
        *,
        macro: list[MacroStep] | None = None,
        timeout: float = 600.0,
        settle: float = 6.0,
        poll: float = 1.0,
        archive: str | os.PathLike | None = None,
        on_status=None,
    ) -> CombatLog:
        """Launch, get a battle replayed, and return the parsed log.

        With ``macro``, the battle is opened automatically. Without it, the
        window is left for you to click the battle in — the session detects
        the replay on its own and closes down afterwards.

        ``settle`` is how many seconds the log must stop growing before the
        replay is considered finished.

        ``archive`` copies the raw log somewhere durable before this session
        exits. Strongly recommended: `log.txt` lives in the game directory and
        is truncated by *any* engine launch, and this session's own cleanup
        puts the previous log back over it. A capture costs a game launch and
        a manual click, so it should not exist in only one place.
        """

        def status(msg: str) -> None:
            if on_status:
                on_status(msg)

        status("launching game (sandboxed copy, real save untouched)")
        self.launch()

        if macro:
            status("waiting for the window before replaying the macro")
            self._await_window(timeout=90)
            self._play_macro(macro, on_status=on_status)
        else:
            status("game is open -- click the battle you want analysed")

        deadline = time.monotonic() + timeout
        last_size = 0
        last_change = time.monotonic()
        saw_combat = False

        while time.monotonic() < deadline:
            if self._proc and self._proc.poll() is not None:
                # Player quit the game themselves; whatever is in the log is
                # what we get.
                break
            size, has_combat = self._log_state()
            if size != last_size:
                last_size, last_change = size, time.monotonic()
                if has_combat and not saw_combat:
                    saw_combat = True
                    status(f"replay detected ({size/1e6:.1f} MB and growing)")
            if saw_combat and time.monotonic() - last_change >= settle:
                status("replay finished")
                break
            time.sleep(poll)
        else:
            raise EngineError(
                f"no replay captured within {timeout:.0f}s. The log only fills "
                "when a battle is actually opened in the viewer."
            )

        if not saw_combat:
            raise EngineError(
                "the game exited before a battle replay was captured -- "
                "open a battle in the viewer before quitting."
            )

        status("closing game and parsing log")
        self.stop()
        if archive:
            dest = Path(archive)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.log_path, dest)
            status(f"raw log archived to {dest}")
        return parse_file(self.log_path)

    # -- input driving -----------------------------------------------------

    def _await_window(self, timeout: float = 90.0) -> None:
        import pygetwindow as gw

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            wins = [w for w in gw.getAllWindows() if "dominions" in w.title.lower()]
            if wins:
                try:
                    wins[0].activate()
                except Exception:
                    pass  # activation is best-effort; focus may already be right
                time.sleep(1.5)
                return
            time.sleep(0.5)
        raise EngineError("the game window never appeared")

    def _play_macro(self, macro: list[MacroStep], on_status=None) -> None:
        import pyautogui

        pyautogui.FAILSAFE = True
        for i, step in enumerate(macro, 1):
            if on_status:
                on_status(f"macro step {i}/{len(macro)}: {step.kind} {step.key or ''}")
            if step.kind == "click" and step.x is not None and step.y is not None:
                pyautogui.click(step.x, step.y)
            elif step.kind == "key" and step.key:
                pyautogui.press(step.key)
            time.sleep(step.delay)


def record_macro(out_path: str | os.PathLike, stop_key: str = "f12") -> list[MacroStep]:
    """Record clicks and keypresses until ``stop_key`` is pressed.

    Run this once with the game already open at :data:`DEFAULT_RES`, open the
    battle exactly as you normally would, then press F12. The macro is saved
    and can be replayed by :meth:`ReplaySession.capture`.

    Coordinates are absolute screen positions, so the macro is only valid while
    the window stays at the size and position it had during recording. That is
    why the session pins ``--res``.
    """
    import json

    import keyboard
    import pyautogui

    steps: list[MacroStep] = []
    last = time.monotonic()

    def _delay() -> float:
        nonlocal last
        now = time.monotonic()
        d = min(5.0, max(0.2, now - last))
        last = now
        return round(d, 2)

    def on_key(event) -> None:
        if event.name == stop_key or event.event_type != "down":
            return
        steps.append(MacroStep(kind="key", key=event.name, delay=_delay()))

    keyboard.hook(on_key)
    print(f"recording -- open the battle, then press {stop_key.upper()} to stop")
    try:
        while not keyboard.is_pressed(stop_key):
            if keyboard.is_pressed("ctrl") and keyboard.is_pressed("shift"):
                x, y = pyautogui.position()
                steps.append(MacroStep(kind="click", x=x, y=y, delay=_delay()))
                time.sleep(0.4)
            time.sleep(0.05)
    finally:
        keyboard.unhook_all()

    Path(out_path).write_text(
        json.dumps([s.to_dict() for s in steps], indent=2), encoding="utf-8"
    )
    print(f"saved {len(steps)} steps to {out_path}")
    return steps


def load_macro(path: str | os.PathLike) -> list[MacroStep]:
    import json

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [MacroStep.from_dict(d) for d in data]
