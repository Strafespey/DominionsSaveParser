# Combat

*Manual pages 57–72 (1-based).*

[p.57]
52. Kill lone units
Lone units (non-commanders) in enemy provinces are killed.  If
there are units without commanders inside enemy territory
they will be killed here to prevent them from making any
pointless attacks.
53. Reclaim provinces
If a fort does not own the province it is in and it is not under
siege, it will take ownership of the province.  This can happen in
team games where the province and the fort might have
different owners from the same team.  This step is resolved in
favor of the owner of the fort.
54. Conscription
Province Defence is raised to a minimum of one and Dominion
and Commander effects to raise the PD take effect.
55. Scouting
New scouting reports are generated for each player.
56. Elimination
Players without any provinces or dominion are eliminated from
the game.
57. Victory
If a victory condition is fulfilled, the game declares a winner and
ends.
58. Update stats
Hall of Fame and scoregraphs are updated.
59. Heroic abilities
Units gain and improve heroic abilities.
60. Reform Immortals
Immortals that are due to return will reform their bodies here.
61. Reduce PD
Province defense is reduced if the population cannot support
the current level.  At least 10 population is required for each
point of province defense.
62. Yearning artifacts
If any new artifacts become yearning, it will happen now.
63. Aftermath
The game validates orders and items, changes shapes if
necessary, etc.
Combat
Combat is what happens when two discovered enemy forces
occupy the same location on the map.  If one force or both
forces are undiscovered, no combat will occur.  Thus, a
stealthy force may move right through an enemy and not
trigger combat.  Thus, both forces are not discovered.  Two
forces which are both discovered may occupy the same
province, but one might be in a fortress which has not yet
been breached.  In this case, the forces are in different
locations (one in the fort, the other besieging in the
province).  When one army is in a fort and one army
besieges, the province is owned by the besieging player and
the fort is owned by the besieged. This situation is known as
partial ownership of the province. When the same player
owns both fort and province, the situation is known as full
ownership. Full and partial ownership of a province have
certain effects in-game (e.g. some events cannot happen in a
partially owned province because they require full
ownership as a precondition to happening).
Once combat occurs, units move according to their tactical
movement allowance on a grid placed over the map.  You
can toggle this grid by hitting the [g] key or the [w] key.
Players can find battles overwhelming.  This can easily
happen if you try to follow every swing of every weapon.  It's
not necessary.
It is important to understand that battles in Dominions are
not fought to the death.  They are fought until one side loses
its nerve and routs.  As will be explained in the section to
follow, routing is based on losses and morale.  This allows
small units of elite troops to hold off masses of undisciplined
barbarians.
Here are some basic points to understand about combat. 
Details will be discussed later on in this section.
57
From the tomes of the lore of Dominions
Raterik is a strange and secretive knight.  As a youth, he befriended a black unicorn and the magical steed gave the peasant boy the 
opportunity to join the Black Order.  Several of the older members of the Order complained about the peasant, but so far he has not 
failed in his tasks.  Raterik has proven himself a resourceful and able commander. 
 Hildegard was the only child of the late Hochmeister of the Black Order.  Her father taught her how to fight and wanted her to join the 
Order, but she was a strong-willed woman who didn’t like the Order’s strict hierarchical organization.  She decided to become a 
freelance warrior and as such, she has become known and respected.  During her more adventurous years, Hildegard befriended a 
unicorn who still accompanies her.

### Battles View

### Battle sequence

### Army Setup

[p.58]
* Units are deployed on the battlefield corresponding to the
Army Setup screen under Position squads.
* The attacker is on the left, the defender on the right.
* Units move across the battlefield in accordance with the
instructions in <set battle orders>
* When units move adjacent to an enemy, they halt due to a
"zone of control"
* Once units are adjacent, they attack each other every turn.
* The chance of scoring a hit in melee depends on the difference
between attack and defense values
* The chance of scoring a hit with missile weapons depends on
the number of units in square the missile hits, and how good the
target's shield is (if it has one).
* The chance of doing damage after scoring a hit depends on the
attacker's strength and weapon damage versus the defender's
protection.
* Magic in combat works a lot like missile weapons (see page
65)
* Morale is calculated for each squad.  A squad takes a morale
check when it suffers enough casualties.
* A squad routs when it fails a morale check.
* Battles are fought until one side routs off the map:  the other
side is said to have won the battle
* Troops will rout when all of their commanders have been killed
or routed. The entire army will rout when their side loses 75%
of its total hit points
So if you kill or rout all of an army's commanders, the whole
army will rout.  It does not matter how big it is.  The biggest
army in the universe (of Dominions) will rout if it is led by a
single commander, and he is killed or routed.
(For this reason, there is no "attack commanders" order. 
You will have to figure out how best to do this yourself!)
Battles View
When you get a report on a battle, you can click on the
message “There was a battle in <province name>”. This gives
you the battle summary with the casualty lists. Clicking the
“View battle” text will take you into the battle replay.
The battles in Dominions are actually very detailed tactical
resolutions fought at the level of the individual fighters,
mages, and priests.  Each unit has its own equipment and
abilities.  They move and fight according to these
parameters, according to the battle sequence.  When you
watch the battle replay, you can see what happened with
various degrees of detail.  There is a box in the upper left
which describes the action.  You can change the level of
detail in this box by hitting the number keys: [1] for least
detail, [2-3] for more detail, and [4] for most detail.
Other useful keys when viewing battles are:
Arrow for scrolling around the map
PageUp / for adjusting the camera height
PageDown
Space for pausing the action
c for toggling colored squares for the teams
g for toggling grid
w for toggling the wire frame grid (battlefield
graphics disappear from view)
q to quit out of the battle replay
f speed up battle replay to fast speed
t speed up battle replay to fastest speed
s switch battle replay back to normal speed
v while viewing a unit, this key will show its
combat log
z slow motion replay (useful when using greatest
amount of detail to see what happens and
when)
F1 Obtain a list of all the units
F2 View current weather and dominion scales
? View the available hotkeys
1 / 2 / 3 / 4 adjusts the level of detail in the battle log
(upper left text box describing the battle action)
+ - scroll the battle log
Battle sequence
When combat is started, the attacker is placed on the left
side of the screen and the defender on the right.  All units
are placed on the battlefield according to their setup.  They
will then proceed to follow whatever orders they have been
given (attack, cast spells) until they rout or the battle ends.
Army Setup
Units in Dominions 6 are placed into squads, which are
under the leadership of a commander.  A single commander
can lead up to five squads.
The total number of units a commander can lead is
designated by the Leadership rating found in the unit
abilities.  Clicking on this rating gives further details of the
commander's leadership limits, such as how many magical
beings or undead may be led.  This is important, as not all
commanders have the skill to give orders to magic monsters.
58

#### Formations

