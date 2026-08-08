# Dominions 6 Save Parser & Battle Analyst

Tools for reading Dominions 6 savegames and game data, with the goal of an
agent that can act as a personal tactical advisor — read your turn file, and
answer questions like *"why did I lose this battle?"* with reasoning grounded
in the actual game rules.

**Status: early. The save format is undocumented and is being reverse
engineered.** What works today is listed below; what doesn't is listed honestly
in `docs/FILE_FORMAT.md`.

## What works today

- **Save header parsing** — version, turn number, owning nation, game name.
- **Battle replay discovery** — finds every battle in a `.trn`, with the two
  sides' nations, the battlefield name, and the RNG seed.
- **String decoding** — Dominions obfuscates all text with XOR `0x4F`.
- **Order of battle** — every combatant in a replay, by name, per side.
- **Reference data extraction** — 103 nations, 1473 spells, 3302 events and
  146 summon rituals dumped from the engine, plus **4115 monsters** and
  **887 weapons** (with length and range) extracted from the executable.
- **Sandboxed battle forecasting** — drives the engine's `--dumpfights`
  against a throwaway copy of your save to show what battles your *current
  orders* would produce, with both sides' full rosters. (This simulates the
  next turn; it is not a replay of past battles — see
  `docs/ENGINE_TOOLING.md`.)

```
$ py scripts/inspect_save.py mid_bandarlog.trn
turn      : 9
nation    : 68 (Bandar Log, Land of the Apes)
battles   : 2

  --- VCR #1 Bandar Log vs Phaeacia in 'Trackless Woods' seed=9187 ---
      combatants          : 89 @0x00042424
        Bandar Log (2 cmd, 37 units)
              13 x Tiger Rider
              13 x Armored Sacred Tiger
              10 x Markata Archer
               1 x Brahmin
               1 x Bandar Noble
        Phaeacia (1 cmd, 49 units)
              49 x Longbowman
               1 x Captain
```

## The key constraint, up front

**Dominions does not store a blow-by-blow combat log.** It stores the battle
setup plus an RNG seed and per-round checksums, and the replay viewer
*re-simulates the fight deterministically* to produce the log you watch. That
is why replays break after a patch, and why the engine ships a
`Battle inconsistency, round %d (calc %d, loaded %d)` check.

So there are two tiers of analysis:

1. **Setup and outcome analysis** — army composition, placement, equipment,
   battle orders, casualties. All recoverable from the save, and enough for
   most tactical advice ("your light infantry was in the front row").
2. **Per-hit narrative** — requires making the *engine* replay the battle and
   emit its log. The engine contains the format strings for this; reaching
   them is an open problem. See `docs/ENGINE_TOOLING.md`.

## Requirements

- Python 3.10+
- Dominions 6 installed (auto-detected via Steam; the engine is used as a data
  source, and is optional for pure save parsing)

No third-party Python dependencies for the core library.

## Usage

```sh
py scripts/inspect_save.py                      # list savegames
py scripts/inspect_save.py <GameName>           # summarise a game
py scripts/inspect_save.py <file> --battles     # hexdump around each battle
py scripts/inspect_save.py <file> --strings 40  # decoded strings

py scripts/extract_reference.py                 # dump game DB to data/reference/
```

```python
import dom6

save = dom6.load(r"%APPDATA%\Dominions6\savedgames\MyGame\mid_ulm.trn")
print(save.header.turn, save.header.nation)
for battle in save.battles:
    print(battle.describe())
```

## Safety

Hosting a turn advances the game, so anything that hosts (`--dumpfights`) runs
against a **temp copy** with `DOM6_SAVE` redirected. Nothing in this repo writes
to your real savegame folder.

## Layout

```
dom6/               core library
  obfuscation.py    XOR 0x4F string codec
  reader.py         little-endian cursor
  paths.py          locate install + savegames
  save.py           header + top-level save parsing
  vcr.py            battle replay sections
  engine.py         driving Dominions6.exe as a data source
scripts/            CLI entry points
docs/               reverse-engineering notes
data/reference/     generated game database (gitignored)
```

## Documentation

- [`docs/FILE_FORMAT.md`](docs/FILE_FORMAT.md) — save format, with confidence
  levels per field and the list of open questions.
- [`docs/ENGINE_TOOLING.md`](docs/ENGINE_TOOLING.md) — engine switches,
  environment variables, and the caveats on `--dumpfights`.

## Rules knowledge base

`kb/` holds the manual as a tiered corpus, so an agent can consult the rules
without loading a 449-page book (~344k tokens):

| Tier | What | Size |
|---|---|---|
| 0 | `kb/rules-cheatsheet.md` — the ~20 mechanics that decide battles | ~1.6k tokens |
| 1 | `kb/index.md` routing table + full 407-entry section index | ~4.6k tokens |
| 1 | `kb/sections/*.md` — one file per chapter (Combat ~16k) | load one |
| 1 | `kb/nations/*.md` — one file per nation | ~1.3k each |
| 2 | `kb/manual.txt` — page-anchored full text, **grep only** | never load |

Sectioning is driven by the PDF's own outline rather than heading regexes, and
every page is marked `[p.N]` so any claim can be cited and checked.

Rebuild with `py scripts/build_manual_kb.py`. The cheat sheet is hand-written
and is not regenerated.

## Roadmap

- [x] Locate battle replays and decode the combatant record
- [x] Extract the monster name table (4115 entries)
- [x] Extract the weapon table with length and range (887 entries)
- [ ] Extract the armour table (located at stride 104, not yet decoded)
- [ ] Find each unit's weapons/armour inside the 888-byte monster record
- [ ] Map battlefield placement (x/y, squad) in the 173-byte combatant record
- [ ] Map province / commander record layouts
- [ ] Build a rules knowledge base from the manual
- [ ] Ship the battle-analyst agent skill
