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

### Size accounting — there is no room for a log ✅

The engine-string argument above is suggestive; this is the measurement.
Reproduce with `py scripts/vcr_anatomy.py <GameName>`.

Each replay section splits into three parts:

| Battle | Combatants | Header | Units (n × 173) | Tail |
|---|---|---|---|---|
| Shamballac | 199 | 47,617 B (82% `0xFF`) | 34,427 B | **1,974 B** |
| Gold Mountains | 8 | 49,377 B (79% `0xFF`) | 1,384 B | **642 B** |
| Trackless Woods | 84 | 46,821 B (83% `0xFF`) | 14,532 B | **1,639 B** |
| Trackless Woods | 89 | 47,811 B (82% `0xFF`) | 15,397 B | **1,178 B** |

Two facts kill the stored-log hypothesis:

1. **The header does not scale with the battle.** The 8-combatant fight has a
   *larger* header than the 199-combatant one. It is 79–83% `0xFF` — fixed-size
   tables initialised to −1 — and holds nation slots (mostly the string
   `unknown`, for nations the player has never met), the map filename,
   `IOversion 6.35`, and the pretender's name. It is per-battle context, and
   its size is essentially constant at ~47–49 KB across two different games.

2. **The tail is one to two orders of magnitude too small.** It is the only
   part that scales with the battle (roughly 600 B fixed plus ~7 B per
   combatant). A minimal per-hit event — attacker, target, damage, flags —
   cannot be under ~6 bytes. Shamballac's 199 combatants over even 30 rounds
   would need ≥ 35,820 B. The tail holds 1,974 B: **5.5%** of the floor.

The tail is the right size for the **per-round checksums** the engine's strings
describe, plus outcome data. It is not a log.

Corroborating detail: the whole 422 KB turn file also carries 121 province
records, the full score history and every message. There is nowhere else for
36 KB of combat log to hide.

> **This does not mean the replay is lossy.** Initial state plus a stored seed
> reproduces a deterministic simulation exactly, frame by frame, at any speed.
> From the viewer's side "recorded" and "reproducible" are indistinguishable —
> which is why the in-game replay viewer is not evidence either way. The
> consequence for *this* project is narrower: there is no per-hit record to
> read, so casualties must be inferred (§4c) and a blow-by-blow narrative has
> to come from the engine, not the file.

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
| `+57` | u32 | ✅ **army stack id**; `0xFFFFFFFF` = unset. *Not* a position — see below |
| `+164` | u16 | ✅ unit number — unique per record |

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

### Army stack id — `+57` (u32) ✅

> **Correction, twice over.** The original revision recorded placement as *not
> present*. A later revision "corrected" that and decoded `+57`/`+58` as squad
> position x/y. **The original was right and the correction was wrong.** No
> battlefield placement is stored anywhere in the save; the engine recomputes
> deployment from squad, formation and orders at battle start. The bad reading
> reached a user as a confident claim that his mage line was stacked on one
> tile, which it was not.

Bytes `+57`..`+60` are a little-endian **u32 army stack id** — which army a
unit marched in with. `0xFFFFFFFF` means unset.

Three things distinguish it from a coordinate pair:

1. **The high half is degenerate.** Across every record in a turn-28
   T'ien Ch'i `.trn`, bytes `+59`/`+60` are only ever `00 00` (308 records) or
   `FF FF` (115). Two more coordinate bytes could not behave that way; a u32
   holding a small id or `-1` does exactly that.
2. **It spans squads.** At Nardago six *different* squads all read `4803`,
   while a seventh — a detachment that arrived separately — read `3920`. As a
   byte pair that rendered as six squads sharing the tile `(195, 18)`, which
   is what a position field cannot mean.
3. **Defenders read `-1`.** The entire defending side is `0xFFFFFFFF`.
   Engine-deployed defenders have no player-assigned stack, but they
   unquestionably have positions.

