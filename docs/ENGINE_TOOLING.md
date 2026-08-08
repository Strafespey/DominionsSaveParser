# Driving the Dominions 6 engine as a data source

`Dominions6.exe` carries a number of undocumented switches that dump internal
data. Some are far more reliable than reverse-engineering the binary format,
so the toolchain uses the engine as a data source wherever it can.

## Running headless

The executable is a **GUI-subsystem** binary, but it writes to inherited
redirected handles, so `subprocess` with `capture_output=True` works.

Always pass `--nosteam --nocrashbox` (no Steam handshake, no modal crash box).

`--textonly` is **not** a general headless mode. The engine rejects it unless
combined with one of `--tcpserver`, `--tcpquery`, `--makemap`, `--newgame` or
`--host`:

```
Något gick fel!
Text only mode can only be used with --tcpserver, --tcpquery, --makemap, --newgame or --host
```

## Environment variables

Read by the engine (found in its string table):

| Variable | Purpose |
|---|---|
| `DOM6_SAVE` | savedgames root — **use this to sandbox** |
| `DOM6_DATA` | data directory |
| `DOM6_CONF` | config directory |
| `DOM6_MODS` | mods directory |
| `DOM6_LOCALMAPS` | local maps directory |

`DOM6_SAVE` is what makes safe experimentation possible: point it at a temp
copy of a savegame and the engine will never touch the real one.

## Safe read-only dump switches

These print and exit without touching a savegame. All are wired up in
`dom6.engine.Engine` and `scripts/extract_reference.py`.

| Switch | Output | Verified yield |
|---|---|---|
| `--listnations` | `id  Name, Subtitle`, grouped by era | 103 nations |
| `--listspells` | `id  Spell Name` | 1473 spells |
| `--listevents` | `id  event text` (with `##godname##` placeholders) | 3302 events |
| `--comsumrits` | TSV: path, level, cost, ints, unit, ritual name | 146 rituals |
| `--help` | full switch list | — |
| `--version` | version string | — |

`--listbless` and `--liststartarmy` produced no output — they probably need a
nation argument.

Note the output is UTF-8 (`Pyrène`), so decode explicitly rather than relying
on the console codepage.

## `--dumpfights` — battle rosters ⚠️ mutates the save

`--dumpfights` only takes effect while the engine **hosts a turn**, which
advances the game. Always run it against a copy (`dom6.engine.SandboxedHost`
does this: it copies the folder to a temp dir and points `DOM6_SAVE` at it).

```
Dominions6.exe --nosteam --nocrashbox --textonly --vcrdebug --dumpfights --host <GameName>
```

Output shape:

```
Pangaea attacking Independents in Henwood with PD 0 (poptype 77)
attstr 1557, defstr 367 (PDstr 0)
commanders:
   1+0 Centaur Commander
units:
  12+0 Satyr
   8+0 Minotaur
commanders:
   1+0 Atavi Chieftain
units:
  29+0 Atavi Archer
```

What it gives you: every battle that turn, both sides' commanders and units
with counts, and the engine's own attack/defence strength estimates.

What it does **not** give you: any per-hit detail. It is a roster dump.

### Caveats

1. **Roster lag — confirmed and corrected.** Roster blocks lag their header
   line by exactly one battle: the first header is followed by empty rosters,
   and each later header is followed by the *previous* battle's roster.
   Confirmed across two hosts that emitted battles in different orders (a
   "Phaeacia attacking …" header was followed by Ulm's units, belonging to the
   preceding "Ulm attacking …" battle). `parse_dumpfights(align=True)` — the
   default — undoes the shift; after alignment every attacker roster matches
   its nation's units. Unavoidable consequence: **the final battle of a host
   never gets a roster printed**, flagged as `rosters_missing`.

2. **⚠️ This dumps the NEXT turn's battles, freshly simulated — it is not a
   replay of the battles already in your `.trn`.** Hosting consumes
   `ftherlnd` + the `.2h` orders and generates the *upcoming* turn. Re-running
   it produces **different results each time**: across two runs of the same
   savegame, Ulm attacked Dragon Ridge in one and Ebys in the other, and
   Mictlan's attack strength went from 1497 to 1640. AI orders and random
   outcomes are re-rolled per host.

   So for *"why did I lose the battle I just watched?"* — a battle in the past —
   `--dumpfights` is the **wrong tool**. That battle lives in the `.trn` as a
   `_vcr_VCR` record (see `FILE_FORMAT.md`). `--dumpfights` is useful for
   *forecasting*: "what is about to happen given my current orders", and for
   sampling outcome variance by hosting the same turn repeatedly.

