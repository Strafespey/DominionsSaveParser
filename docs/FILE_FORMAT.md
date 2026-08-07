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

### Consequences for analysis

- Army composition, placement, equipment, orders and casualties are all
  recoverable from the save.
- A true per-hit log requires the **engine** to replay the fight. The engine has
  the format strings for it (`damage %d on %s (unr%d), spec0x%x ba%d`,
  `%s attacks with %s`, `Shield hit, incoming damage reduced by %d`) but they
  did not appear at debug level `-d -d`. Reaching them is an open problem.

---

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