[p.59]
And undead and demons don't take orders from just
anybody either.
Squad limits related to leadership values
* Leadership 10: automatic -1 to morale for a single squad. An
additional -1 to all squads for every squad beyond the first (so
five squads = -1 base penalty and -4 for four extra squads = -5).
* Leadership 50: No morale penalty if leading one or two squads.
-1 penalty for every additional sq.
* Leadership 100: +1 morale for all squads if three or fewer. -1
penalty to morale for every squad above three.
* Leadership 150: +2 morale for up to 4 squads, -1 penalty to all
if fifth squad added.
* Leadership 200: +3 morale for all five squads.
The morale effects of leadership rating are based on the
base leadership rating of the commander.  Commanders
gain more leadership with experience, so a highly
experienced commander with a base leadership of 50 might
be able to lead up to 175 units or more, but the morale
bonuses still stay the same.
Experience level Leadership bonus Poor leaders (ldr 10)
1 +25 +5
2 +50 +10
3 +50 +10
4 +50 +10
5 +50 +10
Other effects on morale:
* Mixing undisciplined units with normal makes entire squad
undisciplined and hits them with -1 morale
* Mixing undead with living gets a morale penalty of -1
* Mixing demons with normal units gets a morale penalty of -1
Each unit is placed on the map in a grid square.  A single grid
square can hold a total of ten size points of units.  For
human-sized units (size 3), this means three units can fit in a
grid square.
Unassigned units (those in the garrison box at the top of the
Army Setup screen) are formed into one large squad.  They
begin at the center of their side's army.
Formations
Formations are the patterns used to deploy units of a squad
onto the map.  There are five types of formations, some of
which can only be used by good leaders.
Box
A box formation deploys your units in as close to a square as
possible.  For example, a squad of 36 Infantry of Ulm (size 3)
deployed in a box formation would be placed with four squares
frontage and three squares deep, yielding 12 squares of three
units each.
Line
A line formation deploys your units in a straight line facing the
enemy.  This formation is only available to good commanders.
Double line
A double line is the same as a line except half the units are
placed in a rank immediately behind the first line.  This
formation is only available to good commanders.
Sparse line
A sparse line formation is identical to a line, except that an
empty square is inserted between each square of units.  This
doubles the length of the line.  It carries a -1 penalty to the
squad's morale.  This formation is only available to good
commanders.
Skirmish
Skirmish formation forms a box-like checkerboard formation
which separates each square of units from its neighbors with an
empty square in four directions, as above.  It has a -1 penalty to
morale.
Undisciplined squads automatically use the skirmish
formation and cannot use any other.  Adding an
undisciplined unit to a squad makes the whole squad
undisciplined.
The ability Tight Rein negates the undisciplined trait of a
commander's units, enabling other formations as well as
giving specific orders to undisciplined units.
The Skirmisher ability negates the -1 morale penalty when
59
From the tomes of the lore of Dominions
Bandar Log is a very hierarchical society.  Markatas are the smallest of the monkey people and their intellect is barely above that of 
simple beasts.  Markatas are small, noisy, and annoying, especially when met in large numbers.  If alone, they can be used as scouts, but 
when in greater numbers, they quickly become bored and start to make noise and play with each other.  They are generally despised by 
the larger monkeys and apes.  They are sometimes given small bows.  This pleases them no end, but they still are not very useful soldiers.

### Melee combat

#### Battlefield movement

[p.60]
the unit is deployed in a skirmish or sparse line formation.
The ability Formation Fighter allows you to fit more units in
a square.
Battlefield movement
Each unit in combat has combat speed.  A move of one
square on the battlefield costs roughly one point of combat
speed, unless it is diagonal in which case it costs 50% more.
When units move adjacent to an enemy, they become locked
in a “zone of control” which remains as long as the enemy
persists. However, fleeing units do not care about zone of
controls and just run regardless of danger and nearby
enemies.
Usually there can only be 10 size points in a single square
and a unit is unable to enter a square if that results in the
square being too full. However, giants or other monsters
that are considerably larger than the other units will be able
to enter the square by displacing the smaller units. The large
unit must be at least 3 size points larger than any displaced
unit and it will cost one extra point of combat speed.
Note that trampling units will never try to displace anyone
as long as they are not routing, as that would cause damage
to the friendly units.
Each unit moves individually, and has a cooldown at the end
of each action.  After a unit moves one step or strikes, it
must cool down a while before it can perform its next action.
A long cooldown is one round (after a strike) and a short
cooldown comes after a move.  There is some small amount
of randomness to this cooldown value, but when moving it is
mostly determined by the unit’s combat move, so faster
units will wait a shorter time before taking the next action. 
If two units are adjacent, the unit that finishes its cooldown
first will get to strike next.
Melee combat
Melee combat is the act of one combatant (soldier, priest,
monster, or divine being) physically striking another
combatant in some way.  At its heart, it is very simple.
The attacker makes an attack roll.  The defender makes a
defense roll.  These are compared.  If the attack roll (with
modifiers) is greater than the defense roll, it hits.  If not, it
misses.
The attack and defense rolls are modified by a random
number (which is added) and a fatigue penalty (which is
subtracted).
Attack roll: attacker's Attack attribute + DRN - Fatigue penalty
Defense roll: defender's Defense value + DRN - Fatigue penalty
Once a hit is scored, a similar calculation is done to
determine how much damage is done.  This involves the
attacker's damage roll minus the defender's protection roll.
Damage roll: attacker's Strength attribute + weapon Damage
attribute + DRN
Protection defender's Protection attribute + DRN (+ shield
roll: Protection if it is a "shield hit")
If the defender has a shield, the hit is a shield hit unless the
attack beats the combined value of the target's defense and
the shield's Parry value plus the random roll.  If a hit is
scored as a shield hit, the shield's Protection is added to the
defender's protection roll.
Example:  A Heavy Infantry unit has a broad sword, chain
mail hauberk, half helmet and shield.  It has a base defense of
10, gets a defense bonus of +1 from the sword, a defense
penalty of -2 from the armor, and a defense penalty from the
shield of -1.  The shield's Parry value is 4.  The actual defense
is 10 +1 -2 -1 = 8.  With the shield's Parry value, the unit's
total defense is 12.
The Heavy Infantry is attacked by a Vanjarl of Vanheim,
which has attack 14.  Neither unit has any fatigue yet.  The
Vanjarl rolls a 6, for a total attack value of 20.  If the Heavy
Infantry rolls a 7 or less, it is a clean hit and the shield offers
no protection.  If the Heavy Infantry rolls an 8 through 11,
the Vanjarl scores a shield hit and the Heavy Infantry can
use its shield's protection value in the damage calculation.  If
the Heavy Infantry rolls a 12 or higher, the Vanjarl misses
entirely.
The Protection value used is the target's listed Protection
value, unless it is a head hit.  In case of a headshot, the
target's helmet Protection value is used instead of the main
Protection value.  However, if it is a shield hit, the shield
Protection is still added.  The blow is assumed to have
glanced off the shield and hit the target in the head.
If the damage roll is greater than the protection roll, the
difference is subtracted from the target's hit points.  If the
protection roll is equal to or greater than the damage roll,
60

#### Armor defeating hits

#### Shield destruction

