"""Locating the Dominions 6 install and savegames."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

# Dominions 6 honours these environment variables (seen in the executable):
#   DOM6_DATA, DOM6_CONF, DOM6_SAVE, DOM6_LOCALMAPS, DOM6_MODS
ENV_SAVE = "DOM6_SAVE"
ENV_DATA = "DOM6_DATA"

_EXE_NAMES = ("Dominions6.exe", "dom6_amd64", "dom6_mac")

_STEAM_VDF = Path(r"C:\Program Files (x86)\Steam\steamapps\libraryfolders.vdf")


def _candidate_steam_libraries() -> list[Path]:
    libs: list[Path] = []
    if _STEAM_VDF.exists():
        text = _STEAM_VDF.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r'"path"\s+"([^"]+)"', text):
            libs.append(Path(m.group(1).replace("\\\\", "\\")))
    libs += [
        Path(r"C:\Program Files (x86)\Steam"),
        Path(r"C:\Program Files\Steam"),
        Path(r"D:\SteamLibrary"),
    ]
    return libs


def find_game_dir(explicit: str | os.PathLike | None = None) -> Path | None:
    """Locate the Dominions 6 install directory (the one holding the executable)."""
    if explicit:
        p = Path(explicit)
        return p if any((p / n).exists() for n in _EXE_NAMES) else None

    env = os.environ.get(ENV_DATA)
    if env and (Path(env).parent / "Dominions6.exe").exists():
        return Path(env).parent

    for lib in _candidate_steam_libraries():
        p = lib / "steamapps" / "common" / "Dominions6"
        if any((p / n).exists() for n in _EXE_NAMES):
            return p

    for p in (
        Path(r"C:\Program Files\Dominions6"),
        Path(r"C:\Program Files (x86)\Dominions6"),
    ):
        if any((p / n).exists() for n in _EXE_NAMES):
            return p
    return None


def find_executable(game_dir: Path | None = None) -> Path | None:
    game_dir = game_dir or find_game_dir()
    if not game_dir:
        return None
    for n in _EXE_NAMES:
        if (game_dir / n).exists():
            return game_dir / n
    return None


def find_save_root(explicit: str | os.PathLike | None = None) -> Path | None:
    """Locate the savedgames root.

    Order: explicit arg, then $DOM6_SAVE, then %APPDATA%/Dominions6/savedgames.
    """
    if explicit:
        p = Path(explicit)
        return p if p.is_dir() else None

    env = os.environ.get(ENV_SAVE)
    if env and Path(env).is_dir():
        return Path(env)

    appdata = os.environ.get("APPDATA")
    if appdata:
        p = Path(appdata) / "Dominions6" / "savedgames"
        if p.is_dir():
            return p

    # Linux / macOS layouts
    for p in (
        Path.home() / ".dominions6" / "savedgames",
        Path.home() / "Library" / "Application Support" / "Dominions6" / "savedgames",
    ):
        if p.is_dir():
            return p
    return None


@dataclass
class SaveGame:
    """One savegame folder."""

    name: str
    path: Path
    ftherlnd: Path | None = None
    turn_files: list[Path] = field(default_factory=list)  # .trn
    order_files: list[Path] = field(default_factory=list)  # .2h
    map_files: list[Path] = field(default_factory=list)

    @property
    def has_master_state(self) -> bool:
        return self.ftherlnd is not None

    def describe(self) -> str:
        trn = ", ".join(p.name for p in self.turn_files) or "none"
        return f"{self.name}: ftherlnd={'yes' if self.ftherlnd else 'no'}, trn=[{trn}]"


def load_savegame(folder: Path) -> SaveGame:
    sg = SaveGame(name=folder.name, path=folder)
    for f in sorted(folder.iterdir()):
        if not f.is_file():
            continue
        if f.name == "ftherlnd":
            sg.ftherlnd = f
        elif f.suffix == ".trn":
            sg.turn_files.append(f)
        elif f.suffix == ".2h":
            sg.order_files.append(f)
        elif f.suffix in (".map", ".d6m"):
            sg.map_files.append(f)
    return sg


def list_savegames(save_root: Path | None = None) -> list[SaveGame]:
    root = save_root or find_save_root()
    if not root:
        return []
    return [load_savegame(d) for d in sorted(root.iterdir()) if d.is_dir()]
