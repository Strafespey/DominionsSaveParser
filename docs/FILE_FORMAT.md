# Dominions 6 save file format — reverse engineering notes

> **Status legend**
> - ✅ **Verified** — checked against real save data from multiple games.
> - 🟡 **Probable** — strong evidence, not yet cross-checked.
> - ❓ **Hypothesis** — plausible, untested. Do not build on these.

The official `dom6fileformats.pdf` shipped by Illwinter documents **only the
`.d6m` map-recipe format** (one page). The savegame format is undocumented;
everything below was derived by inspecting real files.

---

## 1. Files in a savegame folder

Location: `%APPDATA%/Dominions6/savedgames/<GameName>/`, overridable with the
`DOM6_SAVE` environment variable (see `ENGINE_TOOLING.md`).

| File | Role |
|---|---|
| `ftherlnd` | ✅ Master game state, all nations. Written by the host. |
| `<era>_<nation>.trn` | ✅ Per-player turn file: what that player may see, plus messages and **battle replays**. |
| `<era>_<nation>.2h` | ✅ Per-player orders, written by the client at end turn. |
| `__*.map` / `__*.d6m` | ✅ Map files. `.d6m` is the documented format. |

All three save types share the same header and string encoding.

---

## 2. Header ✅

All multi-byte integers are **little-endian**. Verified across `ftherlnd`,
`.trn` and `.2h` from three different games.

| Offset | Type | Meaning |
|---|---|---|
| `0x00` | 3 bytes | preamble `01 02 04` |
| `0x03` | 3 bytes | ASCII magic `"DOM"` — **not** obfuscated |
| `0x06` | u16 | version — `6001` for Dominions 6 |
| `0x08` | u16 | always `2` so far ❓ sub-version |
| `0x0A` | i32 | per-game constant (`627`, `636`) ❓ province count |
| `0x0E` | i32 | ✅ **turn number** (`9`, `1`, `0`) |
| `0x12` | i32 | `1` in `ftherlnd`/`.trn`, `0` in `.2h` |
| `0x16` | i32 | per-game constant (`11036`, `20847`, `-1`) ❓ map seed |
| `0x1A` | i32 | ✅ **owning nation id**; `-1` in `ftherlnd` |
| `0x1E` | i32 | `1` in `.2h` only |
| `0x22` | i32 | nonzero only in `.2h` ❓ orders checksum |
| `0x26` | string | ✅ obfuscated game name |

Nation ids resolve against `--listnations`: `68` = Bandar Log,
`69` = T'ien Ch'i, `77` = Phaeacia, `0` = Independents.

---

## 3. String obfuscation — XOR 0x4F ✅

Every text string is stored XOR'd byte-by-byte with `0x4F` and NUL-terminated
(the terminator is stored as `0x4F`, i.e. `0x00 ^ 0x4F`).

Numeric fields are **not** obfuscated. You must never XOR a whole save file —
XOR only while reading a string field.

Worked example — raw `2e 23 23 6f 26 21 6f 3b 27 2a 6f 36 2a 2e 3d 6f`
→ `"all in the year "`.

Traps this creates:
- Raw `0x4F` inside a string region is a **terminator**.
- Raw `0x6F` is an ASCII space; raw `0x00` is the letter **`O`**.
- A run of `0x00` padding therefore decodes to `OOOO...` and *looks* like text.
  Small int32 values likewise decode to printable ASCII. A naive printability
  scan reports text almost everywhere. `dom6.save.SaveFile.strings()` works
  around this by anchoring on `0x4F` terminators and walking backwards through
  a conservative alphabet, stopping at a run of 3+ zero bytes.

### Byte distribution

Whole-file entropy of a `.trn` is ~2.2 bits/byte; `0x00` (44.8%) and `0xFF`
(42.9%) make up ~88% of the file. **The file is not compressed** — that
distribution is just large sparse arrays where empty slots are `0` or `-1`.
(`zlib1.dll` ships with the game but is used for assets and gzipped server
logs, not savegame bodies.)

---

## 4. Battle replays — the `_vcr_VCR` section ✅

**Battles are not stored as a blow-by-blow log.** The engine stores the battle
*setup* plus an RNG seed and per-round checksums, then **re-simulates the fight
deterministically** every time you watch the replay. The real-time combat log
you see in the replay viewer is *generated on the fly*, not read from disk.

Evidence, from strings inside `Dominions6.exe`:

```
Battle inconsistency, round %d (calc %d, loaded %d)
battle incon (round %d, seed %d)
Playvcr lnr%d def%d att%d incstle%d seed%d checksums%d
readchecksum %d checksums
--useolddata    Try to preserve battle replays after upgrading
```

The `calc` vs `loaded` comparison is the giveaway: the engine recomputes each
round and asserts it matches the stored checkpoint. That is also why replays
break after a patch.

### Locating replays

Each replay is introduced by the literal 8-byte ASCII marker **`_vcr_VCR`**,
stored raw (not obfuscated). Replays are interleaved into the province stream,
immediately before the record of the province the battle happened in.

Layout relative to the marker:

