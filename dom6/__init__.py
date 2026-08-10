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
from .provinces import Province, find_provinces, owner_of
from .reader import Cursor
from .save import SaveFile, SaveFormatError, SaveHeader, load, parse_header
from .scores import (
    ScoreRecord,
    find_score_history,
    history_for,
    latest_by_nation,
)
from .vcr import MARKER as VCR_MARKER
from .vcr import (
    UNIT_RECORD_SIZE,
    VcrSection,
    VcrUnit,
    find_battles,
    find_battles_in_file,
    find_unit_arrays,
    find_unit_records,
)

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
    "Province",
    "find_provinces",
    "owner_of",
    "ScoreRecord",
    "find_score_history",
    "history_for",
    "latest_by_nation",
    "VcrSection",
    "VcrUnit",
    "VCR_MARKER",
    "UNIT_RECORD_SIZE",
    "find_battles",
    "find_battles_in_file",
    "find_unit_arrays",
    "find_unit_records",
    "SaveGame",
    "find_game_dir",
    "find_executable",
    "find_save_root",
    "list_savegames",
    "load_savegame",
]

__version__ = "0.1.0"