#### Hit locations

#### Weapon types

[p.61]
there is no effect.
Armor defeating hits
A low protection roll may result in an armor defeating hit
that bypasses 25% of the protection. This in addition to the
protection roll being very low is likely to result in a serious
wound.
Fatigue plays a large role in enabling armor defeating hits
and units that are immobilized or unconscious counts as
having 100 fatigue for this purpose.
* Protection roll of 2 always results in an armor defeating hit
* Protection roll of 3 results in an armor defeating hit against
targets with 50 or more fatigue
* Protection roll of 4 results in an armor defeating hit against
targets with 100 or more fatigue
Note that it is very hard to score an armor defeating hit on
an unfatigued and not immobilized unit.
Shield destruction
Shield hits can damage or destroy the shield.  A shield has a
Resistance, which is the same as its shield protection value,
+5 if the shield is a magic one.  The attack has a Break value,
which is equal to the damage of the attack before any
Protection.  Slashing attacks add 50% to damage when
calculating break value, and blunt attacks add 25%.
If the Break value is >= 3x the Shield Resistance, the shield is
damaged. If the Break value is >= 5x the Shield Resistance,
the shield is broken.
An already-damaged shield which is damaged again has a
25% chance of being broken.
A damaged shield has -20% Protection, a broken shield has
-50% Protection.
A magic shield (a real, equipable one) that is damaged will
repair itself after the battle.  If a magic shield is broken, it
will be permanently destroyed and the commander will
revert to his or her standard shield if he or she had one. 
Damaged or broken mundane shields will be repaired when
they are in a province with enough spare production
resources.
Hit locations
Dominions 6 uses anatomical locations to determine where
an adversary was struck.  An attack has a 50% chance of
striking the adversary in the torso, 20% chance to strike the
arms, 20% chance to strike the legs, and 10% chance to
strike the head.  Certain hits can cause afflictions, such as
losing a limb.  If someone loses a limb, it will be the one
which was hit.  This can be an arm, leg, or head.  Losing your
head is usually instant death, but this is not always true, for
example in the case of undead and certain kinds of
regenerating monsters, or those with multiple heads.  Other
types of afflictions include losing an eye, which can only
happen on a head hit.
In order to score a hit on a certain part of the body, however,
the attacker must be able to reach it.  To score a head hit,
attacker size + weapon length must be equal to target size. 
This requirement is one less to hit the torso and two less to
hit the arms.  Thus a human (size 3) wielding a mace (length
1) could hit a size-7 creature only in the legs!
Some monsters have their heads located lower than their
size would indicate and therefore anyone attacking them
will get a bonus to their reach. Lizards and dragons are very
low and are two steps easier to hit when striking anything
higher than the legs. Most four-footed beings like elephants
and wolves are slightly lower than a humanoid would be and
are one step easier to reach. Their lower stature does not
mean they are more likely to be hit in the head (or any other
hard-to-reach location). It is still only a 10% chance, but
attackers with shorter weapons might be able to reach and
hit them in the head in situations where their size might
otherwise prevent it.
Also, some monsters lack certain hit locations.  For example,
a dragon has no arms and a gelatinous cube has no arms,
legs, or head.
A significantly larger unit that attacks a smaller one will
have an increased chance of hitting its target in the head and
a lower chance of hitting it in the leg (20% head, 10% leg). 
To be considered “significantly larger” it must be 2 sizes
larger (if mounted the mount's size is used).
Weapon types
Melee weapons in Dominions 6 come in three different
types:  slashing, piercing, and blunt.  Each type has different
effects when calculating damage.  These are all calculated
after the Damage vs. Protection calculation above, except
for Piercing weapons which reduce Protection prior to the
calculation.
61

#### Harassed

#### Fatigue

#### Repel

##### Unconsciousness

[p.62]
Blunt weapons do 25% more damage when scoring head hits
before the Protection value is deducted.  They score 25%
more damage toward shield destruction.
Slashing weapons do 25% more damage after Protection is
deducted.  They do 50% more damage toward shield
destruction.  If a slashing weapon scores a leg, arm, or head
hit that costs a target greater than or equal to 50% of its hit
points, that body part will be chopped off.  If a head is
chopped off, this will kill the target if it had a head that was
required for it to stay alive. (For example, a hydra does not
fit that description.)
Piercing weapons reduce Protection by 15% prior to any
calculation.  This is the same mechanic as the Armor-
Piercing ability, except that Armor-Piercing reduces
Protection by 50%.  The Armor-Piercing ability stacks with
the piercing weapon type for a total of 65% reduction in
armor.
Two-handed weapons add 125% of Strength to damage.
Underwater effects
Slashing and blunt weapons have an attack penalty equal to
weapon length underwater, while piercing weapons do not.  If a
weapon does both piercing damage as well as another type, the
underwater penalty is halved.  Flails have an additional penalty
of -1.
A weapon may be able to inflict more than one type of
damage.  If so, it has an equal chance of doing each type of
damage, but will only do one of them during that attack.  For
example, the short sword does both slashing and piercing
damage.  It has a 50% chance of doing one of these.  If it does
not do piercing, it will do slashing, but never both.
Note that these weapon types apply to all sorts of weapons,
not just maces, swords, and spears.  A spider's venomous
fangs can do piercing damage, for example.
In addition, weapons may have additional special effects,
such as doing additional fire damage when it hits someone.
Damage is displayed in colored numbers above the unit that
suffered the damage. Pale red is normal damage, dark red is
bleeding, green is poison, etc. This can be very helpful in
determining the effectiveness of your units and tactics.
Harassed
Every time a unit is attacked, it gets a point of harassment
penalty.  Each point of harassment penalty reduces the
unit’s defense by 1.  It is then reduced continuously by a
percentage, so it goes down quickly if it is high and the unit is
no longer being attacked.
For cavalry units only the unit attacked (the rider or the
horse) will be affected. I.e. an attack against the rider will not
give any harassment penalty to the horse.
A weapon with multiple attacks inflicts 1 point of
harassment penalty for each one of its multiple attacks.
Only directed melee attacks will result in harassment
penalty, ranged and AoE attacks do not incur any penalty.
Fatigue
Fatigue is affected by a unit’s encumbrance value.  The more
encumbered it is, the more fatigued it will become during
combat.  Each time it attacks, it gains Fatigue equal to its
current Encumbrance value.  Fatigue affects units as follows.
Defense penalty for fatigue
For each 10 points of fatigue (rounded down) a unit has its
defense reduced by 1.
Attack penalty for fatigue
For each 20 points of fatigue (rounded down) a unit has its
attack reduced by 1.
Unconsciousness
A unit falls unconscious when it reaches 100 fatigue.  Each
turn it is unconscious it regains 5 fatigue until it become
conscious again (i.e. fatigue drops below 100).  A unit with
200 fatigue starts to take hit point damage from exhaustion
instead of fatigue when additional fatigue damage is taken.
Repel
Repel is how Dominions represents the effectiveness of long
weapons, such as halberds, pikes, and the like.  If a unit
attacks an enemy who has a longer weapon than the
attacker, the defender may actually repel the attack and
prevent it from happening.  This occurs as follows:
Any defender that has a longer weapon than the one used by
its attacker makes a repel attack automatically upon being
attacked.  Attack and defense rolls are made.  If the result is
a hit, the attacker must pass a repel morale check or
immediately abort his attack.  If the attacker passes the
repel morale check, he may make his attack, but the
62

#### Multiple attacks

#### Melee attack resolution

##### Multiple weapons

[p.63]
defender’s attack then generates damage and protection
rolls.  If damage is inflicted, the attacker takes one point of
damage and continues his attack.
Repel morale check
Attacker morale check: morale + DRN - (weapon length
difference)
Repeller check: 10 + DRN + (the number by which the defender
won the repel attack) / 2
This simulates the defender successfully placing his longer
weapon between himself and the attacker.  All of this occurs
before the attacker’s strike is resolved.  Note that units with
low morale are more likely to be repelled, and thus using
long weapons against low-morale troops is very effective. 
Also, units with claws and bites (weapon length zero) are
easier to repel.
The repelling unit gets a lingering -2 to its Repel roll which is
gradually removed over a short period of time.  So it’s harder
to repel attacks when they come in quick succession, and
easier if they are spaced out in time.
Giant sized units (size 6+) wield longer weapons than normal
humans. The length of their weapons are 1 point longer than
ordinary human weapons. So a giant wielding a mace (length
2 for giants) would be able to repel humans with ordinary
maces.
Multiple attacks
Some units have multiple attacks.  This may be due to
multiple weapons, or just multiple methods of attack like
biting, clawing, or many tentacles.
Multiple attacks can target different units as long as there
are many in reach. Some rare weapons (e.g. flail) have more
than one attack, these attacks always target the same unit
and if he dies on the first attack the second one is wasted.
Multiple weapons
Attackers with multiple weapons have their attack skill
reduced by the sum of their weapon lengths.  Thus, it is much
easier to fight with two daggers than with two swords.  The
Ambidextrous ability reduces this penalty by the amount of
the Ambidextrous skill.  Some weapons are considered
intrinsic to a unit and do not cause multiple weapon
penalties for the attacker. These are called bonus weapons.
For example, some lizardmen of C'tis might have both a
trident and a bite attack. This bite is considered a bonus
weapon because it is not a wielded weapon and it will not
result in any multiple weapon penalty.
Units with multiple wielded weapons also get one point of
extra encumbrance for each weapon after the first.
Melee attack resolution
There are many special abilities that can affect units that are
fighting in melee and the order in which they take effect can
be important. Here is a list of when most abilities take effect
when doing a melee attack.
Determine target
Determine which unit in the square will be the target. This will
be a single unit or mount.
Early strikeback effects
This is certain longer range defensive abilities of the defender,
e.g. Awe and the Gorgon's petrifying gaze. If the attacker ends
up immobilized for any reason the attack is aborted now.
Repel
Check for repel and abort the attack if it is repelled.
Strikeback effect
This is effects like Slimer, Sight Vengeance, Horror Mark
Attacker and many others. If the attacker ends up immobilized
for any reason the attack is aborted now.
Attack and Defence rolls
The attacker rolls his attack value and the defender his defence
value. If the attack missed completely it is aborted.
Damage and Protection rolls
Rolls for damage and protection are rolled now. Protection
from shields will be added if the previous step indicated a shield
hit.
Defensive abilities
Here abilities like Mirror Image, Protective Force, Luck,
Mossbody and many more take effect and may reduce damage
or negate the attack completely.
Limb cap
If the attack hit an arm or a leg (or a head in the case of a certain
beings that can live without those), the damage will be limited
to at most half of the maximum HP.
Damage Redistribution
If the defender has Damage Reversal, Blood Bond or Blood
Vengeance it will take effect now and maybe shift the damage
to other targets or maybe even kill the attacker. Killing the
attacker in this stage will not negate the attack.
63

### Mounted Units

#### Dancing Weapons

#### Hitting mounted units

#### Mounted units and magic items

#### Rider skill

#### Mounted units and morale

[p.64]
Deal damage
Deal damage to the target as well as any shields that might
have been hit.
Dancing Weapons
Some magic items like the Dancing Trident or the Stone
Birds will float around their wielder and attack nearby
enemies.  These weapons attack independently of their
owner and do not incur any multiple weapon penalty or
fatigue.  They will cause harass penalty to whomever they
attack, just as normal attacks do.  These weapons strike at
different times in the combat round and when or if their
owner is attacking does not matter.
Dancing weapons cannot be repelled, but they can repel
attacks aimed at their owner if they are longer than the
attacking weapon.  Dancing Weapons with more than 2
attacks per round get one point of repel attack bonus per
number of attacks over 2.  Dancing weapons also get an
increased repel penalty if they try to repel repeatedly in a
short time, but the penalty is only half of that for a normal
repelling unit.
Mounted Units
Some combat units like cavalry and chariots are formed
from two or more separate units combined as a single entity.
These are referred to as mounted units.
The individual parts of a rider and its mount can be targeted
and wounded separately and if one dies the other will
remain on the battlefield. A horse without rider will rout
from the battle, but some monsters like the gryphon will
stay and fight even if its rider perishes.
Hitting mounted units
When a mounted unit is attacked either the rider or the
mount is targeted. The chances of hitting the rider vs the
mount is based on the difference of their sizes and the reach
of the attacking unit. If a mount has multiple riders, the size
of the largest rider will be used. The reach of a unit is its size
plus the length of its weapon.
First of all, mounts that are much larger than its rider have
an extra chance of getting hit according to the following
table.
Size difference Chance of targeting mount
3 25
4 50
5+ 75
If the mount wasn't large enough or the attack didn't target
the mount, the attack will choose a target according to the
following rules instead.
* Missile attacks have 50% chance of targeting the mount
* If the mount's size is 2 larger than the reach, the mount will be
targeted
* Otherwise chance of targeting mount is 30% + 10% * mount's
size - 10% * reach. (Chance cannot be lower than 10%).
Some attacks work a bit differently and target one specific
unit or both units.
* All AoE attacks will target both rider and mount.
* Lightning will target both rider and mount.
* Trample will always target the mount.
Mounted units and magic items
It is possible to put a single magic saddle or barding on a
commander's mount.  If the mount should be a commander
for some reason it can have its own misc items too, but that
is rare and usually only a single magic saddle or barding is
allowed.  However, it is possible for the mount to take
advantage of some of the rider's magic items as well as
certain items will bestow some or all of their effects to the
mount as well.  This is indicated in the magic item
information if that is the case.
It is very cumbersome to use two-handed weapons while
mounted and doing so will result in a -3 attack penalty.
Rider skill
Some riders are exceptionally skilled and have the Skilled
Rider ability.  This ability will increase the Morale and
Defence Skill of the mount.  The defence increase is most
effective on lightly armored horses as it is reduced by the
encumbrance value of the mount's armor.
Mounted units and morale
Unnatural fear effects (e.g. Fear auras or Terror spells) will
usually target both the rider and the mount.  If the rider is
routed he will leave the battle together with his mount.  If
only the mount is broken, the rider is thrown to the ground
and the mount routs from battle, but the rider fights on.  If
64

### Missile combat

#### Rerecruiting mounted units

[p.65]
both are broken by a fear effect, the rider will be thrown off
and then both will retreat separately.
Falling off a mount deals a size difference open ended roll of
AN damage. Falling off a chariot does not result in any fall
damage however.
Normal rout checks that affect the entire squad or army will
only affect the rider.  When the rider flees this way he will
flee together with his mount.
Rerecruiting mounted units
When a rider loses his mount he will need to get a new one. 
If there are riderless mounts of the appropriate type that
survived or fled the battle, the rider will claim one of these
and remain in the army.  If on the other hand there are no
surviving mounts to claim the rider will leave the army and
return to his home province.  This might take a few turns if
the rider is far from home.  The traveling rider will not be
affected by province ownership, but he will need to roll
morale checks every turn.  A failed check means the rider
has deserted, lost his way or been killed.  If the rider arrives
in his home province a new mounted unit can be recruited at
half cost.  A small blue number next to the unit icon in the
recruitment screen indicates how many available returned
riders are present.  When rerecruited this new unit retains
his identity including experience and battle afflictions.
Normal mounts do not return to their home province, but
mounts with the tag 'Smart Mount' will.  Just like returning
riders they will add to the number of available half-cost
recruits that are available.  Smart mounts, like riders, retain
their experience and afflictions.
Mounted commanders do not return to their home province
if left without mount.  If there are regular units with the
appropriate mount they will just claim one of these and
force the rider of that mount to return home instead.  If
there are no appropriate mounts the commander will
remain in the army without mount.  However he can spend a
month and use the order 'Reclaim Mount' to get a new
mount.
A few types of riders will automatically regain their mounts.
Missile combat
Missile combat is different from melee combat in that it
doesn’t use defense values.  Instead, the game determines
which square a missile hits, depending on a unit’s Precision,
and the range of the attack.  If there are units in the square,
they may be hit, whether they are friendly or enemy. 
Missiles can’t distinguish friend from foe.
If the range from attacker to target is greater than
Precision/2 – 2 (half the Precision, minus 2) then the missile
will deviate from the target.  The amount of deviation is
equal to the range x 1.25 / Precision.
The game will randomly determine whether the missiles
deviate long or short, left or right, or some combination.  The
actual distribution is a bell curve – most projectiles will fall
within the middle of the deviation range, but some will land
at the extremes.
Once the game decides where a missile lands (even if it is far
away, that square is affected), any unit in that square may be
targeted.  The size of the units relative to one another
influences who will be hit.  If a square with a giant of size 6
and a human of size 3 is hit, the giant will be struck two times
out of three. Once the target has been decided, there is a hit
calculation that uses the following values:
Attacker: DRN + (Size points in the square)/2 +2 if magic
weapon
Defender: DRN + (shield parry value x2) – (Fatigue / 20)
If the attacker’s roll is greater than the defender’s then a hit
is achieved.  Damage is calculated identically to melee
combat (see above).  Most missile weapons add one-half of
the unit’s Strength to the weapon damage value (plus a
random number).  Crossbows and some other weapons are
armor-piercing, meaning that only half of the defender’s
Protection value is used.  Some spells can even be
“armor-negating,” which means that armor affords no
protection.  Lightning spells are armor-negating.  Fire spells
are armor-piercing.
Precision values greater than 10 count double for the
amount above 10.  Thus, a Precision value of 12 is actually
calculated as Precision 14.
Thus, the more units in a square, or the bigger the units in a
square, and the more tired they are, the more likely
someone is going to be hit by a missile weapon landing in
that square.
While it may seem that missile units can’t shoot very far
without having their shots deviate hopelessly, in practice
massed units can deal severe damage to an enemy simply
65

### Special damage

#### Fire damage

#### Cold damage

#### Profuse bleeding

#### Poison damage

[p.66]
due to the number of projectiles in the air.  Everything that
goes up has to come down somewhere!
Special damage
Some types of damage can cause the target to sustain
additional damage.  Others inflict their damage gradually, or
increase fatigue instead of reducing hit points.  These
include fire, cold, poison, fatigue, paralysis, and drain.
Some units are not as susceptible to certain kinds of
damage.  In Dominions, this is represented by the concept of
resistances.  This works similar to protection, but damage is
also reduced by a percentage after the resistance is
deducted from the damage.  The reduction is equal to twice
the resistance value.  This means that a unit with fire
resistance 50 is completely immune to fire damage.
Example:  A Pillar of Fire spell with 35 fire damage hits an
unarmored unit with 15 fire resistance and an armor with
protection 10. The damage DRN is 11 resulting in a total of
46 fire damage.  Pillar of Fire is armor-piercing, so the armor
only gives protection 5, but the fire resistance gives its full
value of 15.  The protection DRN is only 6 and results in a
total protection value of 26.  The difference is 20 points of
damage, which is reduced by 30% (twice the fire resistance
value).  In the end the target suffers 14 points of damage.
Elemental resistances give double protection against
attacks that cause fatigue damage.  So Shock Resistance 5
would reduce fatigue effects from thunder by 10.  Shock
Resistance 15 would thus give protection of 30 from the
fatigue damage of a Thunder Strike.
Fire damage
Fire is generally armor-piercing, which means that a unit
only gains half its normal benefit from Protection. In
addition, a unit may catch fire, which will subject it to
additional burning damage until the fire goes out.  Fire
fatigue damage only counts as 1/3 when determining the
chance of catching fire.
Chance of catching fire
Fire damage before protection x 4%
A unit that is burning takes (1d(size))/2 damage each turn
until the fire goes out.  In other words a die with a number of
sides equal to the size of the unit and with the result divided
by 2 (rounded up).  So for a size 8 unit it would be (1d8)/2). 
This damage is halved for units with 5 or more points of Fire
Resistance.  The chance of the fire going out is:
Chance of putting out fire
25% + (fire resistance) + (cold scale x5) + (100% if raining)
All fire have a minimum 1% chance of being extinguished. 
Fire vulnerability counts as negative fire resistance.  Units
with 10 or more fire resistance, units with chill auras, units
with mistform and ethereal units, cannot burn.
If the province has heat scales instead, this is treated as
negative cold.
Cold damage
A unit suffering cold damage may freeze.  It will then take
additional fatigue damage until it thaws.
A unit that is freezing takes 2d6 additional fatigue points of
fatigue damage each turn until it thaws.  The chance of
thawing is:
Chance of thawing
25% + (cold resistance) + (heat scale x5)
There is always a minimum of 1% chance of thawing each
round.  Cold vulnerability counts as negative cold resistance.
Units with 10 or more cold resistance, units with heat auras,
and ethereal units will never freeze.
Cold scales work like heat scales for burning: if it’s cold in
the province, the chance of thawing is reduced by the scales.
Profuse bleeding
A unit suffering from profuse bleeding suffers 10 fatigue and
takes HP/20 damage each round.  The chance of the
bleeding stopping in a round is:
Chance to stop bleeding
10% + (regeneration value)
The chance to stop bleeding is halved when fighting
underwater.
Poison damage
Poison works differently than fire or cold.  If a unit takes
poison damage, that damage will be suffered over multiple
rounds, which is the amount of time it takes the poison to
have its effect.  This damage is spread out as evenly as
66