3. **Information scope.** Hosting dumps *every* nation's battles, not just
   yours. Fine for solo play; more than a player should see in live multiplayer.

The meaning of the `N+M` count format (e.g. `12+0 Satyr`) is not yet established.

## Other switches worth investigating

| Switch | Note |
|---|---|
| `--vcrtest`, `--vcrseed=`, `--vcrrepeat` | replay-system test harness |
| `--vcrdebug` (`-dd`) | replay debug output |
| `--simulation`, `--simnat=`, `--simamount=`, `--simspells` | built-in battle simulator — a route to "what if" analysis |
| `--statusdump` | writes `<save>/<game>/statusdump.txt` |
| `--statfile` | writes `stats.txt` after each turn |
| `--scoredump` | writes `scores.html` after each turn |
| `-d` | increase debug level (repeatable) |

The engine also references `%s/%d_%d.vcr` and `%s/5_0.vcr` file paths, plus a
`%s/tmp_vpb` temp file used by `ViewProvinceBattles`. No `.vcr` files exist on
disk during normal play — replays live inside the `.trn`.

## The stat tables are not dumpable — but they are extractable ✅

No switch exposes unit/weapon/armour stats, and `data/` ships only art assets.
They are compiled into the executable as arrays of fixed-size structs with the
names stored **inline** (not behind pointers — a pointer search finds nothing).

**The monster table is extracted** by `dom6.gamedata` — 4115 names,
ids 0..4137, stride 888 bytes.

It was located by cross-referencing ids proven from real savegames: a battle
whose roster came from `--dumpfights` established that type 1122 is
"Atavi Infantry", 1125 "Vanara Infantry" and 1141 "Tiger Rider". Locating those
strings in the executable and dividing the gaps by the id differences yields
the stride and base.

The addresses are **not hard-coded**. `solve_layout()` re-derives them from the
anchors at run time and then checks the result against ids that were *not* used
to derive it (17 Archer, 30 Militia, 428 Assassin, 3550 Armored Sacred Tiger,
…). If validation fails it raises rather than returning wrong names, so a game
patch that moves the table produces a clear error instead of silent garbage.

**The weapon table is extracted** too — 887 weapons, stride 152 bytes, ids
following Dominions' documented numbering (`0` Nothing, `1` Spear, `2` Pike).

| Field | Offset | Notes |
|---|---|---|
| name | `+0` | inline, NUL-terminated |
| **length** | `+54` | melee reach; `0xFF` on natural weapons |
| **range** | `+56` | missile range; `0xFF`/`0xFD` = strength-derived |

Validated against the manual, which states *"a human (size 3) wielding a mace
(length 1)"* — the extracted Mace length is exactly 1. Ranges corroborate
independently: Sling 30, Short Bow 35, Crossbow 40, Long Bow 45, Arbalest 50.
Spear 3, Long Spear 4, Pike 5, Dagger 0.

Natural weapons (claws, bites) store `0xFF`; the manual describes them as
"weapon length zero", so it is a sentinel rather than a length of 255. They are
exposed as `length is None` with `effective_length == 0`.

> Caveat: `+54` is only meaningful for ordinary weapons. Special attacks
> ("Hypnotize", "Spectral Fire", "Wail") also carry values there that are
> unlikely to be reach. Trust it for physical weapons.

### Unit combat stats ✅

The stat block sits at `+40`..`+62` of the monster record, values two bytes
apart:

| Offset | Stat | Offset | Stat |
|---|---|---|---|
| `+40` | action points | `+52` | encumbrance |
| `+44` | **size** | `+54` | magic resistance |
| `+46` | **hit points** | `+56` | **attack** |
| `+48` | **protection** (natural only) | `+58` | **defence** |
| `+50` | strength | `+60` | precision |
| | | `+62` | **morale** (`50` = mindless) |

Identified from invariants rather than guesswork, then checked against facts
the offsets were *not* chosen to satisfy (`validate_monster_stats()`):

- **size** — the manual says a square holds *"10 size points"* and that giants
  are *"size 6+"*; the field maxes at exactly 10, giants read 6, humans 3, and
  the manual's own worked example calls a human *"size 3"*.
- **hit points** — rises monotonically with size: mean hp is 3.1 at size 1,
  12.2 at size 3, 42.5 at size 6, 157.5 at size 10.
