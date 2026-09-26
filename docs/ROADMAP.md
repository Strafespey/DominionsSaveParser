# Roadmap

What is still unmapped, what would make the advisor better, and the specific
things **you** can capture that would unblock work I cannot do alone.

Status of the current build is in [`FILE_FORMAT.md`](FILE_FORMAT.md) and
[`ENGINE_TOOLING.md`](ENGINE_TOOLING.md). Anything marked ❓ there is fair game.

---

## 1. Things you can help with

These are blocked on data I cannot generate, because they need someone to play
the game. Each is small.

### 1.1 Battle scripts — the biggest single gap ⭐

Reading back what you ordered your commanders to do is the last missing piece of
your original ask (*"you should have scripted the archers to hold twice"*).
I know the full vocabulary — hold and attack, fire and keep distance, cast
spells, target rearmost, and so on — but not where it is stored.

**What to capture:**

1. Pick one commander with a distinctive, memorable script. Something like
   slot 1 = a specific spell, slots 2–3 = **Hold**, target = **rearmost enemies**.
2. End turn. **Before hosting**, copy the `.2h` somewhere safe, named
   `script_A.2h`, and write down exactly what you set.
3. Change **only that one script** — e.g. slots 2–3 to **Fire**. End turn again,
   copy the `.2h` as `script_B.2h`, and note the change.

Two files differing in exactly one known way localises the field immediately.
This is the same technique that pinned the monster type id, and it worked first
try there.

A third capture with a *different commander* scripted would confirm the record
stride.

### 1.2 Stockpiles — treasury, gems by path, research by school ⭐

The score-graph history now gives income, gem *income* and research *rate*
(`FILE_FORMAT.md` §7), but not what you actually have banked. Those three are
what "should I recruit or save?" turns on, and they are almost certainly stored
per nation somewhere near each other.

`--scoredump` cannot label them — it reports rates, not stocks. So this needs
five numbers off your own screen, for a turn whose `.trn` you keep:

1. **Gold** in the treasury (top bar).
2. **Gem counts per path** — the national summary's gem inventory, all nine
   figures including blood slaves, in order.
3. **Research level per school**, all eight, from the research screen.

With those, the same known-plaintext scan that cracked the score record should
land them immediately: nine gem values in a row is an extremely distinctive
signature to search for.

### 1.3 Formation

Same idea, cheaper. Set one squad to **Box**, save the `.2h`; change it to
**Skirmish**, save again. Formation is per-squad and sits near the placement
fields I already read, so one diff should be enough.

### 1.4 Verify extracted stats against the game

I validated unit stats against invariants and the manual, but never against the
game's own UI. If you open a unit info screen for, say, a **Militia**, a
**Longbowman** and an **Armored Sacred Tiger**, and send me the displayed
hp / prot / att / def / mor / enc / MR, I can confirm the extraction end to end
— including whether `total_protection()` matches what Dominions shows.

This is the highest-value check per minute of your time.

### 1.5 A multiplayer turn file

Everything so far comes from a single-player game. An MP `.trn` would let me
verify the assumption that enemy survivors are genuinely invisible — currently
the reason enemy losses are reported as "no longer visible to you" rather than
kills.

### 1.6 A big, messy battle

A fight with magic, summons, afflictions and multiple commanders per side would
stress the parser in ways your turn-9 skirmish does not.

---

## 2. Save format still unmapped

| Item | Notes |
|---|---|
| **Battle scripts** | see 1.1. Not in the 173-byte combat record; `.2h` is the likely home |
| **Formation** | per-squad; location unknown (it is *not* near `+57`, which is a stack id, not placement) |
| Treasury / gem stock / research levels | rates are readable (`FILE_FORMAT.md` §7); stockpiles are not — see 1.2 |
| Province records | name appears twice per record; field layout unknown |
| **Commander records on the map** ⭐ | equipment slots, magic paths, experience — and, blocking loss inference, *where a surviving commander is stored*. See 2.1 |
| VCR body past `+0x20` | per-round checksums, outcome data |
| Header `0x08/0x0A/0x12/0x16/0x1E/0x22` | `0x0A` is a per-game constant that changed 627 → 636 between turns, so not a static id |
| ~~Placement coordinate space~~ | ✅ resolved as *not stored* — `+57` is an army stack id. See `FILE_FORMAT.md` |
| Afflictions | almost certainly per-unit; not located |

### 2.1 Map commander records — why loss inference is broken for commanders ⭐

`battle_outcomes()` decides a unit survived by finding it again in a map unit
array. Commanders on the map are **not** stored as the 173-byte records
`find_unit_arrays` scans for, so surviving commanders read as casualties.

Measured on the turn-28 Nardago battle (`MATC_Awake_Expander`), for the 25
commanders the player engaged:

| Method | Reported alive |
|---|---|
| `find_unit_arrays(min_length=2)` — what ships | 10 / 25 |
| same at `min_length=1` | 17 / 25 |
| targeted `(unit_number, type_id, owner)` triple search | 3 / 25 |
| unit number present *anywhere* outside the replay bodies | **23 / 25** |