#### Shock damage

#### Acid damage

#### Rust

#### Life Drain damage

#### Paralysis damage

[p.67]
possible.  First, a total amount of damage taken is calculated,
just like with any attack.  Then, each combat round, a unit
will take 10% of the remaining damage.
In addition to taking damage a unit that is under the effect of
poison will also have reduced attack and defence skill. The
skill penalty depends on how much poison is still remaining
in the unit.  The penalty is 25% for every dose equal to the
unit's full amount of HP, capped at a maximum of 50%.
So if a unit with 10 HP (when uninjured) takes 15 points of
poison damage, it will take 2,2,2,1,1,1,1,1,1,1 points of
damage (each number is in one round).  In the first three
rounds it will take 2 points per round, and in the last seven
rounds it will take 1 point per round.  In addition to taking
damage the units attack and defence will be reduced by
37.5% as soon as it gets poisoned, this penalty will then
decrease by time as the remaining amount of poison is
reduced.
Poison resistance has no effect on the duration of damage. 
Once the poison has taken hold, there is no additional
benefit to poison resistance.  It is useful only in reducing the
total amount of damage initially.
Shock damage
Shock damage can Stun a target. The chance of getting
stunned is:
Chance of getting stunned
5% + (percentage of hit points lost from this hit) / 2
Stun prevents the affected unit from taking any action for
one round.
Acid damage
Acid damage can inflict Rust.
Chance of equipment rusting
Acid damage before protection x 4%
Only units with iron weapons or iron armor can be affected
by Rust.
Rust
Rusty armor can be damaged if it takes a hit in combat.
Chance for Rusty armor to be damaged = damage inflicted
(before armor protection, but after shield protection) * 2%
Rusty weapons have a 25% chance of being damaged when
they inflict a hit on something.  Damaged weapons have
their damage reduced by 2, except for blunt weapons which
have their damage reduced by 1.
Life Drain damage
Life Drain damage is not extra damage, but instead is a way
for the attacker to restore his or her hit points and fatigue
by damaging an enemy.  Once damage has been calculated
(if the target is a living unit), the attacker with life drain
receives the following:
Benefits from life drain
Increases hit points with damage / 2
Reduces fatigue by damage x 2
Weapons with partial life drain are less potent, and only the
first 5 points of damage dealt are treated as drain.  The
remainder are considered normal damage only.
Life Drain cannot increase a unit’s hit points above 150% of
its maximum hit points +10.
Lifeless units only take 25% damage (after Protection) and
the damage will not heal the attacker in any way.  Lifeless
units with a life drain attack or weapon will receive the full
benefit from it.
Paralysis damage
Paralysis is a type of damage based in part on the victim’s
size.  It, as you might have guessed, paralyzes the target. 
The number of combat rounds the paralysis lasts (the
duration) is determined by the number of paralysis points
done.
Duration = (Damage – victim's Size) / 2
If that is all the paralysis damage taken, then the target is
only paralyzed for that many rounds.  However, if the target
takes additional paralysis damage, a new duration is
calculated, and the target takes half as many points of
damage as the lesser of the new or old duration.  In other
words
If already paralyzed, Damage = (minimum of old and new
duration) / 2
This damage can never exceed 5 points.
The new duration will be the greater of old and new
67

### Clouds

#### Fatigue damage

#### False damage

[p.68]
duration (not cumulative), so if the new attack has a longer
duration, the target will be paralyzed longer.
Fatigue damage
Fatigue damage adds to a unit’s fatigue rather than
subtracting from its hit points.  Units fall unconscious when
they reach 100 fatigue.  No unit can have more than 200
fatigue – each 50 fatigue points inflicted once a unit has
reached 200 inflicts 1 point of hit point damage.  If fewer
than 50 fatigue points are inflicted, the chance of taking 1
hit point of damage is (the number of fatigue points inflicted
x 2)%.
False damage
Illusions as well as most spells from the path of Glamour will
only cause false damage.  The false damage is kept real in the
mind of the victims with the help of glamour magic.  If all
enemy glamour mages die, the false damage will quickly
dissipate (2 points / round) without leaving any scars on the
victims.
The false damage feels real enough that someone taking
damage + false damage equaling his total HP will die
instantly.  False damage will never cause any afflictions,
apart from death.
False damage is shown as light purple numbers and dots in
the battle.
False damage will not trigger certain effects like Damage
Reversal, Blood Vengeance and Blood Bond.  Also
regeneration, life drain and healing spells will not heal false
damage.
Clouds
Certain beings, spells and attacks create battlefield clouds. 
E.g. a Hydra is surrounded by a poison cloud, a Fireball will
leave a lingering heat cloud where it strikes and an attack
with the magic Ice Mist Scimitar will create a large frost
cloud when it is swinged.
Battlefield clouds will dissipate quite fast if not replenished,
having their strength reduced by about 1 level per battle
round until it disappears.  Multiple clouds of the same type
cannot overlap, if there are many units spreading the same
type of cloud they will simply spread the cloud further away
instead.  However clouds can sometimes increase the level
of a cloud square by at most one level instead of spreading
further away.
Damage from clouds is always armor negating.  The
different type of clouds and their effects are listed in the
following tables:
Frost Cloud
Level 1 2 fatigue
Level 2 3 fatigue
Level 3 4 fatigue, 1 damage
Level 4 5 fatigue, 2 damage
Level 5+ 6+ fatigue, 3+ damage
(damage is capped to 1 unless unit is frozen)
Heat Cloud
Level 1 2 fatigue
Level 2 3 fatigue
Level 3 4 fatigue, 1 damage
Level 4 5 fatigue, 2 damage
Level 5+ 6+ fatigue, 3+ damage
Poison Cloud
Level 1 1 poison
Level 2 2 poison
Level 3+ 3+ poison
Disease Cloud
Level 1 disease (easy MR)
Level 2 disease (easy MR)
Level 3+ disease (MR)
Sulphur Cloud
Level 1 1 fire fatigue + 1 poison
Level 2 1 fire fatigue + 1 poison
Level 3 2 fire fatigue + 1 poison
Level 4 2 fire fatigue + 2 poison
Level 5 3 fire fatigue + 2 poison
Level 6 3 fire fatigue + 3 poison
Level 7 4 fire fatigue + 3 poison
(poison is capped to 1 point of damage)
Rust Cloud
Level 1 armor rusts
Level 2 armor rusts
Level 3+ armor rusts
Death Cloud
Level 1 1 damage (MR)
Level 2 2 damage (MR)
Level 3+ 3+ damage (MR)
68

### Morale and rout

#### Morale

#### Morale bonuses

#### Rout

##### Morale, magic bonus

[p.69]
Shimmering Light Cloud
Level 1 1 capped false damage (easy MR)
Level 2 1 capped false damage (MR)
Level 3 2 false damage (MR)
Level 4+ 3+ false damage (MR)
Leeching Cloud
Level 1 weakness (easy MR)
Level 2 weakness (easy MR), 1 damage (easy MR)
Level 3 weakness (MR), 1 damage (easy MR)
Level 4+ weakness (MR), 1 damage (MR)
(weakness decreases Str by 1 permanently)
(all damage is capped to 1)
Sleep Cloud
Level 1 sleep (easy MR)
Level 2 sleep (MR)
Level 3+ sleep (MR)
All type of clouds range from level 1 to 7. Sometimes the
effects of the different levels are the same and higher level
clouds will only last longer. All damage from clouds is armor
negating.
Monsters that spread clouds, e.g. Hydra and Ghost, spread
level 1 clouds.  As they are spread at level 1 they can
accumulate to at most a level 2 cloud. Spells and magic items
can create clouds at higher levels.
Heat Clouds and Frost Clouds cancel out each other and it is
not possible for both of them to be in the same square.
Morale and rout
Morale
Morale is a measure of how likely a squad is to keep fighting
after taking casualties.  Each unit has a morale value, but the
morale value that is checked is the morale level of the entire
squad.  Each squad has a morale level, which is the average
of all the morale ratings of the members of the squad.
Morale bonuses
A unit can have a number of modifiers to its morale.  For
example, Sacred units can be blessed, which increases their
morale by 1.  In addition, all units can gain the following
bonuses:
* +1 for fighting in friendly dominion
* +1 for fighting in a unit’s  home province (the province where it
was recruited)
* +x for a commander's leadership bonus (click on Leadership
attribute)  This is further modified by the formation in which
the unit is fighting, how many squads the commander is leading,
etc.
* +1 for every level of the Inspirational ability the squad's
commander has (can also be negative)
* +x if there is a unit with the Standard ability in the squad,
where x is the bonus from highest Standard
Morale, magic bonus
Many magic effects can modify a unit's magic bonus to
morale. This bonus can go from -10 to +1. Units with fear
will lower this bonus and priests can increase it with the
Sermon of Courage and Fanaticism spells. Most combat spell
that causes some kind of fear effect will also modify this
bonus.
The morale magic bonus will increase by 1 about every 2
rounds if it is negative. A positive bonus will last the entire
battle if left to itself.
Rout
During combat, squads will have their members killed and
wounded, and eventually they will take flight from the field. 
This is called routing, and happens to the entire squad.
Rout is normally checked by squad.  A squad which fails its
morale check routs.  A squad will check morale if:
In a few rare cases a unit routs independently from its
squad.  This might happen if a mount loses its rider.
* The squad has suffered “heavy losses” since the last morale
check, and its overall casualties are at least 20%
* The squad has four or fewer units left in it and at least one of
the units has taken damage this round
* The squad is near a monster causing Fear (e.g. an Abomination)
* The squad has been subjected to a spell causing Fear (e.g.
Terror). Note that the spells causing Frighten do not apply.
* The entire army has taken 50% or more of its total hit point
value in casualties.  In this case, morale will be checked every
turn for the remainder of the battle.  Retinues are excluded
from this "greater than 50% of army hit points" if there is
nothing more than one creature and its retinue.  This is a
special case.
69