The evidence once cited *for* the position reading says the same thing once
converted: the two sides "sitting apart" at `(140, 20)` and `(82, 14)` is
stacks `5260` and `3666`, and squads at `(100, 4)` / `(93, 4)` — which looked
like two squads on one rank — are ids `1124` and `1117`, consecutive stack
numbers. The `.trn`/`.2h` agreement was real; it just confirmed a stable id,
not a placement.

Regression: `tests/test_vcr_regression.py::test_stack_field_is_not_a_coordinate_pair`.
It asserts the high half stays degenerate and that `VcrUnit.position` does not
come back.

In a battle the two sides sit apart:

```
Bandar Log
  squad 5063 (1)  at (140, 20)   1 x Atavi Infantry
  squad 5075 (10) at (140, 20)  10 x Markata Archer
  squad 5113 (26) at (140, 20)  13 x Tiger Rider + 13 mounts
  commanders                     (unset)
Phaeacia
  squad 183 (49)  at (82, 14)   49 x Longbowman
```

Commanders read unset, as do squads the engine deploys itself (independent
province defenders show `0xFF/0xFF` throughout).

**What is not pinned down** is the coordinate space. It is probably the
army-setup grid the player arranges squads on, but that is unproven, and in one
battle three separate squads shared a single pair while in another they
differed — so treat the values as relative, not absolute. Deriving a reliable
"front row versus back row" from them needs more evidence.

