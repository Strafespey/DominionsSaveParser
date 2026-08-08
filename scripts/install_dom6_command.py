"""Install the `dom6` shortcut so the analyst can be launched from any shell.

Copies `tools/dom6.cmd` to a directory already on PATH, with this checkout's
location baked in. A `.cmd` works from PowerShell, cmd.exe and Git Bash alike,
so no shell profile has to be edited.

    py scripts/install_dom6_command.py            # install
    py scripts/install_dom6_command.py --dry-run  # show what would happen
    py scripts/install_dom6_command.py --dir D:\bin
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "tools" / "dom6.cmd"
DEFAULT_PLACEHOLDER = r"C:\Users\Alex\DominionsSaveParser"


def path_dirs() -> list[Path]:
    return [Path(p) for p in os.environ.get("PATH", "").split(os.pathsep) if p.strip()]


def pick_target() -> Path | None:
    """Prefer a writable per-user directory that is already on PATH."""
    home = Path.home()
    dirs = [d for d in path_dirs() if home in d.parents or d == home]
    preferred = [home / ".local" / "bin", home / "bin"]
    for p in preferred:
        if p in dirs and p.is_dir():
            return p
    for d in dirs:
        if d.is_dir() and "windows" not in str(d).lower():
            return d
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", type=Path, help="install directory (must be on PATH)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not SOURCE.exists():
        print(f"missing {SOURCE}")
        return 1

    target_dir = args.dir or pick_target()
    if not target_dir:
        print(
            "No writable directory on PATH found.\n"
            "Pass one explicitly, e.g.:  py scripts/install_dom6_command.py "
            r"--dir %USERPROFILE%\.local\bin"
        )
        return 1

    body = SOURCE.read_text(encoding="utf-8").replace(DEFAULT_PLACEHOLDER, str(ROOT))
    target = target_dir / "dom6.cmd"

    print(f"source : {SOURCE}")
    print(f"target : {target}")
    print(f"project: {ROOT}")
    if target_dir not in path_dirs():
        print(f"\nwarning: {target_dir} is not on PATH; `dom6` will not resolve.")

    if args.dry_run:
        print("\n(dry run, nothing written)")
        return 0

    target_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    print("\ninstalled. Open a new shell and run:  dom6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