##### Army rout

##### Morale check

##### Rout effects

##### Mindless units

##### Magic beings and undead

##### Magic fear effects

[p.70]
“Heavy losses” is one wound for every two members of the
squad.  A “wound” is simply 1 or more hit points of damage
that reduces a unit to 80% or less of its normal hit points.  So
a unit with 25 hit points that is undamaged and suffers 4
points of damage does not count as having suffered a
“wound” for these purposes.  The next point of damage,
however, will reduce him to 80% of normal, and every hit
thereafter (even if for 1 point) will continue to satisfy these
criteria.  Units are very enthusiastic at the beginning of
battle, but less so after taking damage.
No matter how many times the above conditions are
satisfied, a squad cannot have its morale checked more than
once a turn.
Army rout
Once an army has taken 75% of its total hit point value in
casualties in a battle, it will automatically rout.
Mounts only have 25% of their HP count towards the army's
total HP. Any units from the Province Defence also only
have 25% of their HP count, they are expected to run. Slaves
are also expected to run and only have 50% of their HP
count.
Morale check
A morale check consists of two numbers, the morale roll and
the fear roll.  If the fear roll is greater than the morale roll,
the squad routs.  If not, the squad keeps fighting.  Although it
is called the “fear roll,” it applies to anything that checks
morale, not just fear.
Morale roll: squad morale + DRN + survivor bonus
Fear roll: 14 + DRN
The survivor bonus ranges from 0-5, depending on how
many of the squad’s original members are still alive.  The
smaller the proportion of survivors, the smaller the bonus. 
An intact (or almost intact) squad will get a bonus of 5.  A
squad that has been almost wiped out gets no bonus.
Rout effects
A routed unit will use all of its action points each turn to
move towards its own side of the battlefield and off the
friendly edge.
A routing unit suffers a -4 penalty to its defense skill.  Fast
units can be very effective at picking off enemy units that
are routing, as they have a better chance of catching them
before they exit the map.
Once a routing unit reaches the map edge, it is safe, and on
the turn after the battle will appear in a province adjacent to
the battle (see Retreat rules on page 72).  If a unit
retreats to an enemy province, it is destroyed.  A routed
army may scatter to multiple provinces after a battle,
requiring a commander to go collect it.  Routed units
suffering from profuse bleeding, poison, burning, decay or
other special damage will have the remainder of that
damage applied once they get off the map edge and may not
survive.  This represents the unit successfully fleeing the
battle but expiring of its wounds before finding help.
Units in a victorious army can rout off the map as well, since
a squad can rout while others are winning the battle.  If the
battle ends before the routing units exit the map, at the end
of the battle they remain with the victorious army.  If they
rout off the map before the battle ends, they scatter to
adjacent provinces.
Mindless units
Mindless units need to be under the control of a
commander.  If there are no unrouted commanders on the
battlefield eligible to command mindless units, remaining
mindless units on the field are automatically subject to
mindless dissolution.
If all eligible commanders (i.e. commanders who can
command mindless units) have been killed or routed, the
mindless beings become immobile and have a 33% chance
each turn of dissolving and vanishing from the battle.  They
will not move, but will attack adjacent units.
Magic beings and undead
These units have special leadership requirements, such as
magical leadership or undead leadership.  If such units are
on the battlefield without proper leadership, they will rout.
If a unit is both an undead and a magic being (such as the
manikins of Asphodel), it requires undead leadership to lead.
Demons require undead leadership to lead.
Magic fear effects
There are two types of magic fear effects: fear and frighten. 
Fear is the most severe and the most common one, it can
decrease morale by up to 10 points.  Being subject to fear
will also force the entire squad to make a morale check at
the end of the round, failure means it will break.  Units hit by
70