The last row is the important one: the data is in the file, in a structure the
scanner does not recognise. Dropping `min_length` to 1 is **not** the fix — it
readmits exactly the noise the guard exists for (46 phantom "Wailing Ladies"
in one file).

Lead worth following: hits cluster around `+0x49000`–`+0x4A000` in that file
and come in pairs **254 bytes** apart, which suggests a ~254-byte commander
record with the unit number appearing at two offsets within it. Unit 6084
(a General) happens to line up with the 173-byte layout at `+164` and 8087
(a White Tiger of the West) does not, so the number is not at a fixed offset
from the record start in both structures.

Until this is mapped, `SideOutcome.lost_commanders` is reported separately and
explicitly as *unconfirmed*, and is excluded from `loss_fraction`. This
mattered in practice: a White Tiger of the West that survived the battle was
reported to the player as killed.

---

## 3. Game data still unextracted

| Item | Notes |
|---|---|
| Weapon damage / attack / defence modifiers | only `length` and `range` are decoded; damage is needed for the damage roll |
| Shield **parry** value | the manual's own example uses it (Parry 4); not located |
| Armour defence penalty | manual example: −2 body, −1 shield |
| Monster field `+42` | 0–100, Horrors max it, elephants read 3; unexplained |
| Armour field `+68` | resource cost vs encumbrance not disambiguated |
| Magic paths, leadership, special abilities | in the monster record; not mapped |
| Spell effects | `--listspells` gives id → name only, no damage/range/fatigue |

Weapon damage and shield parry are the most valuable, because together with
what exists they would allow an actual expected-damage calculation rather than
a qualitative "you were out-ranged".

---

## 4. Analysis features worth building

- **Expected-damage model.** With weapon damage + parry, compute per-round hit
  and kill probability between two unit types. Turns advice from directional to
  quantitative.
- **Per-hit combat narrative.** 🟡 mostly done. Settled long ago that the save
  does not contain one (`FILE_FORMAT.md` §4 size accounting — the tail of a
  replay is ~5% of the floor a log would need), so it has to come from the
  engine re-simulating.

  - ✅ **The log is parsed.** `dom6/combatlog.py` turns `log.txt` into typed
    events — hits with location/weapon/damage roll vs protection roll, the
    hit-area cap, shield hits, repels, individual and army rout checks, casts,
    environmental damage — plus per-unit damage/kills and an attempts-versus-
    landed **hit rate**. The grammar was lifted from the engine's own format
    strings, not from samples, so it covers cases the sample logs lack.
  - ✅ **Capture is automated except for one click.** `dom6/replay.py` launches
    the game already configured (no Steam launch options), points `DOM6_SAVE`
    at a throwaway copy, preserves the pre-existing `log.txt`, watches for the
    replay, and shuts down when the log stops growing.
    `scripts/analyze_battle.py` is the CLI.
  - ⏸️ **Opening the battle is still manual — parked deliberately.** The replay
    only renders in the viewer, so something must click it. A record-and-replay
    input macro is implemented (`record_macro` / `--macro`) but **has never
    been run against a real window**; treat it as a sketch, not a feature.
    Image-based navigation is not an option today — neither Pillow nor OpenCV
    is installed.
  - Remaining lead for a cleaner route: the engine reads and writes standalone
    **`.vcr` files** (`%s/%d_%d.vcr`), and `readvcr: got land %d, own %d,
    frtown %d, pd %d, ass %d` implies they carry province owner and PD *at
    battle time* — which would also fix the after-only outcome read. The UI
    path is `viewvcrs` → `gotomsg` → `playvcr nbr %d`, i.e. battles are indexed
    as turn **messages**; no CLI switch exposes that index.
- **Matchup simulator.** The engine has `--simulation`, `--simnat`,
  `--simamount`, `--simbatspells`. Driving it sandboxed would let the advisor
  answer *"what if I had brought 20 more archers?"* empirically instead of
  arguing from stats.
- **Outcome variance.** `--dumpfights` re-rolls each host, so hosting the same
  turn N times samples the distribution — "you were unlucky" becomes measurable.
- ~~**Multi-turn trends.** Army growth, losses over time, income.~~ ✅ done —
  the score-graph history in every save carries provinces, forts, income,
  gem income, research, dominion and army size for every visible nation on
  every turn. `scripts/empire_report.py`, `FILE_FORMAT.md` §7.
- **Pre-battle warnings.** Read the `.2h` before you host and flag being
  out-ranged, length-0 melee, or a single commander leading everything.

---

## 5. Tooling

- Tests. Two golden-file suites exist over the turn-9 fixture
  (`tests/test_vcr_regression.py`, `tests/test_scores.py`), plus
  `tests/test_combatlog.py` (9 cases) whose sample lines are instantiations of
  the engine's own format strings rather than invented text. The game-data
  extractors still have none — they have validation functions
  (`validate_monster_stats`) but nothing pinning the extracted values.
- Package properly (`pyproject.toml`) instead of `sys.path` juggling in scripts.
- Handle Dominions patches gracefully: table layouts are re-derived at runtime
  and validated, so a patch should raise rather than return wrong data — but
  that path has never actually been exercised.
