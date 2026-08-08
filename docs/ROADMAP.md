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

### 1.2 Formation

Same idea, cheaper. Set one squad to **Box**, save the `.2h`; change it to
**Skirmish**, save again. Formation is per-squad and sits near the placement
fields I already read, so one diff should be enough.

### 1.3 Verify extracted stats against the game

I validated unit stats against invariants and the manual, but never against the
game's own UI. If you open a unit info screen for, say, a **Militia**, a
**Longbowman** and an **Armored Sacred Tiger**, and send me the displayed
hp / prot / att / def / mor / enc / MR, I can confirm the extraction end to end
— including whether `total_protection()` matches what Dominions shows.

This is the highest-value check per minute of your time.

### 1.4 A multiplayer turn file

Everything so far comes from a single-player game. An MP `.trn` would let me
verify the assumption that enemy survivors are genuinely invisible — currently
the reason enemy losses are reported as "no longer visible to you" rather than
kills.

### 1.5 A big, messy battle

A fight with magic, summons, afflictions and multiple commanders per side would
stress the parser in ways your turn-9 skirmish does not.

---

## 2. Save format still unmapped

| Item | Notes |
|---|---|
| **Battle scripts** | see 1.1. Not in the 173-byte combat record; `.2h` is the likely home |
| **Formation** | per-squad, near the placement fields |
| Province records | name appears twice per record; field layout unknown |
| Commander records | equipment slots, magic paths, experience |
| VCR body past `+0x20` | per-round checksums, outcome data |
| Header `0x08/0x0A/0x12/0x16/0x1E/0x22` | `0x0A` is a per-game constant that changed 627 → 636 between turns, so not a static id |
| Placement coordinate space | values are usable relatively; absolute meaning unproven |
| Afflictions | almost certainly per-unit; not located |

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
- **Matchup simulator.** The engine has `--simulation`, `--simnat`,
  `--simamount`, `--simbatspells`. Driving it sandboxed would let the advisor
  answer *"what if I had brought 20 more archers?"* empirically instead of
  arguing from stats.
- **Outcome variance.** `--dumpfights` re-rolls each host, so hosting the same
  turn N times samples the distribution — "you were unlucky" becomes measurable.
- **Multi-turn trends.** Army growth, losses over time, income.
- **Pre-battle warnings.** Read the `.2h` before you host and flag being
  out-ranged, length-0 melee, or a single commander leading everything.

---

## 5. Tooling

- Tests. There are none. The extractors have validation functions
  (`validate_monster_stats`) but no test suite; a few golden-file tests over the
  turn-9 save would catch regressions.
- Package properly (`pyproject.toml`) instead of `sys.path` juggling in scripts.
- Handle Dominions patches gracefully: table layouts are re-derived at runtime
  and validated, so a patch should raise rather than return wrong data — but
  that path has never actually been exercised.