Formation (line / sparse line / box / skirmish) and battle orders are still
unmapped; the engine strings confirm they exist
(*"Units with the Guard Commander order always deploy next to the commander
they are guarding"*).

### Casualties are inferred, not stored ⚠️

There is **no casualty list and no per-unit death flag**. Tested directly: two
battles occur in the same province on the same turn, so the units missing from
the second are exactly those lost in the first — and comparing those records
against the survivors' finds **no offset that separates them**. The replay
holds the state at battle *start*; the outcome is produced by re-simulating.

`dom6.analysis.battle_outcomes()` therefore *infers* losses: a unit is counted
lost in battle *i* if it fought there and appears neither in a later battle of
the same turn nor among the units still on the map afterwards.

Checking later battles is what makes the attribution correct. Without it, a
unit that survived the first fight and died in the second is charged to both —
which inflated one battle from 3 losses to 16.

**Two caveats, kept explicit in the API rather than averaged away:**

1. **Enemy losses are not confirmed kills.** A turn file only shows what its
   owner can see, so enemy survivors are invisible whether they died or merely
   walked away. `SideOutcome.observable` is `False` for every nation except the
   file's owner, and `.caveat` spells this out.
2. **Own losses depend on complete map-army detection.** A missed array
   overstates losses. This is why the unit-number uniqueness filter matters.

Worked example from a real turn-9 file:

```
Trackless Woods — Independents vs Bandar Log
  Independents: 43 engaged,  1 survived, 42 lost (98%)   [not confirmed kills]
  Bandar Log:   41 engaged, 38 survived,  3 lost (7%)
      -1 Bandar Noble, -1 Tiger Rider, -1 Armored Sacred Tiger

Trackless Woods — Bandar Log vs Phaeacia
  Bandar Log:   39 engaged, 22 survived, 17 lost (44%)
      -6 Armored Sacred Tiger, -5 Tiger Rider, -4 Markata Archer, ...
  Phaeacia:     50 engaged,  2 survived, 48 lost (96%)   [not confirmed kills]
```

Riders and mounts are separate units, so they are lost separately — 5 Tiger
Riders and 6 of their tigers, meaning one tiger outlived its rider.

### Locating arrays outside replays 🟡

The same 173-byte record is used for **armies standing on the map**, not just
combatants in a replay. `dom6.vcr.find_unit_arrays()` scans a whole file for
them.

The record has no magic number, so a run offset by a few bytes from a genuine
array still passes a naive per-field plausibility test. Three filters separate
them, in increasing order of power:

1. Overlapping candidates resolve in favour of the longest.
2. Arrays with more than two distinct owners are rejected.
3. **Unit-number uniqueness** (`+164`) is the decisive test. Unit numbers are
   per-unit identifiers, so a genuine array has almost no duplicates. Measured
   across a real turn file, genuine arrays score **1.00** while every
   byte-shifted alias scores between **0.01 and 0.17**.

Passing `known_types` (the extracted monster id set) tightens it further.

Without test 3 the detector was actively wrong: a 101-record alias of
"Wailing Lady" — 98 of whose records claimed to be commanders — outranked and
suppressed the player's real armies, so a scan of the player's own turn file
reported *no* armies at all.

### Consequences for analysis

- Army composition, placement, equipment, orders and casualties are all
  recoverable from the save.
- A true per-hit log requires the **engine** to replay the fight — the file
  provably does not contain one (see the size accounting in §4). Nearby engine
  strings show the replay machinery is **seed-driven and file-backed**:

  ```
  play vcr (seed %d)          playvcr nbr %d (seed %d) ok %d
  %s/%d_%d.vcr   %s/5_0.vcr   failed to open vcr
  readvcr, lnr %d, seed %d    readvcr: bad CHECK
  crvcr: bad seed             crvcr: put land %d, owner %d, fortowner %d, p...
  ```

  Note `%s/%d_%d.vcr`: the engine reads and writes **standalone `.vcr` files**,
  not only the replays embedded in a `.trn`, and both `crvcr:` (create) and
  `readvcr:` (read) paths exist, so the format round-trips. No such files exist
  during normal play. Making the engine emit one is the most promising lead for
  driving a re-simulation headlessly.

  The format strings themselves are present and unambiguous —
  `damage %d on %s (unr%d), spec0x%x ba%d`, `%s attacks with %s`,
  `Shield hit, incoming damage reduced by %d` — but they do not appear on
  stdout at any debug level tried so far (see `ENGINE_TOOLING.md`).

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

## 4c. ⚠️ Inferred casualties cannot decide a battle

**A defeat reads as a crushing victory.** This bug shipped, produced a
confident wrong analysis of a real game, and is the reason `owner` was decoded.

The chain: `battle_outcomes()` counts a unit lost if it is not visible on the
map afterwards. A turn file only shows what its owner can see, so enemy
survivors are *never* visible — and losing a battle also loses sight of the
province, which makes the enemy look annihilated. Every enemy side ever
reported for one real game:

```
turn 13  Koromoo   100%      turn 20  Shamballac      99%   <- actually LOST
turn 13  S'catli   100%      turn 20  Gold Mountains  88%   <- actually LOST
turn 13  Pnophia    98%
```

The figure is not measuring the enemy. **Never present an enemy loss fraction
as evidence of an outcome.** Use province ownership (§5). `SideOutcome.caveat`
carries this, and `tests/test_province_owner.py` pins it.

Own-side losses remain usable: your own survivors *are* on the map, including
after a retreat.

## 5. Province records 🟡

Each record contains the province name **twice** in immediate succession
(e.g. `Redbud Grove` at `0x1BC` and again at `0x1C9`) — probably current name
and base name, since renaming is a game feature. Event messages for the
province follow inline:

```
@0x00E95  "Early Fall in the year 0 of the ascension wars:"
@0x00EC7  "Sleepy Mountains was conquered by Ulm"
```

### Owner 🟡

| Offset | Type | Meaning |
|---|---|---|
| end of 2nd name `+34` | u8 | 🟡 **owner nation id**; `0` = independent *or* never seen |

Located by constraint rather than by mapping the record: it is the only offset
whose per-nation counts reproduce the score record's province column (§7)
across `ftherlnd` and `.trn` in two different games. Cross-checks that hold:
no nation is ever *over*counted, the player's own count matches exactly in
their `.trn`, and nations the player has never met read 0 there while reading
correctly in `ftherlnd`.

⚠️ **Enumeration is incomplete — about 90% of owned provinces are found.**
Every nation comes up 1–2 short; none over. Some province records evidently do
not match the twice-repeated-name signature (renamed provinces are the leading
suspect). So a province that is found is reliable; a province that is missing
is **unknown**, not unowned. `owner_of()` returns `None` for that case and
callers must not read it as "nobody".

Battle replays also store their province name twice (`+0x41`), so replay spans
must be excluded or they appear as phantom province records — one such phantom
reported a province as owned by the player when the real record said otherwise.

The rest of the record layout is still unmapped.


---

## 6. Nation records 🟡

Roughly `0x373B8`–`0x461EF` in the sample file, spaced ~3900 bytes apart.
Contain the pretender's name (`Jamasp`, `Harald`, `Gangr`) and title strings
(`the Most High, King of Kings, the Evil Prince, King of the Crafts`).
Nations the player has not met read `unknown`.

---

## 7. Score-graph history — empire statistics ✅

Every `ftherlnd` and `.trn` carries the data behind the in-game score graphs
as a flat array of **22-byte records, one per (turn, nation)**. A turn-13
`.trn` of a six-nation game holds 78 records: six nations × turns 0–12.
`.2h` order files carry none.

| Offset | Type | Meaning |
|---|---|---|
| `+0` | u16 | ✅ turn |
| `+2` | u16 | ✅ nation id |
| `+4` | u16 | ✅ provinces held |
| `+6` | u16 | ✅ forts |
| `+8` | u16 | ✅ **income** — gold per turn |
| `+10` | u16 | ✅ **gem income** — gems per turn, all paths summed |
| `+12` | u16 | ❓ `0` in every record seen |
| `+14` | u16 | ✅ **research** — research points per turn |
| `+16` | u16 | ✅ **dominion** — total dominion strength |
| `+18` | u16 | ✅ **army size** — units, mounts and commanders included |
| `+20` | u16 | ❓ `0` in every record seen |

`scores.html` has one column with no home above — Victory Points — and it read
0 for every nation in both sample games, so it is most likely `+12` or `+20`.

### How it was found, and how it is verified

`--scoredump` makes the engine write its own `scores.html` after hosting
(see `ENGINE_TOOLING.md`). That is **labelled ground truth for six nations at
once**, which turns the search into known-plaintext: find offsets whose values
reproduce the whole table. Six simultaneous constraints per metric leave no
room for coincidence.

The first search assumed `offset = base + nation_id * stride` and found
nothing; the array is indexed by **participation slot**, not nation id, and
the record is headed by its own `(turn, nation)` pair.

Verification is a genuine holdout: the layout was derived from a MA T'ien Ch'i
game and then checked against a **different game** (Bandar Log, different
nations, different turn) by hosting a sandboxed copy with `--scoredump`.
**42 of 42 values matched** — six nations × seven metrics. That check is
frozen as `tests/test_scores.py`.

### Locating the array

It has no magic number. `dom6.scores.find_score_history()` identifies it by
shape: records cycle through a fixed nation set in a fixed order, and the turn
counter advances by exactly one each time the cycle wraps. Runs shorter than
three turns are rejected, because a handful of records occurs by chance in the
sparse zero/`0xFF` regions that make up most of a save.

### Two things to know before using it

- **The newest record lags the header turn by one.** The array is appended to
  when the host generates the following turn, so a turn-13 `.trn` ends at
  turn 12.
- **`income`, `gem_income` and `research` are per-turn rates**, not stockpiles.
  The **treasury**, the **gem inventory by path**, and **research levels per
  school** are stored elsewhere and are still unmapped — see the roadmap.

---

## 8. Open questions

- [ ] Treasury (gold on hand), gem stock per path, research level per school.
- [ ] Province record field layout and length.
- [ ] Unit/army records: unit type id, count, squad number, x/y battlefield placement.
- [ ] Commander records: equipment slots, magic paths, battle script (spell order).
- [ ] VCR body after `+0x20`: per-round checksums, unit lists, outcome.
- [ ] Header fields at `0x08`, `0x0A`, `0x12`, `0x16`, `0x1E`, `0x22`.
- [ ] How to reach the engine's per-hit combat logging.