| Offset | Type | Meaning |
|---|---|---|
| `+0x00` | 8 bytes | `_vcr_VCR` |
| `+0x08` | i32 | ✅ version — `4` |
| `+0x0C` | i32 | constant `50` so far |
| `+0x10` | i32 | ✅ **nation id of one side** (`0` = independents) |
| `+0x14` | i32 | ✅ **nation id of the other side** |
| `+0x18` | i32 | constant `2` ❓ number of sides |
| `+0x1C` | i32 | 🟡 **RNG seed** |
| `+0x20`… | i32 | further fields, meaning unknown |
| `+0x41` | string | ✅ battlefield / province name, stored **twice** |

Verified example — turn-9 Bandar Log `.trn`, 2 replays:

```
VCR #0 @0x00027351 v4 Independents vs Bandar Log in 'Trackless Woods' seed=115
VCR #1 @0x00036961 v4 Bandar Log  vs Phaeacia    in 'Trackless Woods' seed=9187
```

Corroborated by the province event text in the same file:
`"Trackless Woods was conquered by Bandar Log"`. A turn-1 `.trn` from a
different game contains zero markers, consistent with no battles yet.

### The combatant record — 173 bytes ✅

Inside a replay body sits an array of fixed-size 173-byte records, one per
combatant. The stride was found by measuring the dominant repeat distance of
u16 values across the body (173 won with 1860 votes; the next candidate had
210). Field meanings were then established with **labelled ground truth**:
host a turn with `--dumpfights` to get a known roster, then parse the `.trn`
that same host wrote.

| Offset | Type | Meaning |
|---|---|---|
| `+19` | u8 | constant within a squad ❓ |
| `+20` | u16 | ✅ **squad id**; `0xFFFF` marks a commander |
| `+23` | u16 | ✅ **monster type id** |
| `+27` | u8 | file-global stamp — see warning below |
| `+29` | u8 | constant per side ❓ |
| `+55` | u8 | ✅ **owner nation id** (`0` = independents) |
| `+164` | u16 | unit number 🟡 |

Grouping by `+20` reproduces the roster stacks exactly, which is what confirms
it as the squad id:

```
owner  0 squad   18:  15 Archer
owner  0 squad   35:  26 Militia
owner  0 squad   63:  22 Light Infantry
owner  0 squad 65535:   3 Commander            <- commanders
owner 68 squad 5048:  12 Tiger Rider + 12 Armored Sacred Tiger
owner 68 squad 5063:  30 Atavi Infantry + 24 Vanara Infantry
```

Note squad 5048: **mounts inherit their rider's squad**, so a cavalry squad
reports twice as many members as riders.

Verification, battle in "The Mire of Mystery": 145 records split
**79 Bandar Log / 66 Independents** by `+55`, and grouped by `+23` as:

| Owner | Types found | `--dumpfights` roster |
|---|---|---|
| 68 | `1122`×30, `1125`×24, `1141`×12, `3550`×12, `1135`×1 | 30 Atavi Infantry, 24 Vanara Infantry, 12 Tiger Rider, 1 commander |
| 0 | `30`×26, `28`×22, `17`×15, `34`×3 | 26 Militia, 22 Light Infantry, 15 Archer, 3 Commander |

The 12 extra records are the **Tiger Riders' mounts** — mounts are separate
combatants, consistent with the engine's
`bc: Mount (%s) and master (%s) have different owners`. Type `3550` appears
exactly as often as type `1141` in every battle observed, confirming the
pairing. `+20 == 0xFFFF` selected exactly the 4 commanders the roster reported.

> ⚠️ **`+27` is not a magic number.** It is identical across every record
> within one file (`0x31` in a turn-10 `.trn`) which makes it a tempting
> anchor, but a turn-9 `.trn` of the *same game* carries `50` there, and the
> same value appears in the replay header. Anchoring on a hard-coded value
> silently finds nothing in other files. Records are located by field
> plausibility, requiring a run to share whatever stamp its first record has.

### Battlefield placement is NOT in the replay ❌

Searched for and **not found**. Recording the negative result so it is not
re-investigated:

- **No per-unit x/y in the combat record.** Every field that separates cleanly
  by owner turned out to be one already identified (`+20` squad, `+23` type,
  `+164` unit number). Nothing in the 173 bytes behaves like a coordinate.
- **No squad position table before the unit array.** The ~47 KB preceding the
  array in one replay contains none of that battle's squad ids
  (`18, 35, 63, 5048, 5063`) — a single coincidental match for `35` aside.

The most likely explanation is that Dominions **recomputes deployment** at
battle start from squad composition, formation and battle orders, all of which
are deterministic given the stored seed. The engine's own strings support this:
`Box formation`, `Line formation`, `Skirmish formation`, sparse line, and
*"Units with the Guard Commander order always deploy next to the commander they
are guarding."*

So the squad layout the player arranges on the army-setup screen persists with
the **army**, not with the battle. To recover front/back placement, map the
army records in the `.trn` / `.2h` (squad definitions with their placement and
formation) rather than looking inside the replay.