### Afflictions

### Sieges

##### Long lasting battles and Twilight

[p.71]
magic fear effects may also break individually if they fail an
easy morale check.
Breaking individually will make the unit flee while his
companions stay and continue to fight. This can only occur
due to magic fear, normally the squad will always break and
flee together.
Frighten is much less severe.  It can lower morale by up to 5
points, but does not force any automatic morale checks.
Long lasting battles and Twilight
If a battle goes on for too long the sun sets.  This will have
profound effects on the remainder of the battle.  Battle
enchantments and other spells will end and the battlefield
will be affected by Twilight, as per the spell.  Berserking ends
and berserkers cannot go berserk again.
Turn Effects
100 Twilight: All enchantments, temporary magic effects and
berserking ends, Twilight effect (-2 prec, +1 glamour magic).
150 Nightfall/Daybreak: Attacking units rout, Darkness effect
(-3 att/def/prec), or return to daylight in case of a night time
battle.
170 Defending units rout.
200 Any units left on the battlefield are killed.
Note that mindless units cannot rout and will dissolve
instead of routing.
Afflictions
Whenever a unit is struck in battle, it may suffer an
affliction. The chance of this occurring is simply the % hit
points lost in the blow.  So if a normal 10HP soldier receives
two 4HP blows, he would have a 40% chance and then
another 40% chance of getting an affliction.  What type of
affliction is suffered depends on which part of the body was
struck.
It is possible to get more than one affliction if the damage
exceeds 100%, e.g. a single blow dealing 15HP damage on a
10HP soldier would result in one affliction and then a 50%
chance for an additional one. Of course the soldier would be
dead afterwards, so the extra affliction would only matter if
he was raised from the dead somehow.
There are major afflictions and minor afflictions.  The chance
of an affliction being major is affliction chance / 1.5, or at
most 33%.  Where the hit occurs determines which kind of
afflictions may be inflicted.  The game will randomize from
all afflictions available for that level (major or minor) and
that body part.
Body Part Minor Affliction Major Affliction
Any Battle Fright
Profuse Bleeding
Head Eye Loss Dementia
Mute Feeblemindedness
Blindness
Chest Chest Wound Diseased
Never-Healing Wound
Arm Weakened Lost an arm
Leg Limp Crippled
Profuse Bleeding is the only affliction that is not permanent:
it will disappear during or after the battle.  While a unit
bleeds, it loses 5% of its hit points and gains 10 fatigue per
round of combat.  The bleeding has a 10% chance of
stopping per round.  Being underwater halves this chance
and regeneration increases it.
Limp will cause commanders to suffer a -4 map movement
penalty.  Non-commander units do not lose any map
movement points, but whenever their army marches more
than one province in a month, they will have a 25% chance of
becoming crippled.
Cripple will cause commanders to lose 75% of their map
movement speed.  Non-commander units do not lose any
map movement points, but whenever their army marches,
they will have a 35% chance of dying, or a 70% chance of
dying if marching more than one province.
Sieges
Fortresses must be reduced before they can be stormed.  To
reduce a fortress, its Defense value must be reduced to zero.
Each turn, the total reduction strength of the besiegers is
compared to the total repair strength of the defenders.
Reduction strength = unit strength squared
* Flying units are doubled
Repair strength = unit strength squared / 2
* Flying units are doubled
* Mindless units are only worth 1/8th of calculated value
* Animals (not monkeys!) are halved
* Undisciplined units are halved
71

