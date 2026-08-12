# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Tools for reading Dominions 6 savegames, plus an agent skill that uses them to
act as a tactical advisor. **The save format is undocumented and is being
reverse engineered**, which shapes nearly every convention below.

## Commands

```sh
py tests/test_combatlog.py          # run one suite -- each test file is its own runner
py tests/test_vcr_regression.py     # golden-file tests over tests/fixtures/mid_bandarlog.trn
```

There is **no pytest installed** and no test runner script. Each `tests/test_*.py`
has a `main()` that runs every `test_*` function in the file and prints
`N/N passed`; `unittest discover` finds nothing. To run a single test, call it
from the file (`py -c "import sys; sys.path.insert(0,'tests'); import test_combatlog as t; t.test_misses()"`)
or comment out the others — there is no `-k` equivalent.

No build step, no linter config, no `pyproject.toml` (packaging is an open
roadmap item; scripts do `sys.path` juggling instead). Python 3.10+, `py`
launcher on Windows. The core library has no third-party dependencies. Only the
never-yet-exercised input-macro path in `dom6/replay.py` needs `pyautogui` /
`pygetwindow` / `keyboard`, none of which are installed.

Common entry points — all take a savegame *name*, a folder, or a `.trn` path:

```sh
py scripts/inspect_save.py                       # list savegames
py scripts/battle_report.py <GameName>           # order of battle and losses
py scripts/empire_report.py <GameName> --history # score-graph trends
py scripts/analyze_battle.py <GameName>          # list battles in the turn file
py scripts/analyze_battle.py <GameName> --capture   # replay + capture combat log
py scripts/analyze_battle.py --log captures/X.log   # re-analyse an existing log
py scripts/friendly_fire.py <GameName> --log captures/X.log
py scripts/extract_reference.py                  # regenerate data/reference/ from the engine + exe
py scripts/build_manual_kb.py                    # regenerate kb/ from the manual PDF
```

## The two hard invariants

**1. Never write to the real savegame folder.** Hosting a turn advances the
game irreversibly. Anything that hosts (`--dumpfights`, `--scoredump`) must run
against a temp copy with the `DOM6_SAVE` environment variable redirected —
that is what `SandboxedHost` (`dom6/engine.py`) and `ReplaySession`
(`dom6/replay.py`) exist for; both copy the savegame on `__enter__` and clean
up on exit. `SAFE_QUERY_SWITCHES` lists the switches that only read.

**2. Any engine launch truncates `log.txt` in the game directory** — even
`--listnations`. That file is the only copy of a captured combat log and costs
a game launch plus a manual click to produce. `Engine.run` preserves and
restores it around every call; don't remove that. Captures are archived to
`captures/` (gitignored via `*.log`) so the game directory is never the only copy.

## Architecture

### Layered save parsing (`dom6/`)

`obfuscation.py` → `reader.py` → `save.py` → `vcr.py` → `analysis.py`, with
`paths.py` locating the install and savegames.

- **All strings are XOR `0x4F`, NUL-terminated; numbers are not obfuscated.**
  Never XOR a whole file — only while reading a string field.
- `save.py` decodes only fields verified against real files; everything else
  stays as raw offsets rather than being guessed at.
- `vcr.py` finds battles by the literal 8-byte marker `_vcr_VCR` (not
  obfuscated), which is why replays are locatable even though the record layout
  past `+0x20` is unmapped.
- `analysis.py` *infers* casualties — there is no "killed" flag. A unit engaged
  and not observed afterwards did not come back. Sound for your own army,
  unreliable for the enemy's, and `SideOutcome.observable` keeps that
  distinction explicit.

### Game data is re-derived, never hard-coded (`dom6/gamedata.py`)

Monster/weapon/armour stats are compiled into `Dominions6.exe` as fixed-stride
struct arrays. Rather than hard-coding addresses that a patch would silently
break, `solve_layout()` derives `(base, stride)` at runtime from `*_ANCHORS`
(names whose ids were proven from real savegames) and then verifies against
`*_VALIDATION` ids deliberately excluded from the derivation. **On failure it
raises rather than returning wrong data.** Preserve that property when touching
this module — the whole design exists so a patch produces an error, not
plausible-looking garbage.

### Battles: setup on disk, narrative only from a live engine

The save stores battle *setup* + RNG seed + per-round checksums and
re-simulates deterministically on replay. There is **no blow-by-blow record on
disk**, so analysis splits in two:

1. **Setup and outcome** — composition, placement, casualties. From the save.
2. **Per-hit narrative** — only exists while the engine re-simulates, requires
   launching with `--vcrdebug -d -d -d`, and only renders in the viewer (needs
   an OpenGL context). There is no headless route; `dom6/replay.py` automates
   everything except the click that opens the battle.

`dom6/combatlog.py` parses the resulting `log.txt`. Its grammar came from the
engine's own format strings, not from samples. Two traps, both already handled
and both regression-tested:

- **The viewer echoes every on-screen message back into the log** wrapped in
  renderer text-cache chatter (`creating new text tex '...' (482*15) forcep2 0`).
  Parsing those counts each event 2–3× and invents units named
  `creating new text tex 'Red Guard`. Echoes are dropped by prefix *and* by
  closing signature — the engine writes from several buffers, so an echo's
  opening is sometimes cut off mid-word.
- **Units are identified by name only.** No unit ids, so two Red Guards are
  indistinguishable; per-unit-type totals are reliable, "this particular
  soldier" is not. Attributing a *side* requires joining to the turn file's
  roster on `type_id → owner` (see `scripts/friendly_fire.py`), which is only
  sound when a name belongs to one side — that script reports and excludes
  ambiguous names rather than guessing.
- `accuracy()` is **melee-only**: the engine emits no miss line for missile
  fire, so archers read as a spurious 100%.

### Rules knowledge base (`kb/`)

The 449-page manual as a tiered corpus so an agent can cite rules without
loading ~344k tokens: `rules-cheatsheet.md` (~1.6k) → `index.md` routing table →
one `sections/*.md` per chapter → `manual.txt` (**grep only, never load**).
Every page is marked `[p.N]` so any claim is checkable.

## Conventions that matter here

- **Distinguish established from inferred.** `docs/FILE_FORMAT.md` carries
  per-field confidence levels and `docs/ROADMAP.md` lists what is unmapped.
  When you decode something new, record how it was proven and what would
  falsify it. Leaving a field as a raw offset is preferred to guessing.
- **Comments explain the reverse-engineering reasoning**, not the syntax —
  which known-plaintext search or anchor cross-check established a layout, and
  what the engine string was that revealed it. Match that density.
- **Docstrings carry the caveats** (⚠️ blocks for things that will mislead a
  caller). This is where the "by name only" and "melee-only" warnings live, and
  it is why analysis code doesn't have to re-learn them.
- The advisor's own rules — including what the data cannot support — live in
  `.claude/skills/dominions6-analyst/SKILL.md`. Notably: **the player has no
  control once a battle starts**, so all advice must be a pre-battle setup
  change (placement, formation, target orders, commander script slots),
  never a mid-battle reaction.
