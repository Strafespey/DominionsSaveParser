"""dom6 -- tools for reading Dominions 6 savegames and game data.

The savegame format is undocumented; see docs/FILE_FORMAT.md for what has been
established and what is still guesswork.
"""

from .obfuscation import XOR_KEY, deobfuscate, read_cstring
from .paths import (
    SaveGame,
    find_executable,
    find_game_dir,
    find_save_root,
    list_savegames,
    load_savegame,
)
from .reader import Cursor
from .save import SaveFile, SaveFormatError, SaveHeader, load, parse_header
from .vcr import MARKER as VCR_MARKER
from .vcr import VcrSection, find_battles, find_battles_in_file

__all__ = [
    "XOR_KEY",
    "deobfuscate",
    "read_cstring",
    "Cursor",
    "SaveFile",
    "SaveHeader",
    "SaveFormatError",
    "load",
    "parse_header",
    "VcrSection",
    "VCR_MARKER",
    "find_battles",
    "find_battles_in_file",
    "SaveGame",
    "find_game_dir",
    "find_executable",
    "find_save_root",
    "list_savegames",
    "load_savegame",
]

__version__ = "0.1.0"