What *is* available today from the replay: full squad composition per side,
which unit types are grouped together, and each type's weapons with reach and
range — enough to reason about reach mismatches and missile duels without
knowing exact coordinates.

### Locating arrays outside replays 🟡

The same 173-byte record is used for **armies standing on the map**, not just
combatants in a replay. `dom6.vcr.find_unit_arrays()` scans a whole file for
them.

This is **best-effort**: the record has no magic number, so a run offset by a
few bytes from a genuine array still passes a per-field plausibility test.
Overlapping candidates are resolved in favour of the longest, and arrays with
more than two distinct owners are rejected — but false positives remain
(clusters of type ids like `2048`/`255`/`3072` in `ftherlnd` are aliases, not
armies). Inside a replay, where the two nation ids are known and can constrain
the owner field, detection is reliable and verified.

### Consequences for analysis

- Army composition, placement, equipment, orders and casualties are all
  recoverable from the save.
- A true per-hit log requires the **engine** to replay the fight. The engine has
  the format strings for it (`damage %d on %s (unr%d), spec0x%x ba%d`,
  `%s attacks with %s`, `Shield hit, incoming damage reduced by %d`) but they
  did not appear at debug level `-d -d`. Reaching them is an open problem.

---

## 4b. Battle scripting — vocabulary known, storage NOT found ❌

Dominions lets you script a commander with an ordered list of actions ("cast
this spell, then this one, then hold, then advance") plus a target preference.
Being able to read that back is what would allow advice like *"script the
archers to hold twice so they out-range the javelin throwers"*.

**The vocabulary is recovered** from the executable's string table.

Commander orders (letter shortcuts in parentheses):

| Order | Description |
|---|---|
| (a) Attack | Move towards enemies to engage in melee |
| (v) Attack one turn | Move towards a random enemy for one combat round |
| (y) Fly Attack one turn | As above, flying |
| (f) Fire | Fire missile weapons against enemies |
| (e) Fire and keep distance | Fire until the target closes, then withdraw |
| (c) Cast spells | The computer chooses spells |
| (d) Advance and cast spells | Advance to the front and cast |
| (s) Stay behind troops | Cast, fire, or hang back |
| (g) Guard commander | Deploy next to the commander being guarded |
| (h) Hold and attack | **Hold position for two turns, then advance** |
| (r) Retreat | Leave the battlefield |

Squad orders: Attack, Hold and attack, Fire, Hold and Fire, Fire and keep
distance, Retreat, Guard commander.

Targets: closest enemy, rearmost enemies, enemy archers, enemy cavalry,
enemy fliers, large enemy monsters.

**Where scripts are stored is still unknown.** Two negative results worth
recording so they are not re-investigated:

- They are **not** in the 173-byte combat record. Commander records there are
  almost entirely zero outside unit state (`+23` type, `+55` owner, `+164`
  unit number). Apparent "spell id" hits at `+60`/`+168` are coincidences —
  `255` and `83` falling out of `0xFF` sentinel bytes and a terminator.
- Diffing a commander between `.trn` and `.2h` does not work directly: the
  two files do not share unit numbering (196 distinct unit numbers in the
  `.trn` versus 17 in the `.2h`, overlapping only on junk values such as
  `0`, `1`, `65535`).

The `.2h` does contain 173-byte unit records, so it is the most likely home,
but its record layout has not been mapped.

### How to unblock this

The same technique that cracked the combat record — **labelled ground truth** —
applies. Set a distinctive, known script on one commander (e.g. slot 1 a
memorable spell, slots 2–3 "hold", target "rearmost enemies"), end the turn,
and keep the `.2h`. Then change *only* that script and end turn again. Diffing
two `.2h` files that differ in exactly one known way localises the field
immediately.

## 5. Province records 🟡

Provinces occupy the bulk of a `.trn`. Each record contains the province name
**twice** in succession (e.g. `Redbud Grove` at `0x1BC` and again at `0x1C9`) —
probably the current name and the original/base name, since renaming is a game
feature. Event messages for the province follow inline:

```
@0x00E95  "Early Fall in the year 0 of the ascension wars:"
@0x00EC7  "Sleepy Mountains was conquered by Ulm"
```

Exact field layout is not yet mapped.

---

## 6. Nation records 🟡

Roughly `0x373B8`–`0x461EF` in the sample file, spaced ~3900 bytes apart.
Contain the pretender's name (`Jamasp`, `Harald`, `Gangr`) and title strings
(`the Most High, King of Kings, the Evil Prince, King of the Crafts`).
Nations the player has not met read `unknown`.

---

## 7. Open questions

- [ ] Province record field layout and length.
- [ ] Unit/army records: unit type id, count, squad number, x/y battlefield placement.
- [ ] Commander records: equipment slots, magic paths, battle script (spell order).
- [ ] VCR body after `+0x20`: per-round checksums, unit lists, outcome.
- [ ] Header fields at `0x08`, `0x0A`, `0x12`, `0x16`, `0x1E`, `0x22`.
- [ ] How to reach the engine's per-hit combat logging.
