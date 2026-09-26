# Dominions 6 combat mechanics — cheat sheet

The ~20 rules that decide battles, distilled from the manual with page
citations. **Every claim here is checkable** — open `sections/06-combat.md`
(or `manual.txt`) and find the `[p.N]` marker.

This is the always-loaded tier. Load a chapter file only when a question needs
detail this does not cover.

Field names in **`code`** are what `dom6` extracts, so a rule can be applied to
a real save without guessing which number to use.

---

## The die: DRN (p.13)

Every roll is a **DRN** — an *open-ended* 2d6. If a die shows 6, subtract 1,
re-roll it and add; repeat while it keeps showing 6. A lowercase `drn` is the
same thing with a single die.

Consequence: **nothing is impossible.** Militia can hit anything, and a 2%
matchup still happens across 49 shooters and 20 rounds. Never reason as if a
large stat gap is a guarantee.

---

## Melee resolution (p.60)

```
Attack roll     = attacker Attack  + DRN - fatigue penalty
Defense roll    = defender Defense + DRN - fatigue penalty
                  hit if attack roll > defense roll

Damage roll     = attacker Strength + weapon Damage + DRN
Protection roll = defender Protection + DRN  (+ shield Protection on a shield hit)
                  damage dealt = damage roll - protection roll
```

Data: **`attack`**, **`defence`**, **`strength`**, **`total_protection()`**
(natural + body armour; shields are tracked separately).

**Shields (p.60).** A hit is a *shield hit* unless the attack beats defence +
the shield's Parry. On a shield hit the shield's Protection is added.

> Manual's worked example: Heavy Infantry, base defence 10, +1 sword,
> −2 armour, −1 shield = **8**; with Parry 4 its effective defence is **12**.

Note this means the raw `defence` stat is *before* equipment modifiers.

**Armour-defeating hits (p.61).** A protection roll of **2** is always
armour-defeating; **3** is armour-defeating against targets at 50+ fatigue.
Immobilised or unconscious units count as having 100 fatigue.

---

## Repel — long weapons get the first say (p.62–63)

A defender whose weapon is **longer** than the attacker's repels automatically,
*before* the attack resolves.

```
Attacker morale check : morale + DRN - (weapon length difference)
Repeller check        : 10 + DRN + (margin the defender won the repel by) / 2
```

Fail the check and **the attack is aborted entirely**.

- Units with claws and bites (**length 0**) are the easiest thing to repel.
- Low-morale troops are repelled far more often — *"using long weapons against
  low-morale troops is very effective"* (p.63).
- The repeller takes a **lingering −2** to its repel roll that decays, so rapid
  successive attacks are harder to repel than spaced-out ones.
- **Giants (size 6+) wield weapons 1 length longer** than normal (p.63).

Data: weapon **`length`** / **`effective_length`** (natural weapons report
`None`, count as 0), unit **`morale`**, **`size`**.

---

## Hit location (p.61)

`attacker size + weapon length` must equal target size to reach the **head**;
one less for the **torso**, two less for the **arms**.

> *"a human (size 3) wielding a mace (length 1) could hit a size-7 creature
> only in the legs"*

Data: **`size`**, weapon **`length`**.

---

## Fatigue (p.62)

- Each attack adds fatigue equal to the unit's current **`encumbrance`**.
- Every **20** fatigue (rounded down) = **−1 attack**.
- **100** fatigue → unconscious; recovers 5/turn until back under 100.
- **200** fatigue → further fatigue becomes **hit point damage**.
- Wielding multiple weapons adds **+1 encumbrance per weapon after the first**.

So heavy armour is not free: it raises protection and encumbrance together, and
an exhausted unit is both easier to hit and vulnerable to armour-defeating hits.

---

## Morale and rout (p.58)

Battles are **not fought to the death** — they end when one side's nerve breaks.

- Morale is checked **per squad**; a squad checks when it takes enough casualties.
- A squad that fails its check **routs**.
- Troops rout when **all their commanders** are killed or routed — regardless of
  army size.
- The **whole army routs at 75% of total hit points lost**.
- Mindless units never rout (the engine stores **`morale` 50** for them).

> *"The biggest army in the universe will rout if it is led by a single
> commander, and he is killed or routed."*

---

## Deployment (p.58–59)

- **Attacker on the left, defender on the right.**
- A commander leads up to **5 squads**; total troops capped by Leadership.
- A grid square holds **10 size points** — three size-3 humans.
- Formations: **Box**, **Line**, **Double line**, **Sparse line** (−1 morale),
  **Skirmish** (−1 morale). Undisciplined squads are forced into Skirmish.
- Leadership morale (p.59): Ldr 10 → −1 and a further −1 per squad past the
  first; Ldr 50 → no penalty for 1–2 squads; Ldr 100 → +1 for ≤3 squads;
  Ldr 150 → +2 for ≤4; Ldr 200 → +3 for all five.
- Mixing undead, demons, or undisciplined units into a squad: **−1 morale** each.

Data: **`squad_id`** groups combatants. **Placement is not in the save** — the
engine recomputes deployment at battle start, and **`stack_id`** only says
which army a squad marched in with. Never infer where a squad stood.

---

## Missiles (p.58)

Missile hit chance depends on **how many units are in the target square** and
**the target's shield** — not on a defence roll. So packing troops densely is
punished by archery, and shields matter more against arrows than armour does.

Range is fixed per weapon (**`range`**): Sling 30, Short Bow 35, Crossbow 40,
Long Bow 45, Arbalest 50. Javelins and boulders derive range from strength.

**Out-ranging is decisive**: the longer-ranged side shoots for free while
closing. Compare `range` across both sides before anything else in a missile
matchup.

---

## Underwater (p.63)

Slashing and blunt weapons take an attack penalty **equal to their length**;
piercing weapons do not. Flails take an extra −1.

---

## Where to read more

| Question | File |
|---|---|
| Combat detail, repel, fatigue, morale | `sections/06-combat.md` |
| DRN, probability tables | `sections/02-the-basics.md` |
| Unit abilities, afflictions | `sections/04-units.md` |
| Battlefield movement, terrain | `sections/05-movement.md` |
| Spells in battle | `sections/07-magic.md`, `sections/13-battlefield-spells.md` |
| A specific nation | `nations/<slug>.md` |
| Anything else | grep `manual.txt` |