### Storming a castle

### Weather

### Retreats

#### Supply during sieges

[p.72]
The difference is subtracted from the fortress defense value
if the Reduction strength is greater.  If the fortress has been
damaged, and the repair strength is greater, the difference is
added back to the defense value, to the maximum of the
original value.
That's why you get the message sometimes when you're the
besieger, that "the enemy is repairing the walls faster than
we can destroy them. We need more men." This means the
repair value is higher than the reduction value, and the
besieged units are actually fixing the walls.  There is no way
for the besieger to know exactly how close a fortress is to
being breached (although you will get hints).  The defender,
however, can click on the fortification location button in
that province, and the current defense value will be
displayed.  Fortresses which are damaged but not besieged
are automatically fully repaired.
Supply during sieges
When a fortress is besieged, it provides its supply value to
the defenders, divided by the number of turns of the siege. 
So on the first turn of a siege, a fortress with 300 supply
provides 300 supply points on the first turn of the siege,
then 150, then 100, then 75, then 60.  Units which are
unsupplied suffer the starvation effect, and units which
starve for two consecutive turns can become diseased. 
Diseased units will then start to slowly get more afflictions
and eventually die.
Storming a castle
When the fortress' wall integrity value is reduced to zero it
can be stormed. Commanders besieging the fortress can
choose to 'Storm Castle' or 'Maintain Siege'.  If one or more
commander storms the castle a battle at the gates of the
fortress will take place.  Inside the walls are the defending
units and outside the walls are commanders with the 'Storm
Castle' order along with all units under their command.  If a
commander set to 'Storm Castle' is killed before the battle
at the fortress takes place, units under his command will not
participate in the battle.  The storming of the castle takes
place after any other battle in the province, so it is possible
to fight off or decimate the besieging army before they
storm the castle.
All forts have some additional units that will aid the
defender in the battle "see page  26.
Weather
The weather for any land battle is usually clear skies and
during the day. But the weather can also be rainy or snowy
at random times, unless the battle occurs in a wasteland or
in a cave.
Snowfall can only happen if the cold scale is 1 or more and
rain can only occur if the heat is 0 or greater.
Snowfall chance
Cold scale * 15%
Rainfall chance
Growth scale * 10% + 10%
Global enchantments can also affect the weather in many
ways. Assassination battles are special and often occur
indoors where there is no weather and have about 50%
chance of occurring at night. If they occur outdoors they use
the same chances for rain and snow as other battles.
Retreats
If units retreat from a battle, they will go to an adjacent
province, or perhaps a friendly castle in the same province. 
To do this, a commander must be smart.  Each commander
will undergo a check and has a 75% chance of making a
“smart” retreat.  (If a unit is in native terrain, it will get a
second chance to be smart at 50% if it fails its first check.
A smart leader will:
* Retreat into a fort in the same province if there is one
* Move to a random friendly-controlled adjacent province if no
fort is present
A not-so-smart leader will:
* Move into a random adjacent province, even if not friendly
controlled.
Troops will follow a leader under whose command they are
when they retreat, if they pass a morale check.  The squad
morale bonus counts double for this, undisciplined units
suffer a -3 penalty, and the squad morale penalty for
skirmish formation also applies.
Troops that have lost their leader or who fail a check to
follow their leader will individually check for being smart or
not (with only a 50% chance of success, although the 50%
second chance for natives still applies) and then retreat
72