- **attack vs defence** — units whose defence exceeds attack are agile types
  (Sprite, Ghost King, Spectator); units whose attack exceeds defence are
  immobile trees reading **defence 0** (Dying Treelord, Irminsul, Hamadryad).
- **morale** — 5–18 for living units and exactly **50** for mindless undead,
  which never rout.
- **encumbrance** — 0 for undead and inanimate, 2–4 for the living.

Spot check:

```
Militia               hp 10 sz 3 prot  0 str 10 att  8 def  8 mr 10 enc 4 mor 8
Sprite                hp  2 sz 1 prot  0 str  3 att 14 def 20 mr 14 enc 1 mor 7
Elephant              hp 61 sz 9 prot 11 str 20 att  9 def  8 mr  5 enc 3 mor 8
Jotun Jarl            hp 40 sz 6 prot  5 str 23 att 13 def 12 mr 10 enc 3 mor 14
Longdead              hp  5 sz 3 prot  0 str 10 att 11 def  9 mr 10 enc 0 mindless
```

`protection` is **natural protection only** — worn armour adds to it, and the
armour table is not decoded yet, so armoured units read lower than they fight.

### Unit → weapon link ✅

The 888-byte monster record carries the ids of the weapons the unit wields:

| Field | Offset | Slots |
|---|---|---|
| weapon ids | `+832` | 7 × u16, `0` = empty |
| armour ids | `+852` | 4 × u16, `0` = empty |

Found by requiring Longbowman → Long Bow and Crossbowman → Crossbow, then
confirmed across the whole table by inspection:

| Unit | Weapons |
|---|---|
| Longbowman | Short Sword (len 1), Long Bow (range 45) |
| Archer | Dagger (len 0), Short Bow (range 35) |
| Militia / Light Infantry | Spear (len 3) |
| Heavy Infantry | Broad Sword (len 1) |
| Deer Tribe Warrior | Spear (len 3), Javelin |
| Armored Sacred Tiger | Bite, Claw (both natural → length 0) |

### Armour table ✅

298 entries, stride 104, ids `0` Nothing, `1` Buckler, `2` Shield,
`3` Kite Shield, `4` Tower Shield, `5` Leather Cuirass … `19` Full Plate Mail,
`20` Iron Cap, `21` Full Helmet.

| Field | Offset | Notes |
|---|---|---|
| slot | `+36` | `1` head, `2` body, `5` shield |
| protection | `+38` | where the piece actually covers |
| body protection | `+42` | averaged over the whole body |
| weight | `+68` | rises with bulk (Buckler 1, Full Plate Mail 25) ❓ |

**Two protection fields, and the difference matters.** A Plate Cuirass reads
21 at `+38` but only 8 at `+42`, because it covers the torso alone; Full Plate
Mail reads 21 in both. `+42` is the figure that adds to a unit's natural
protection.

`MonsterTable.total_protection()` sums natural protection with **body armour
only** — helmets and shields protect their own areas rather than raising
overall protection, so including them would overstate it. Shields are reported
separately as `+shield`.

The base was anchored on the table's own first entry (`0` = "Nothing", matching
the weapon table's convention), *not* by automatic scoring: several candidate
bases resolved every referenced id to a valid name, and the highest-scoring one
was wrong — it gave Militia a Tower Shield and Heavy Infantry two body armours
at once. The check that settles it is that each unit ends up with exactly one
body piece, one helmet and at most one shield:

```
Militia               natural  0 -> total  3   Leather Cuirass, Reinforced Leather Cap, Shield
Heavy Infantry        natural  0 -> total  9   Ring Mail Hauberk, Iron Cap, Shield
Longbowman            natural  0 -> total  3   Leather Cuirass, Leather Cap
Tiger Rider           natural  1 -> total 12   Scale Mail Hauberk, Iron Cap, Buckler
Infantry of Ulm       natural  0 -> total 19   Full Chain of Ulm, Half Helmet of Ulm
Black Plate Infantry  natural  0 -> total 23   Full Plate of Ulm, Full Helmet of Ulm
Markata Archer        natural  0 -> total  0   (nothing)
```

Longbowmen carrying no shield is a good sign — a longbow needs both hands.
`+68` was left under a neutral name because resource cost and encumbrance were
not told apart.

### Why this matters

The manual gives the repel rule outright:

```
Repel morale check
Attacker morale check: morale + DRN - (weapon length difference)
...units with claws and bites (weapon length zero) are easier to repel.
```

Weapon length is therefore the quantity behind advice like *"your light
infantry took free hits from long weapons"*.
