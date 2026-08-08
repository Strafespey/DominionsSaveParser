# Launch Options

*Manual pages 430–449 (1-based).*

[p.430]
Launch Options
The following launch options (command line options) can be used to modify the behavior of the game before it starts up. Most players will
not need to use this feature, but it can be used to automate things or help if the game doesn't start properly.
The short options can be combined e.g. "-sw" will start without sound and in a window.
-v  --version       Print version number and exit
-d                  Increase debug level
-g  --host          Generate new turn and exit
    --verify        Verify all 2h-files and exit (creates .chk files)
    --statfile      Create a player info file after each turn (stats.txt)
    --scoredump     Create a score file after each turn (scores.html)
    --finalhost     Generate new turn, send out final score msg and exit
-c  --nocredits     Disables the end credits
    --noedgescroll  Disables edge scrolling
    --edgescroll    Enables edge scrolling in fullscreen mode
    --winedgescroll Enables edge scrolling always
    --askifplayed   Will ask if you want to redo turn if possible
    --noshowscouts  Do not show allied scouts on map
    --autoorder     Put new mages on research by default
    --multimove     Enable multiple turn movement
    --maxunits X    Sets max nbr of units in a game (default and max 600000)
    --listnations   Prints a list of all nation numbers
    --multiai X     Create up to X processes for AI computations (0=off) (Linux only)
    --nothread      Don't use multithreading
    --nomappopups   Don't show popups on the main map
    --nosteam       Do not connect to steam (workshop will be unavailable)
    --nocrashbox    Don't show a dialogue box with crash message on (Windows only)
    --useolddata    Try to preserve battle replays after upgrading
    --gamepad       Enable gamepad/joystick inputs
    --nogamepad     Disable gamepad/joystick inputs
    --backup        Create a tar archive of save before hosting (Linux only)
******* Network Options *******
    --lobby         Enter game lobby
    --lgpasswd XXX  Password for lobby game
-C  --tcpclient     Connect to a Dominions multiplayer server
-S  --tcpserver     Start a Dominions multiplayer server
    --tcpquery      Query Dominions server about game status and exit
    --ipadr XXX     Use this IP-adr when connecting to server
    --port X        Use this port nbr
    --preexec CMD   Execute this command before each new turn
    --postexec CMD  Execute this command after each new turn
-t  --hosttime X Y  Host on day X (0=sunday) hour Y (0-23)
    --minutes X     Set host interval in minutes
    --hours X       Set host interval in hours
    --pauseday X    Stop timer on this day (0=sunday)
    --timeleft X    Hours until first host (default = full host interval)
    --noquickhost   Don't host just because all turns are done
    --maxholdups X  Quickhost disregards players that have stalled last X turns
-n  --nonationsel   No nation selection when resuming a network game
-o  --onserver      I'm playing on the server, don't ask
    --noclientstart Clients cannot start the game during Choose Participants
430

[p.431]
--uploadtime X  Game is created after this many minutes.
    --uploadmaxp X  Game is created if this many players join.
    --closed X      Nation closed X=nation number (5-499)
    --easyai X      Nation ai controlled X=nation number (5-499)
    --normai X      Nation ai controlled X=nation number (5-499)
    --diffai X      Nation ai controlled X=nation number (5-499)
    --mightyai X    Nation ai controlled X=nation number (5-499)
    --masterai X    Nation ai controlled X=nation number (5-499)
    --impai X       Nation ai controlled X=nation number (5-499)
    --team X Y Z    X=nation, Y=team, Z=type (type: 1=pretender, 2=disciple)
    --statuspage XX Create html page that shows who needs to play their turn
    --statusdump    Continuously create info on players in a parsable format
    --nodownlmods   Don't download mods from game server automatically
    --nomaster      Disallow download/upload turns using the master password
    --timerwarn X   Warning sound when less than X seconds left (0=disable)
******* New Game Options *******
    --mapfile XXX   Filename of map. E.g. eye.map
    --randmap X     Make and use a random map with X prov per player (10,15,20)
    --research X    Research difficulty 0 to 4 (default 2)
    --norandres     No random start research
    --hofsize X     Size of Hall of Fame 5-15 (default 10)
    --mercsize X    Maximum number of Mercs 0-10 (default 5)
    --globals X     Global Enchantment slots 3-9 (default 5)
    --yearning X    Yearning chance for artifacts (default 50)
    --indepstr X    Strength of Independents 0-9 (default 5)
    --magicsites X  Magic site frequency 0-75 (default 40)
    --eventrarity X Random event rarity 1-2, 1=common 2=rare
    --richness X    Money multiple 50-300 (default 100)
    --resources X   Resource multiple 50-300 (default 100)
    --recruitment X Unit recruitment point multiple 50-300 (default 100)
    --supplies X    Supply multiple 50-300 (default 100)
    --masterpass XX Master password. E.g. masterblaster
    --startprov X   Number of starting provinces (1-9)
    --renaming      Enable commander renaming
    --scoregraphs   Enable score graphs during play
    --nonationinfo  No info at all on other nations
    --weakdiplo     Formal dimplomacy is non-binding
    --nodiplo       No formal dimplomacy
    --nocheatdet    Turns off cheat detection
    --era X         New game created in this era (1-3)
    --nomods        Disable all mods
-M  --enablemod XXX Enable the mod with filename XXX
    --noartrest     Players can create more than one artifact per turn
    --nolvl9rest    Players research lvl 9 spells as fast as any other spells
    --teamgame      Disciple game, multiple players on same team
    --clustered     Clustered start positions for team game
    --edgestart     Edge start positions for team game
    --nostoryevents Disable all story events
    --storyevents   Enable some story events
    --allstoryevents Enable all story events
    --newgame       Create a new game and exit (for scripted game creation)
    --newailvl X    AI level for human players who quit (1-6, def 2)
431

[p.432]
--nonewai       Disable become AI controlled
******* New Game Victory Condition *******
    --conqall        Win by eliminating all opponents only
    --thrones X Y Z  Number of thrones of level 1, 2 and 3
    --requiredap X   Ascension points required for victory (def total-1)
    --cataclysm X    Cataclysm will occur on turn X (def off)
******* Random Map Options *******
    --makemap XXX    Generate a random map with filename XXX and exit
    --tgapreview     Also make a tga preview for the random map
    --blueprint XXX  Use this TGA/PNG file as blueprint for random map
    --blueacc X      0-9, the blueprint accuracy (default 2)
    --noundercaves   Don't create a underworld plane with caves
    --riverpart X    0-1000, 0=no rivers (default 100)
    --bridges X      Bridge chance 0-100, 0=no bridges (default 60)
    --extraislands X Chance of extra islands 0-100, (default 0)
    --seapart X      Percent of map that is below water level (default 45)
    --cavepart X     Percent of under caves plane that is caves (default 20)
    --mountpart X    Percent of map that is mountains (default 20)
    --forestpart X   Percent of lands that are forests (default 20)
    --farmpart X     Percent of lands that are farm lands (default 15)
    --wastepart X    Percent of lands that are wastes (default 10)
    --swamppart X    Percent of lands that are swamps (default 10)
    --kelppart X     Percent of seas that are kelp forests (default 25)
    --gorgepart X    Percent of deeps seas that are gorges (default 25)
    --mapsize W H    Set width and height of random map (default 3000 2000)
    --mapprov X      Set number of provinces (default 150)
    --mapscol R G B A   Sea color 0-255 (default 54 54 130 255)
    --mapdscol R G B A  Deep Sea color 0-255 (default depending on mapscol)
    --mapccol R G B A   Coast color 0-255 (default depending on mapscol)
    --mapbcol R G B A   Ground border color 0-255
    --mapsbcol R G B A  Sea border color 0-255
    --mapbtopcol R G B A   Top border color 0-255
    --mapnoise X     Ground color noise 0-255 (default 15)
    --mapdirt X      Amount of dirt blobs (default 100)
    --mapdirtcol X   Color variance of dirt blobs (default 5)
    --mapdirtsize X  Size of dirt blobs (default 100)
    --borderwidth X  Border width 0-500 (default 100)
    --hills X        Number of Hills/Craters (default 150)
    --rugedness X    Rugedness 0-100 (default 30)
    --seasize X      Sea size, 100=normal land size (default 350)
    --mapnospr       Don't draw any sprites on the map
    --nowaterprov    Don't put any capitals in the water areas
    --vwrap          Make map wrap north/south
    --nohwrap        Make map not wrap east/west
    --mapbunch X     When making a bunch, make this many maps (default 12)
    --quiet          Don't print stuff
******* Graphics Options *******
-w  --window        Run Dominions 6 in a window
-u  --fullscreen    Use the entire screen
    --borderless    Use a borderless fullscreen window
432

[p.433]
--bitplanes X   Try to use a color depth of X bits per pixel
    --zbuffer X     Try to use a depth buffer of X bits per pixel (default 24)
-T  --textonly      Use this with --tcpserver to get graphicless server
    --gamma X       Set gamma function (brightness) 0.1 - 5.0 (default 1.0)
    --opacity X     Set gui opacity 0 - 100
-r  --res X Y       Set screen resolution / window size
    --animback      Use animated backgrounds
-a  --noanimback    Don't use animated backgrounds
    --fade          Use fade effects
-f  --nofade        No fade effects
    --nopopups      No helpful popups
    --maxfps X      Maximum nbr of frames per second (default 60)
    --filtering X   Quality of OpenGL filtering 0-3 (default 2)
    --maxtexsize X  Max texture size in pixels 8-4096 (default unlimited)
    --texqual X     Texture quality 1-5 (default 3)
    --notracers     Visual aid, puts a particle trace after arrows
    --nomapcolrit   Don't color map remote ritual dots per path
    --nolightfx     No light effects in battles
    --partamount X  Max nbr of particles 0-9 (0=none, 4=default, 9=max)
    --noarcade      Don't draw floating damage numbers
    --batflash      Flash units green/magenta when receiving buffs/debuffs
    --nonetinfo     Don't draw timer and flags during network play
    --glfinish      Flush the graphics pipeline each frame
    --noglfinish    Don't flush the graphics pipeline each frame
    --noglext       Don't use any OpenGL extensions
-x  --fastgrx       Faster and simpler graphics
    --simpgui       Use a simple GUI without any background textures
    --gfxlevel X    Graphics level 1-20 (default 10, 14 = very high)
    --multisample X Use multisampling, X=number of samples (0-16)
    --renderpath X  Use a different rendering method 0-3 (default 2)
    --benchmark     Run a graphics benchmark and exit
    --softmouse     Draw a mouse cursor instead of using the standard OS one
    --textsize X    Set size of text in percent (small 90, std 100, huge 120)
    --battextsize X Set size of floating texts in battles (std 100)
    --nowarnings    Disable warnings for bad graphics drivers
******* Audio Options *******
-s  --nosound       No sound effects or music
-m  --nomusic       No music
    --musicvol X    Set music volume, 0-100 (default 100)
    --fxvol X       Set sound effect volume, 0-100 (default 100)
    --clickvol X    Set mouse click volume, 0-100 (default 25)
    --randpitch X   Set max sound effect pitch randomness (default 3)
    --noturnsound   Don't play a sound when a new turn arrives (network only)
    --jack          Route sound through JACK sound server (Linux)
    --pulseaudio    Route sound through pulse audio (Linux)
    --alsa          Use direct alsa sound output (Linux)
    --oss           Use direct oss sound output (Linux)
    --portaudio     Use portaudio for sound (Linux & OSX)
    --directsound   Use direct sound (Windows)
    --waveout       Use waveout for sound (Windows)
    --sdlsound      Force usage of default sdl sound device (Windows)
433

[p.434]
A
A Short History of Dominions  6
Abominable Arms  112
About The Creation of Dominions 4  7
About the Creation of Dominions 5  9
About the Creation of Dominions 6  11
Abysia  89
Abysia, Blood and Fire  327
Abysia, Blood of Humans  389
Abysia, Children of Flame  263
Acashic Knowledge  223
Acashic Record  223
Access to Magic Spells  74
Acid Bolt  121
Acid damage  67
Acid Rain  121
Acid Spray  121
Acid Storm  121
Acorn Necklace  111
Additional abilities  40
Admin  25
Afflictions  41, 71
Agartha  89
Agartha, Golem Cult  319
Agartha, Ktonian Dead  385
Agartha, Pale Ones  261
Agony  130
AI Opponents  30
Air Shield  120
Alchemical Transmutation  221
Alchemist's Stone  113
Alchemy  81
All-consuming Pyre  120
Amalgamation of Air and Flesh  192
Amalgamation of Earth and Flesh  192
Amalgamation of Fire and Flesh  192
Amalgamation of Water and Flesh  192
Ambush of Tigers  161, 162, 180, 181, 
198
Amon Hotep  108
Amulet of Antimagic  111
Amulet of Breathing  110
Amulet of Clarity  110
Amulet of Giants  111
Amulet of Missile Protection  110
Amulet of Resilience  111
Amulet of the Dead  111
Amulet of the Doppelganger  113
Amulet of the Fish  111
Anathema  138
Andramania, Dog Republic  420
Anemone Mace  100
Angelic Choir  172, 174, 192
Angelic Host  172, 174, 192
Animal Horde  149
Animate Dead  125
Animate Skeleton  125
Animate Tree  126
Animated Weapons  64
Antimagic  124
Apostasy  136, 138
Appointing a prophet  83
Arcane Analysis  223
Arcane Bolt  124
Arcane Decree  211
Arcane Domination  125
Arcane Lens  112
Arcane Nexus  211
Arcane Probing  223
Arcoscephale  89
Arcoscephale, Golden Era  243
Arcoscephale, Sibylline Guidance  373
Arcoscephale, The Old Kingdom  303
Ardmon's Soul Trap  113
Armor defeating hits  61
Armor of Achilles  123
Armor of Knights  106
Armor of Meteoritic Iron  106
Armor of Souls  106
Armor of the Dawn  107
Armor of the Five Elements  106
Armor of Twisting Thorns  106
Armor of Virtue  107
Army of Bronze  124
Army of Giants  126
Army of Gold  123
Army of Lead  123
Army of Mist  120
Army of Rats  126
Army of Shades  128
Army of the Dead  147
Army Regeneration  126
Army rout  70
Army Setup  43, 58
Arouse Hunger  147
Arrow Fend  120
Arrow of the Western Wind  120
Arrow Ward  120
Aseftik's Armor  107
Ashdod, Reign of the Anakim  329
Ashes to Ashes  131
Asphodel  89
Asphodel, Carrion Woods  308
Assassinate  52
Astral Corruption  214
Astral Disruption  223
Astral Fires  124
Astral Geyser  124
Astral Healing  124
Astral Projection  223
Astral Serpent  111
Astral Shield  124
Astral Tempest  124
Astral Travel  223
Astral Window  223
At the End of the Rainbow  228
Atlantis, Emergence of the Deep Ones  
300
Atlantis, Frozen Sea  426
Atlantis, Kings of the Deep  369
Atlas of Creation  113
Attack Current Province  55
Attentive Statues  173
Augury  217
Aura of Bewilderment  128
Aura of Splendor  128
Aurora Borealis  128
Auspex  219
Authors Note  12
Automatic Bless Effects  37
Awaken Algae Men  149
Awaken Dark Vines  153
Awaken Draugar  166, 167, 186, 203
Awaken Forest  126
Awaken Hamadryad  155, 156, 170, 172, 
189, 190
Awaken Ivy King  149
Awaken Jinn Block  176
Awaken Jotun Draugar  168, 188, 204
Awaken Sepulchral  191
Awaken Shard Wights  173, 191
Awaken Sleeper  151
Awaken Tarrasque  149
434

[p.435]
Awaken Tattoos  133
Awaken Tomb Oracle  191
Awaken Treelord  149
Awaken Vine Men  149
Awaken Vine Ogres  149
Axe of Hate  101
Axe of Sharpness  100
B
Bag of Winds  111
Baleful Star  223
Bandar Log, Kailasa, Lanka and Patala  90
Bandar Log, Land of the Apes  336
Bane Blade  100, 102
Bane Fire  125
Bane Fire Dart  125
Bane Venom Charm  111
Banefire Crossbow  104
Banish Demon  130
Banishment  131
Banner of the Northern Star  103
Banquet for the Dead  175
Barathrus Pact  157, 173
Barkskin  126
Barkskin Amulet  110
Barrel of Air  112
Barrier  105
Basic attributes  38
Basic Game Functions  18
Battle Fortune  128
Battle Fury  118
Battle Magic  75
Battle Magic mechanics  75
Battle Orders  44
Battle position  44
Battle sequence  58
Battle Summary  73
Battlefield movement  60
Battlefield Spells  118
Battles View  58
Bear Claw Talisman  109
Beast Fury  126
Beast Mastery  128
Beckoning  228
Become Prophet  54
Behemoth  147
Bell of Cleansing  113
Berserker Pelt  105
Berytos  90
Berytos, The Phoenix Empire  286
Bewitching Lights  128
Bind Arch Devil  153
Bind Beast Bats  163, 164, 183, 200, 201
Bind Bone Fiends  153
Bind Demon Knight  153
Bind Demon Lord  153
Bind Devil  153
Bind Fiend  153
Bind Fiery Imps  153
Bind Frost Fiend  153
Bind Harlequin  192
Bind Heliophagus  153
Bind Ice Devil  153
Bind Incubus  153
Bind Jaguar Fiends  163, 164, 183, 200, 
201
Bind Keres  155, 169, 170, 186, 189
Bind Penumbral  157
Bind Scorpion Beast  141
Bind Serpent Fiends  153
Bind Shadow Imp  153
Bind Spine Devil  153
Bind Storm Demon  153
Bind Succubus  153
Bind Tzitzimitl  163, 183, 200
Bind Umbral  157
Birch Boots  109
Black Bow of Botulf  104
Black Death  225
Black Dragon Scale Mail  106
Black Halberd  102
Black Laurel  107
Blacksteel Barding  114
Blacksteel Full Plate  105
Blacksteel Helmet  107
Blacksteel Kite Shield  104
Blacksteel Plate  105
Blacksteel Sword  99
Blacksteel Tower Shield  104
Blade of Grass  100
Blade Wind  123
Blast of Unlife  125
Bleed  130
Bless Effects  32
Blessing  131
Blessing of the God-slayer  231
Blight  221
Blindness  118
Blink  124
Blizzard  120
Blood Boil  130
Blood Burst  130
Blood Feast  230
Blood Fecundity  230
Blood Heal  130
Blood Hunt  51
Blood Lust  130
Blood Moon  214
Blood Pendant  112
Blood Poisoning  126
Blood Rain  130
Blood Rite  153
Blood Sacrifices  84
Blood Stone  111
Blood Thorn  101
Blood Vortex  214
Bloodletting  131
Bloodstone Armor  106
Blue Dragon Scale Mail  106
Blur  128
Blurred Body  128
Boar Leather Barding  114
Body Ethereal  124
Bogarus, Age of Heroes  410
Bogarus, Vanarus, and Rus  90
Boil  118
Bolt of Unlife  125
Bonds of Fire  118
Bone Armor  106
Bone Grinding  126
Bone Melter  121
Boots of Antaeus  109
Boots of Giant Strength  109
Boots of Grasping Earth  109
Boots of Long Strides  109
Boots of Quickness  109
Boots of Seven Mile Strides  109
Boots of Stone  109
Boots of the Behemoth  109
Boots of the Messenger  109
Boots of the Planes  109
Boots of the Spider  109
Boots of Youth  109
Bottle of Living Water  112
435

[p.436]
Bow of the Titans  104
Bow of War  104
Bowl of Blood  230
Bracers of Protection  110
Brazen Vessel  111
Break Siege  52
Break the First Soul  134, 137, 140
Break the Fourth Soul  134, 137, 140
Break the Second Soul  134, 137, 140
Break the Third Soul  134, 137, 140
Breath of the Desert  217
Breath of the Dragon  126
Breath of Winter  121
Brightmail Haubergeon  106
Brightmail Hauberk  106
Brimstone Boots  109
Brood of Garm  167, 168, 188, 204
Burden of Time  211
Burn  118
Burning Blade  100
Burning Hands  118
Burning Pearl  110
C
C'tis  91
C'tis, Desert Tombs  407
C'tis, Lizard Kings  282
C'tis, Miasma  350
Caelum  91
Caelum, Eagle Kings  277
Caelum, Reign of the Seraphim  342
Caelum, Return of the Raptors  393
Call Abomination  147
Call Ahurani  163, 183, 194
Call Amesha Spenta  163, 183, 194
Call Ancestor  133, 134, 139
Call Ancient Presence  143
Call Anzus  159, 177
Call Apkallu  159, 177
Call Arel  175, 177, 195, 205
Call Celestial Soldiers  161, 180, 198
Call Celestial Yazad  163, 183, 194
Call Cyclops Tribe  177, 205
Call Daevas  163, 183, 194
Call Ephor  169
Call Fravashi  163, 183, 194
Call God  36
Call Greater Daeva  163, 183, 194
Call Hashmal  175, 177, 195, 205
Call Horror  130
Call Jahi  163, 183, 194
Call Krakens  143
Call Ladon  186, 206
Call Lesser Horror  130
Call Malakh  175, 177, 195, 205
Call Melqart  166
Call Merkavah  175, 177, 195, 205
Call of the Drugvant  233, 236, 239
Call of the Wild  149
Call of the Winds  142
Call Ophan  175, 177, 195, 205
Call Spectral Philosopher  169
Call the Birds of Splendor  177, 205
Call the Eater of the Dead  147
Call the Worm That Walks  149
Call Wraith Lord  147
Call Yata  163, 183, 194
Calm Emotions  121
Capsule screen  23
Capture Slaves  54
Carcator the Pocket Lich  113
Carmine Cleaver  103
Carrier Birds  219
Carrier Eagle  219
Carrion Bow  104
Carrion Centaur  171
Carrion Fortress  235
Carrion Growth  135
Carrion Lady  171
Carrion Lord  171
Carrion Reanimation  147
Carrion Seed  112
Castle Guards and Wall Defenders  26
Cat Charm  110
Cat Eyes  126
Cat's Eye Amulet  110
Cat-eyed Warriors  126
Cataclysm  17
Cauldron of the Elven Halls  111
Celestial Chastisement  134, 137, 139
Celestial Hounds  161, 180, 198
Celestial Music  134, 137
Celestial Rainbow  213
Celestial Servant  161, 180, 198
Chain Lightning  120
Chain Mail of Displacement  106
Chains of Reconstruction  112
Champion's Skull  110
Charcoal Shield  105
Charge Body  120
Charm  128
Charm Animal  126
Cheat prevention  17
Chi Shoes  109
Choleria  217
Choosing an Age  14
Choosing participants  15
Chorus Master  136
Chorus Slave  136
Claim Life  131
Clam of Pearls  110
Claws of Kokytos  130
Claymen  143
Cleansing Water  121
Cloak of Invisibility  106
Clockwork Bird  110
Clockwork Horrors  145
Clockwork Soldiers  145
Cloud of Death  125
Cloud of Dreamless Slumber  128
Cloud Trapeze  219
Clouds  68
Cockerel Scepter  100
Coin of Meteoritic Iron  111
Cold Blast  121
Cold Bolt  121
Cold damage  66
Cold Resistance  118
Cold Resistant Warriors  118
Combat  57
Combined Paths  74
Combustion  118
Command Draugar  188
Commander orders  45
Communal Chants  79
Communion Master  124
Communion Slave  124
Communions  78
Companion Bracelet  111
Conflagration  118
Confusion  128
Conjure Phantasmal Beast  128
Conjure Phantasmal Knight  128
Conjure Phantasmal Warriors  128
436

[p.437]
Conjure Phantasmal Wolves  128
Construct Building  55
Construct Mandragora  149
Construct Manikin  149
Contact Alkonost  167, 186, 203
Contact Allies  54
Contact Angel of the Host  172, 174, 192
Contact Bakeneko  181, 198
Contact Beregina  167, 186, 203
Contact Boar of Carnutes  157
Contact Civateteo  163, 183, 200
Contact Cloud Vila  167, 186, 203
Contact Couatl  163, 165, 183, 185, 200, 
202
Contact Dai Tengu  162, 181, 198
Contact Draconians  142
Contact Forest Giants  149
Contact Forest Trolls  149
Contact Gamayun  167, 186, 203
Contact Harbinger  172, 174, 192
Contact Hesperide  186, 206
Contact Hill Giant  145
Contact Houri  176
Contact Huli Jing  161, 180
Contact Iron Angel  174
Contact Jigami  198
Contact Jinn  176
Contact Jorogumo  181
Contact Kaijin  198
Contact Kitsune  181, 198
Contact Lamia Queen  149
Contact Lamias  149
Contact Lar  156, 172, 190
Contact Leshiy  167, 186, 203
Contact Marid  158
Contact Mori-no-kami  198
Contact Mountain Vila  167, 186, 203
Contact Mujina  181, 198
Contact Nagaraja  178
Contact Nagarishi  178
Contact Nagini  178
Contact Naiad  143
Contact Nushi  162, 181, 198
Contact Onaqui  163, 164, 183, 200, 201
Contact Scorpion Man  157, 159, 165, 
175, 177, 185, 193, 202
Contact Sea Trolls  143
Contact Sirin  167, 186, 203
Contact Tanuki  181, 198
Contact Tatsu  198
Contact Tlahuelpuchi  163, 183, 200
Contact Trolls  145
Contact Void Spectre  207
Contact Yaksha  159, 178, 196
Contact Yakshini  159, 178, 196
Contact Yama-no-kami  198
Control  124
Control the Dead  125
Copper Plate  106
Coral Blade  100
Cornucopia  111
Corpse Candle  125
Corpse Man Construction  142
Corpses  24
Corruption  53
Craft Keledone  155, 170, 186, 189, 206
Crawl  121
Create Revenant  147
Creating a new game  14
Creating a Pretender  31
Creating Pretender  16
Creeping Doom  126
Cross Breeding  230
Crown of Bones  107
Crown of Command  107
Crown of Lead  107
Crown of Overmight  108
Crown of the Elements  108
Crown of the Fire King  108
Crown of the Frost King  108
Crown of the Ivy King  108
Crown of the Magi  108
Crown of the Shah  107
Crown of the Titans  108
Crown of the Whispering Dead  107
Crumble  221
Crusher Construction  145
Crystal Heart  112
Cure Disease  227
Curse  128
Curse of Balor  133
Curse of Blood  153
Curse of Stones  123
Curse of the Desert  121
Curse of the Frog Prince  126
Curse Tablet  238
D
Damage Reversal  130
Dance of Ephemeral Swords  128
Dance of the Morrigans  133
Dancing Shield  111
Dancing Trident  111
Dancing Weapons  64
Dark Knowledge  225
Dark Skies  208
Dark Slumber  235
Darkness  125
Daughter of Typhon  156, 190
Dawn Fang  101
Death of Immortal Pretenders  36
Decay  125
Deceive the Decree of the Lost  205
Decree of the Underworld  131
Defend  51
Defense  24, 25
Definition of participant  78
Demolish Building  55
Demon Bane  103
Demon Cleansing  123
Demon Whip  101
Desiccation  121
Despair  128
Destruction  123
Different Communions  79
Dimensional Rod  102
Dire Wolf Pelt  105
Dirge for the Dead  175
Disciple games  15
Disease Grinder  113
Disenchantment  223
Disintegrate  125
Dispel  223
Dispel mechanics  77
Dispelling global enchantments  77
Displace Body  128
Displaced Warriors  128
Distill Gold  217
Divine Blessing  131
Divine Channeling  132
Divine Magic  32, 81
Divine Name  223
Dogs of Gold and Silver  186
Dome of Arcane Warding  223
437

[p.438]
Dome of Corruption  230
Dome of Flaming Death  217
Dome of Misdirection  228
Dome of Seven Seals  223
Dome of Solid Air  219
Dome of the Ancients  113
Dominion  23, 34, 82
Dominion effects  85
Dominion over water  83
Dominion scales  24, 85
Dominion spread  84
Dominion strategy  87
Dominion victory  87
Dominions Random Number (DRN)  13
Doom  124
Doom Glaive  102
Dragon Crown  107
Dragon Helmet  107
Dragon Master  228
Dragon Pretenders  31
Dragon Sceptre  101
Drain Life  125
Draupnir  113
Dream Seduction  53
Dream Spool  111
Dreams of R'lyeh  240
Dreams of the Awakening God  213
Dreamstone  111
Dreamwild Demesne  228
Dreamwild Legion  130
Duskdagger  100
Dust to Dust  125
Dwarven Hammer  100
E
Eagle Eyes  126
Eagle-eyed Warriors  126
Earth Attack  221
Earth Blood Deep Well  210
Earth Boots  109
Earth Gem Alchemy  221
Earth Grip  123
Earth Meld  123
Earth Sense  221
Earth Shatter Army  124
Earth Shatter Hammers  123
Earth-touching Sign  139
Earthquake  123
Earthquake Warriors  123
Effects of Dominion Scales  85
Effigy of War  110
Elemental Armor  106
Elemental Dampening  210
Elemental Fortitude  126
Elemental Opposition of Air  221
Elemental Opposition of Earth  219
Elemental Opposition of Fire  220
Elemental Opposition of Water  217
Elf Bane  100
Elf Shot  128
Elixir of Life  112
Ember  101
Empowerment  74
Encase in Ice  121
Enchanted Barding  114
Enchanted Forests  212
Enchanted Helmet  107
Enchanted Mirror  111
Enchanted Pike  102
Enchanted Ring Mail Armor  105
Enchanted Saddle  114
Enchanted Salt  111
Enchanted Shield  104
Enchanted Spear  100
Enchanted Sword  99
Enchanted Walls  223
End of Culture  215
End of Weakness  134
Endless Bag of Wine  111
Enemy dominion  83
Enfeeble  125
Enlarge  126
Enliven Gargoyles  145
Enliven Granite Guard  173
Enliven Marble Oracle  173
Enliven Sentinel  173
Enliven Statues  145
Enormous Cauldron of Broth  110
Enslave Mind  124
Enslave Sea Trolls  169
Envenom Arrows  126
Ephemeral Blast  128
Ephemeral Bolt  128
Epopteia  238
Eriu  91
Eriu, Last of the Tuatha  317
Ermor and its legacy  91
Ermor, Ashen Empire  310
Ermor, New Faith  248
Ermorian Legion  171
Erytheia, Kingdom of Two Worlds  424
Eternal Pyre  208
Eternal Twilight  213
Ether Gate  223
Ethereal Crossbow  104
Evening Star  101
Extreme heat/cold scales  86
Eye of Aiming  110
Eye of Innocence  112
Eye of the Oracle  113
Eye of the Void  111
Eye Pendant  112
Eye Shield  105
Eyecatcher  100
Eyes of the Condors  236
F
Faerie Court  151
Faery Trod  227
Faithful  100
Falling Fires  118
Falling Frost  121
False damage  68
False Fetters  128
False Fire  128
False Horror  128
Fanaticism  132
Farflight  120
Farflight Arrows  120
Farstrike  123
Fascination  128
Fata Morgana  213
Fate of Oedipus  217
Father Illearth  153
Fatigue  62, 76
Fatigue damage  68
Fatigue distribution  78
Fay Steed Barding  115
Fay-eyed Warriors  128
Fear  71
Fear-not Sign  139
Feast for Ghuls  158, 176
Feast of Flesh  160, 178, 196
Feminie, Sage-Queens  416
438

[p.439]
Fenris' Pelt  107
Ferocity  126
Fever Fetish  113
Fields of the Dead  125
Final Rest  131
Fire Blast  118
Fire Bola  104
Fire Brand  101
Fire Cloud  118
Fire damage  66
Fire Darts  118
Fire Fend  118
Fire Flies  118
Fire in a Jar  110
Fire Plate  105
Fire Resistance  121
Fire Resistant Warriors  121
Fire Shield  118
Fire Storm  118
Fire Sword  99
Fireball  118
Fires from Afar  217
Fish Scale Boots  109
Fists of Iron  123
Flambeau  102
Flame Bolt  118
Flame Corpse Construction  191
Flame Eruption  118
Flame Helmet  107
Flame Storm  119
Flame Ward  118
Flameflesh Army  118
Flames from the Sky  217
Flaming Arrows  118
Flare  118
Flask of Holy Water  110
Flesh Eater  100
Flesh Ward  107
Flying Carpet  111
Flying Ointment  110
Flying Shards  123
Flying Shield  123
Fog Warriors  120
Fomoria and Tir na n'Og  92
Fomoria, The Cursed Ones  252
Forces of Darkness  153
Forces of Ice  153
Forest Dome  227
Forest Troll Tribe  149
Forge Brass Bull  155, 169, 170, 186, 189, 
206
Forge of the Ancients  210
Forgotten Palace  228
Formations  59
Fort of the Ancients  235, 238
Fortress statistics  26
Fortress types  25
Forts  25
Foul Air  211
Foul Vapors  126
Fountain of Youth  113
Freeze  121
Freezing Mist  121
Freezing Touch  121
Friendly Currents  121
Frighten  125
From Death Comes Life  238
Frost Brand  100
Frost Dome  220
Frost Fend  121
Frostflesh Army  121
Frozen Heart  121
Furious Warriors  118
Fury of the Wild  126
G
Gaia's Blessing  128
Gale Gate  208
Game settings  16
Game Tools  18
Garrison units  43
Gate Cleaver  103
Gate Stone  113
Gates of Horn and Ivory  213
Gateway  223
Gath, Last of the Giants  395
Geas  133, 136, 138
General orders  44, 46
General rules governing movement  47
Geoglyphs  236
Geyser  121
Ghost General  162, 181, 198
Ghost Grip  125
Ghost Riders  147
Ghost Ship Armada  209
Ghost Wolves  128
Giant Strength Warriors  123
Giant Warriors  126
Gift of Cat Eyes  126
Gift of Cheated Fate  124
Gift of Displacement  128
Gift of Flight  120
Gift of Formlessness  121
Gift of Giant Strength  123
Gift of Health  212
Gift of Nature's Bounty  212
Gift of Reason  227
Gift of Spirit Sight  124
Gift of Splendor  128
Gift of the First Soul  134, 137, 140
Gift of the Fourth Soul  134, 137, 140
Gift of the Furies  118
Gift of the Hare  126
Gift of the Moon  139
Gift of the Sacred Swamp  138
Gift of the Second Soul  134, 137, 140
Gift of the Serpent  126
Gift of the Third Soul  134, 137, 140
Gift of True Sight  128
Gifts from Heaven  123
Gigantomachia  215, 216
Girdle of Might  111
Global Enchantments  77, 208
Gloves of the Gladiator  102
Gnome Lore  221
God Brood  185
God-Slayer Spear  100
Golden Arbalest  104
Golden Barding  115
Golden Hoplon  105
Golem Construction  147
Gooey Water  121
Gossamer Barding  114
Gossamer Cloth  110
Gossamer Gown  105
Gossamer Veil  107
Grand Communions  78
Great Lamentation  171
Greater Farflight  120
Greater Hannya Pact  233
Greatsword of Sharpness  102
Green Dragon Scale Mail  106
Grip of Winter  121
Ground Army  123
439

[p.440]
Group Barkskin  126
Group Blur  128
Group Ironskin  123
Group Luck  128
Group Regeneration  126
Group Stoneskin  123
Grow Fortress  232, 234, 237
Growing Fury  126
Guardians of the Deep  209
Gust of Winds  120
H
Hail of Burning Embers  118
Hail of Serpent Fangs  126
Halberd of Might  102
Hall of Statues  173
Hall of the Dead  191
Hammer of the Forge Lord  103
Hammer of the Mountains  102
Hand of Death  125
Hand of Dust  125
Handful of Acorns  110
Hannya Pact  233
Harassed  62
Hardwood Club  100
Harm  130
Haruspex  227
Harvest Blade  103
Harvester of Sorrows  147
Haste  126
Haunted Forest  212
Headband of Woven Dreams  108
Headdress of the Bull  107
Heal  126
Healing Light  124
Healing Touch  126
Heart Finder Sword  100
Heat from Hell  118
Heat/Cold scale variability  86
Heavenly Choir  172, 174, 192
Heavenly Fire  131
Heavenly Fires  161
Heavenly Rivers  161
Heavenly Strike  131
Heavenly Wrath  172, 174, 192
Helheim, Dusk and Death  289
Hell Power  130
Hell Ride  230
Hell Sword  103
Hellbind Heart  130
Hellfire  130
Hellscape  233, 236, 239
Helmet of Heroes  107
Helmet of Perfection  108
Helmet of the Dawn  108
Herald Lance  100
Herd of Buffaloes  159, 161, 177, 180, 
198
Herd of Elephants  166, 185, 194
Herd of Morvarc'h  188
Herd of Unicorns  173, 191
Heretics  85
Heroic abilities  41
Hidden Flame  118
Hidden in Sand  145
Hidden in Snow  143
Hidden Underneath  145
Hide  54
Hinnom, Ashdod and Gath  91
Hinnom, Sons of the Fallen  265
Hit locations  61
Hitting mounted units  64
Holger the Head  113
Holy Avenger  131
Holy Pyre  136, 139
Holy Scourge  102
Holy Word  131
Homunculus  111
Horde from Hell  153
Horde of Skeletons  125
Horn of Storms  111
Horn of Valor  111
Horned Helmet  107
Horrible Visage  128
Horror Helmet  107
Horror Mark  124
Horror Seed  230
Host of Ganas  160, 178, 196
How forts collect resources  26
Howl  126
Huaca Headdress  108
Hunter's Knife  100
Hurricane  219
Hydra Skin Armor  106
Hydrophobia  118
I
Ice Aegis  105
Ice Helmet  107
Ice Lance  99
Ice Mist Scimitar  100
Ice Pebble Staff  102
Ice Shield  121
Ice Strike  121
Ice Sword  99
Ice Walls  220
Ignite Arrows  118
Igor Könhelm's Tome  113
Illusory Army  128
Illusory Attack  151
Illwinter  215, 216
Immaculate Fort  228
Immaculate Mounts  126
Immaculate Shield  105
Immobile Pretenders  31
Immolation  118
Immortal Pretenders  31
Imp Familiar  110
Implementor Axe  102
Imprint Souls  223
Improved Cross Breeding  230
Incinerate  118
Income  22
Increasing your dominion  83
Ind and its successors  92
Ind, Magnificent Kingdom of Exalted 
Virtue  335
Indirect Magic  74
Infernal Breeding  233, 236, 239
Infernal Circle  230
Infernal Crusade  153
Infernal Disease  230
Infernal Forces  153
Infernal Fumes  230
Infernal Prison  130
Infernal Sword  103
Infernal Tempest  153
Infiltrate  54
Initiation of combat.  49
Inner Furnace  133, 136, 139
Inner Sun  217
Inquisitor bonus  85
Instill Uprising  54
Internal Alchemy  233, 236, 239
440

[p.441]
Interrupts  75
Introduction  6
Invisibility  128
Invulnerability  125
Iron Bane  123
Iron Blizzard  136, 139
Iron Corpse Reanimation  191
Iron Darts  136, 139
Iron Dragon  145
Iron Face  108
Iron Gryphon  141
Iron Marionettes  139
Iron Pigs  145
Iron Walls  221
Iron Warriors  123
Iron Will  123
Ironskin  123
Ivory Bow  104
Ivy Crown  107
J
Jade Armor  106
Jade Knife  100
Jellyberd  103
Jinn Bottle  112
Jomon, Human Daimyos  401
Jotunheim, Iron Woods  359
Juggernaut Construction  147
Just Man's Cross  104
K
Kailasa, Rise of the Ape Kings  271
Katabasis  238
King of Banefires  147
King of Elemental Earth  145
King of Elemental Fire  141
Kithaironic Lion Pelt  105
Knife of the Damned  100
Knight's Barding  115
Krupp's Bracers  113
Ktonian Legion  191
L
Laboratories  28
Lacerating Winds  120
Lamentation  171
Land of the Ever Young  228
Lanka, Land of Demons  272
Lantern Shield  105
Launch Options  430
Lead Shield  104
Leech  130
Leeching Darkness  125
Leeching Touch  130
Legendary Spells  80
Legion of Wights  147
Legion's Demise  130
Legions of Steel  123
Lemuria, Soul Gates  380
Leprosy  225
Lesser Flame Ward  118
Lesser Thunder Ward  120
Lesser Winter Ward  121
Level bonus  78
Leviathan  147
Levitate  120
Levitate Soldiers  120
Lichcraft  225
Lictorian Guard  171
Lictorian Legion  171
Life after Death  125
Life Drain damage  67
Life for a Life  130
Lifelong Protection  111
Light of the Northern Star  124
Lightless Lantern  112
Lightning Bolt  120
Lightning Field  121
Lightning Resistance  123
Lightning Resistant Warriors  123
Lightning Rod  102
Lightning Spear  100
Lightweight Cataphract Barding  115
Lightweight Scale Mail  105
Limited legendary spell research rate  16
Limited unique artifact forging rate  16
Lion Sentinels  221
Liquid Body  121
Liquid Flames of Rhuax  133, 136, 139
Liquify  121
Living Castle  227
Living Clouds  120
Living Earth  123
Living Fire  118
Living Mercury  157, 173, 180
Living Water  121
Locust Swarms  227
Lodestone Amulet  110
Long lasting battles and Twilight  71
Lore of Legends  228
Lost Land  221
Luck  128
Lucky Coin  104
Lure of the Deep  213
Lure of the sirens  53
Lychantropos' Amulet  111
M
Mace of Eruption  100
Machaka  92
Machaka, Lion Kings  284
Machaka, Reign of Sorcerors  352
Maelstrom  209
Mage Bane  101
Maggots  126
Magic  32, 73
Magic beings and undead  70
Magic Duel  124
Magic fear effects  70
Magic gem inventory  24, 46
Magic Gems  79
Magic Items  80, 99
Magic Sites  28
Magma Bolts  123
Magma Eruption  123
Main Gauche of Parrying  100
Maintain Siege  52
Major Changes in Dominions 6  12
Man  93
Man, Tower of Avalon  315
Man, Towers of Chelms  381
Managing your magic resources  79
Manifest Vitriol  143
Manifestation  225
Manikin Reanimation  54
Manual Dominions 6  1
Manual of Water Breathing  111
Marble Armor  106
Marble Army  123
Marble Warriors  123
Marignon  93
Marignon, Conquerors of the Sea  387
Marignon, Fiery Justice  323
Marverni  93
441

[p.442]
Marverni, Time of Druids  256
Mask of Face-borrowing  108
Mass Confusion  128
Mass Flight  120
Mass Regeneration  126
Master Enslave  125
Master password  16
Master's Athame  101
Maws of the Earth  123
Maximum dominion  83
Mechanical Men  145
Mechanical Militia  210
Medallion of Vengeance  111
Meditation Sign  140
Mekone & Phlegra  93
Mekone, Brazen Giants  245
Melancholia  221
Melee attack resolution  63
Melee combat  60
Memories of Stone  195
Mend the Dead  135
Mercenaries  29
Mercury Barrel  112
Mercybrand  100
Messenger Crows  219
Meteor Shower  123
Miasma  227
Mictlan  84, 93
Mictlan, Blood and Rain  403
Mictlan, Reign of Blood  279
Mictlan, Reign of the Lawgiver  346
Midgård, Age of Men  409
Midget Masher  102
Midget's Revenge  113
Mind Blank  128
Mind Burn  124
Mind Hunt  223
Mind Vessel  235
Mindless units  70
Miraculous Cure All Elixir  111
Mirage  228
Mirage Bola  104
Mirage Crystal  112
Mirror Armor  105
Mirror Image  128
Mirror Mind  128
Mirror of Earth's Memories  232
Mirror of False Impressions  112
Mirror of Long Lost Battles  105
Mirror of Trapped Images  111
Mirror Walk  239
Missile combat  65
Mist  120
Mistform  120
Mistletoe Garland  107
Mists of Deception  128
Monolith Armor  107
Monster Boar  231, 232, 235, 238
Moon Blade  103
Moonvine Bracelet  112
Morale  69
Morale and rout  69
Morale bonuses  69
Morale check  70
Morale, magic bonus  69
Mossbody  126
Mother Oak  212
Mounted Units  64
Mounted units and magic items  64
Mounted units and morale  64
Mounts  52
Move  50
Move and Patrol  51
Movement  47
Multiple attacks  63
Multiple weapons  63
Murdering Winter  220
Muspelheim, Sons of Fire  294
N
Na'Ba and Ubar  94
Na'Ba, Queens of the Desert  331
Naiad Warriors  143
Nation Index  241
National summary  24
Nazca  94
Nazca, Kingdom of the Sun  344
Nest of Asps  126
Nest of Salamanders  118
Nether Bolt  124
Nether Darts  124
Nethgul  113
Neverending Keg of Mead  111
Nexus Gate  223
Nidavangr  94
Nidavangr, Bear, Wolf and Crow  361
Niefel Flames  122
Niefelheim, Sons of Winter  293
Nightfall  128
Nightmare Construction  191
Nightmare Masks  128
O
O'al Kan's Sceptre  101
Oaken Army  126
Oceania, Coming of the Capricorns  298
Oceania, Mermidons  367
Oceania, Pelagia, and Erytheia  94
Olm Conclave  173
Opposition  124
Oppressors Headband  107
Orb Lightning  120
Orb of Atlantis  113
Orb of Elemental Air  113
Orb of Elemental Earth  113
Orb of Elemental Fire  113
Orb of Elemental Water  113
Ordeal by Fire  208
Orders  50
Orgy  190
Other Rituals  217
Owl Quill  110
P
Pack Ferocity  126
Pack of Wolves  149
Pain Transfer  130
Pale Riders  147
Pangaea  95
Pangaea, Age of Bronze  306
Pangaea, Age of Revelry  246
Pangaea, New Era  377
Panic  126
Paralysis damage  67
Paralyze  124
Parting of the Soul  134, 137, 139
Patala, Reign of the Nagas  397
Path Boosters  116
Patrol  50
Pebble Skin Suit  107
Pelagia, Pearl Kings  296
Pelagia, Triton Kings  365
Pendant of Beauty  111
Pendant of Courage  110
442

[p.443]
Pendant of Luck  110
Percival the Pocket Knight  113
Perform Blood Sacrifice  54
Perpetual Storm  208
Personal Barkskin  126
Personal Flight  120
Personal Ironskin  123
Personal Luck  128
Personal Mistform  120
Personal Poison Resistance  126
Personal Regeneration  126
Personal Stoneskin  123
Petrify  123
Phaeacia  95
Phaeacia, Isle of the Dark Ships  354
Phlegmatia  220
Phlegra, Deformed Giants  305
Phlegra, Sleeping Giants  375
Phoenix Power  118
Phoenix Pyre  118
Physical form  31
Piconye, Legacy of the Prester King  418
Picus's Axe of Rulership  101
Piercer  104
Pillage  53
Pillar of Fire  118
Pills of Water Breathing  111
Pixie Shoes  109
Pixie Spear  100
Plague  125
Plague of Locusts  153
Playing a hotseat game  18
Playing a multiplayer game  18
Playing a network game  18
Playing the Game  18
Pocket Ship  112
Poison Arrows  126
Poison Cloud  126
Poison damage  66
Poison Darts  126
Poison Golem  147
Poison Mist  126
Poison Touch  126
Poison Ward  126
Polymorph  126
Population  22
Power of the Grave  140
Power of the Reborn King  140
Power of the Sepulchre  136
Power of the Shadelands  139
Power of the Spheres  124
Preach  53
Preaching the Word of God  84
Pretender and prophet hit points  86
Pretender death  36
Pride of Lions  149
Prison of Fire  118
Prison of Sedna  121
Probabilities in Dominions 6  13
Procas's Axe of Rulership  101
Procession of the Underworld  155, 169, 
170, 189
Profuse bleeding  66
Project Self  228
Protection from Cold  121
Protection from Fire  118
Protection from Lightning  120
Protection from Poison  126
Protection of the Grave  140
Protection of the Sepulchre  135, 136
Protection of the Shadelands  138
Protection vs global enchantments  78
Protective Winds  120
Proud Steed  126
Province attributes  21
Province Defense  29
Pull from the Grave  131
Puppet Mastery  135
Purgatory  208
Purify Blood  131
Purifying Water  131
Purple Silk Garments  105
Pyrène  95
Pyrène, Cambion Kings  422
Pyrène, Kingdom of the Bekrydes  259
Pyrène, Time of the Akelarre  325
Pyre of Catharsis  217
Pythium  95
Pythium, Emerald Empire  313
Pythium, Serpent Cult  378
Q
Quagmire  121
Queen of Elemental Air  142
Queen of Elemental Water  143
Quick Roots  135
Quicken Self  121
Quickening  121
Quickness  121
R
R'lyeh and Atlantis  96
R'lyeh, Dreamlands  428
R'lyeh, Fallen Star  371
R'lyeh, Time of Aboleths  301
Rabbit Foot Charm  109
Rage  118
Rage of the Cornered Rat  126
Ragha  95
Ragha, Dual Kingdom  391
Raging Hearts  217
Raid  53
Rain  121
Rain of Jaguars  163, 164, 183, 200, 201
Rain of Stones  123
Rain of Toads  230
Rainbow Armor  106
Raise Dead  125
Raise Skeletons  125
Ranger's Boots  109
Ranger's Cloak  105
Rat Tail  100
Raven Feast  219
Raw Hide Shield  104
Reanimate  53
Reanimate Ancestor  191
Reanimate Archers  147
Reanimation  147
Reascendance  192
Reawaken Fossil  193
Recruiting units  42
Recruitment costs  42
Recruitment Points  22
Recruitment restrictions  42
Red Dragon Scale Mail  106
Regeneration  126
Regrowth  135
Reinvigoration  130
Rejuvenate  230
Release Lord of Civilization  158, 177, 
205
Relief  126
Remnants in the Depths  211
Renaming  16
443

[p.444]
Repel  62
Rerecruiting mounted units  65
Research  80
Resist Cold  118
Resist Fire  121
Resist Lightning  123
Resist Magic  124
Resources  22
Retreating when besieged  73
Retreats  72
Return of the Past  131
Returning  124
Revive Acolyte  171
Revive Arch Bishop  171
Revive Bane  147
Revive Bane Lord  147
Revive Bishop  171
Revive Cavern Wights  157
Revive Censor  171
Revive Dusk Elder  171
Revive Grand Lemur  190
Revive Grave Consort  202
Revive King  147
Revive Lemur Acolyte  190
Revive Lemur Centurion  190
Revive Lemur Consul  190
Revive Lemur Senator  190
Revive Lemur Thaumaturg  190
Revive Lictor  171
Revive Shadow Tribune  190
Revive Spectator  171
Revive Tomb King  202
Revive Tomb Priest  202
Revive Wailing Lady  171
Revive Wights  147
Rewrite Fate  124
Rhapsody of Life  138
Rhapsody of the Dead  138
Rhuax Pact  157, 173
Riches from Beneath  210
Rider skill  64
Rigor Mortis  125
Rime Hammer  103
Rime Hauberk  106
Ring of Fire  109
Ring of Frost  109
Ring of Invisibility  112
Ring of Levitation  110
Ring of Regeneration  111
Ring of Returning  112
Ring of Sorcery  112
Ring of Tamed Lightning  109
Ring of the False Prophet  112
Ring of the Warrior  110
Ring of Warning  110
Ring of Water Breathing  110
Ring of Wizardry  112
Ritual of Five Gates  153
Ritual of Rebirth  225
Ritual of Returning  223
Rituals  76
Robe of Calius the Druid  107
Robe of Invulnerability  106
Robe of Missile Protection  105
Robe of Shadows  106
Robe of the Magi  106
Robe of the Sea  106
Rod of Death  101
Rod of the Leper King  100
Rod of the Phoenix  101
Rout  69
Rout effects  70
Royal Power  140
Royal Protection  140
Rune Smasher  100
Rus, Sons of Heaven  291
Rush of Strength  130
Rust  67
Rust Mist  123
S
Sabbath Master  130
Sabbath Slave  130
Sacred Crocodile  165, 185, 202
Sacred Wind  131
Sailors' Death  121
Salamander Silk Garments  106
Sandals of the Crane  109
Sandman's Blessing  128
Sanguine Dowsing Rod  111
Sanguine Heritage  191
Sanguinia  219
Sauromatia  96
Sauromatia, Amazon Queens  250
Scale Walls  52
Scales  34
Scapegoats  166, 195
Sceleria and Lemuria  96
Sceleria, The Reformed Empire  311
Sceptre of Authority  100
Sceptre of Corruption  101
Sceptre of Dark Regency  101
School of Sharks  121
Scorching Wind  133, 137
Score graphs  16
Scorpion Crown  108
Scouting and Scrying  30
Scrying Pool  220
Scutata Volturnus  105
Sea King's Court  143
Sea King's Goblet  112
Sea of Ice  209
Second Sight  124
Second Sun  208
Seduction  53
Seeking Arrow  219
Seith Curse  234, 237, 240
Send Aatxe  232, 235
Send Bukavac  167, 186, 203
Send Dream Horror  230
Send Horror  153
Send Lady Midday  234, 237, 240
Send Lesser Horror  153
Send Tupilak  240
Send Vodyanoy  167, 186, 203
Serenity  121
Sermon of Courage  131
Serpent Fang Arrows  126
Serpent Kryss  100
Serpent's Blessing  126
Seven Year Fever  126
Shademail Haubergeon  106
Shadow Blast  125
Shadow Bolt  125
Shadow Brand  101
Shadow Servant  147
Shadow Warriors  128
Shaman's Staff  102
Shambler Skin Armor  105
Shark Attack  121
Shatter  123
Shield destruction  61
Shield of Gleaming Gold  105
Shield of Meteoritic Iron  104
444

[p.445]
Shield of the Accursed  105
Shield of the Dawn  105
Shield of Valor  104
Shillelagh  100
Shimmering Fields  128
Shinuyama, Land of the Bakemono  340
Shock damage  67
Shock Trident  102
Shock Wave  120
Shocking Grasp  120
Shrink  126
Shroud of Bewilderment  128
Shroud of Flying Shards  123
Shroud of Splendor  128
Shroud of the Battle Saint  106
Siege Golem  145
Sieges  71
Silent Boots  109
Silver Hauberk  106
Silver Silk Garments  107
Simulacrum  228
Singing Sword  101
Skeletal Body  125
Skeletal Legion  125
Skull Mentor  111
Skull of Fire  112
Skull Staff  102
Skull Standard  102
Skull Talisman  109
Skullface  108
Sky Metal Matrix  111
Slave Collar  110
Slave Matrix  111
Slave's Heart  111
Sleep  128
Sleep Ray  128
Sleep Vines  135
Slime  121
Sling of Accuracy  104
Sling of Crystal Shards  104
Sloth of Bears  157
Slow  121
Slumber  128
Smasher  100
Smite  131
Smite Demon  131
Smokeless Flame  133, 137
Snake Bladder Stick  100
Snake Ring  109
Sneak  50
Soaring Army  121
Solar Brilliance  124
Solar Eclipse  118
Solar Rays  124
Soldiers of Steel  123
Soul Contract  110
Soul Drain  124
Soul Scales  112
Soul Slay  124
Soul Transaction  130
Soul Vortex  125
Soulstone of the Wolves  113
Sounder of Boars  157
Sow Dragon Teeth  132, 134, 135, 137, 
138, 140
Spear of the Morrigan  100
Special abilities  38
Special damage  66
Special Dominions  87
Specific orders  46
Spell Focus  111
Spell Ward  124
Spider Amulet  111
Spirit Curse  125
Spirit Helmet  108
Spirit Mask  107
Spirit Mastery  147
Spirits of the Wood  149
Squads  43
Staff of Corrosion  102
Staff of Elemental Mastery  103
Staff of Flame Focus  102
Staff of Storms  103
Standard of the Damned  103
Star Fires  124
Star of Darkness  100
Star of Heroes  100
Star of Thraldom  101
Starfire Staff  100
Starshine Skullcap  108
Starting a Game  14
Starvation  24
Steal Breath  120
Steal Sight  128
Steel Slice Warriors  123
Stellar Cascades  124
Stellar Decree  131
Stellar Focus  211
Stellar Strike  223
Stinger  100
Stone Birds  110
Stone Idol  112
Stone Sphere  111
Stoneskin  123
Storm  120
Storm Castle  52
Storm of Thorns  126
Storm Spool  111
Storm Wind  120
Storming a castle  72
Strands of Arcane Power  211
Strange Fire  137, 139
Stream of Life  126
Streams from Hades  143
Strength of Gaia  126
Strength of Giants  123
Stygian Paths  225
Stygian Rains  125
Stygian Skin  125
Stymphalian Wings  106
Sulphur Haze  118
Summer Sword  100
Summon Abysian Ancestors  193
Summon Air Elemental  120
Summon Aka-Oni  181, 198
Summon Amphiptere  142
Summon Angiri  159, 178, 196
Summon Animals  149
Summon Ao-Oni  181, 198
Summon Apsaras  159, 178, 196
Summon Araburu-kami  162
Summon Asp Turtle  143
Summon Asrapas  160, 178, 196
Summon Balam  164, 185, 201
Summon Barghests  156, 173, 191
Summon Bean Sidhe  191
Summon Bears  167
Summon Binn  158, 176
Summon Bishop Fish  143
Summon Black Dogs  156, 173, 191
Summon Bluecap  151
Summon Bog Beasts  149
Summon Calydonian Boar  149
Summon Catoblepas  143
445

[p.446]
Summon Cave Cows  143
Summon Cave Crab  145
Summon Cave Drake  145
Summon Cave Grubs  145
Summon Cave Kobolds  151
Summon Chaac  164, 185, 201
Summon Condors  183
Summon Crocodiles  149
Summon Cu Sidhe  157, 173, 191
Summon Dai Oni  181, 198
Summon Daitya  160, 178, 196
Summon Dakini  160, 178, 196
Summon Daktyl  188, 206
Summon Danavas  160, 178, 196
Summon Devala  159, 178, 196
Summon Devata  159, 178, 196
Summon Dwarf of the Four Directions  
166, 167, 168, 186, 188, 203, 204
Summon Earth Elemental  123
Summon Earthpower  123
Summon Ether Warriors  147
Summon Fall Bears  145
Summon Fay Folk  151
Summon Fay Footfolk  151
Summon Fay Knights  151
Summon Fay Prince  151
Summon Fire Ants  141
Summon Fire Drake  141
Summon Fire Elemental  118
Summon Fire Snakes  141
Summon Firebird  167, 186, 203
Summon Flame Jellies  141
Summon Flame Spirit  141
Summon Gandharvas  159, 178, 196
Summon Garudas  159, 178
Summon Ghosts  147
Summon Ghulah  158, 176
Summon Glosos  168, 188, 204
Summon Gnome  151
Summon Gozu Mezu  162, 181, 198
Summon Great Eagles  142
Summon Gryphons  142
Summon Hawk  120
Summon Hekateride  188, 206
Summon Hinn  158, 176
Summon Horned Serpents  149
Summon Hound of Twilight  155, 169, 
170, 186, 189, 206
Summon Huacas  183
Summon Ice Drake  143
Summon Ifrit  176
Summon Illearth  130
Summon Imps  130
Summon Incubus  206
Summon Jade Serpents  163, 183, 185, 
200, 201
Summon Jaguar Toads  163, 183, 185, 
200, 201
Summon Jaguars  163, 164, 183, 200, 201
Summon Jinn Warriors  176
Summon Kappa  162, 198
Summon Karasu Tengus  162, 181, 198
Summon Kenzoku  198
Summon Killer Mantis  149
Summon Kimpurushas  159, 178, 196
Summon Kinnara  159, 178, 196
Summon Kithaironic Lion  149
Summon Ko-Oni  181, 198
Summon Konoha Tengus  162, 181, 198
Summon Kuro-Oni  181, 198
Summon Kusarikkus  159, 177
Summon Lammashtas  125
Summon Leogryphs  149
Summon Lesser Air Elemental  120
Summon Lesser Earth Elemental  123
Summon Lesser Fire Elemental  118
Summon Lesser Water Elemental  121
Summon Likho  167, 186, 203
Summon Lilot  158, 166, 175, 195
Summon Mandeha  160, 178, 196
Summon Manticores  149
Summon Marid  176
Summon Maruts  159, 178, 196
Summon Mazzikim  158, 166, 175, 195
Summon Monster Fish  169, 189, 206
Summon Monster Toad  163, 183, 185, 
200, 201
Summon Monster Toads  165, 185
Summon Morrigan  156
Summon Mound Fiend  147
Summon Nagas  178
Summon Ogres  145
Summon Okami  181, 198
Summon Omukade  181
Summon Oni  181, 198
Summon Oni General  181, 198
Summon Penumbrals  173, 191
Summon Rakshasa Warriors  160, 178, 
196
Summon Rakshasas  160, 178, 196
Summon Rimvaettir  168, 188
Summon Rudra  159, 178, 196
Summon Rusalka  167, 186, 203
Summon Sacred Scorpion  164, 201
Summon Samanishada  160, 178, 196
Summon Sandhyabalas  160, 178, 196
Summon Se'irim  158, 175
Summon Sea Dogs  149
Summon Sea Lions  149
Summon Sea Serpent  143
Summon Shade Beasts  147
Summon Shades  147
Summon Shaytan  176
Summon Shedim  158, 166, 175, 195
Summon Shikome  162
Summon Si'lat  158, 176
Summon Siddha  159, 178, 196
Summon Simargl  167, 186, 203
Summon Spectral Infantry  157, 175
Summon Spectre  147
Summon Spine Frog  149
Summon Spring Hawks  142
Summon Sprites  128
Summon Storm Drake  142
Summon Storm Power  120
Summon Succubus  206
Summon Summer Lions  141
Summon Supayas  183
Summon Swamp Drake  149
Summon Telkhine  166, 169
Summon Tlaloque  163, 183, 200
Summon Ugallu  159, 177
Summon Ujigami  198
Summon Umbrals  173, 191
Summon Valkyries  134, 137, 140
Summon Vetalas  160, 178, 196
Summon Vidyadhara  159, 178, 196
Summon Water Elemental  121
Summon Water Kobold  151
Summon Water Power  121
Summon Winter Wolves  143
Summon Wyverns  142
Summon Yazatas  163, 183, 194
Summon Yetis  143
446

[p.447]
Summon Zmey  167, 186, 203
Summoning Rituals  141
Sun Slayer  103
Sunrise Barding  116
Supplies  23
Supply  25
Supply during sieges  72
Supply Usage  23
Swarm  126
Sword of Injustice  101
Sword of Justice  103
Sword of Sharpness  100
Sword of Swiftness  100
Sword of the Five Elements  100
Syllable of Death  131
T
T'ien Ch'i  96
T'ien Ch'i, Barbarian Kings  399
T'ien Ch'i, Imperial Bureaucracy  338
T'ien Ch'i, Spring and Autumn  274
Tablecloth of Marvelous Feasts  110
Tangle Thicket  126
Tangle Vines  126
Tapestry of Dreams  228
Target orders  45
Tartarian Gate  225
Taurobolium  238
Teaching Sign  139
Teleport  223
Teleport Gems  223
Teleport Item  223
Telestic Animation  147
Temper Armors  123
Temper Flesh  123
Tempering the Will  136, 139
Tempest  103
Temples  28
Terracotta Army  141
Terrain  21
Terror  125
The Aegis  105
The Ankh  113
The Ark  113
The Astral Harpoon  113
The Awakening  36
The Basics  13
The Black Book of Secrets  113
The Black Heart  112
The Black Mirror  113
The Boots of Calius the Druid  109
The Chalice  113
The Copper Arm  112
The Crown of Despair  108
The Crown of Pure Blood  108
The Death Globes  113
The Eyes of God  211
The First Anvil  113
The First Crown  108
The Flailing Hands  103
The Flying Ship  113
The Forbidden Light  113
The Gift of Kurgi  113
The Green Eye  113
The Heart of Life  111
The Heart of Quickness  112
The Horror Harmonica  113
The Interface  14
The Jade Mask  108
The Kindly Ones  208
The Looming Hell  214
The Magic Lamp  113
The Manual of Cross Breeding  113
The Map  20
The Missing Tune  113
The Oath Rod of Kurgi  103
The Origins of Nations  89
The Paths of Magical Power  73
The Pebble Pouch  104
The Pretender  30
The Protection of Geryon  113
The Quintessence Chest  114
The Ravenous Swarm  126
The Ruby Eye  113
The Schools of Magical Research  73
The Sharpest Tooth  101
The Sickle whose Crop is Pain  101
The Silver Arms  113
The Staff from the Sun  103
The Stone Sword  103
The Summit  101
The Sword of Aurgelmer  101
The Sword of Many Colors  103
The Tartarian Chains  101
The Tome of Gaia  113
The Trapped Dreams of Hruvur  113
The Void Sphere  113
The Wrath of God  211
Theft of the Sun  215
Therodos  96
Therodos, Telkhine Spectre  299
Thetis' Blessing  209
Thistle Mace  100
Thorn Spear  100
Thorn Staff  102
Thousand Year Ginseng  236
Three Red Seconds  230
Throne game settings  17
Throne settings  17
Thunder Bow  104
Thunder Fend  120
Thunder Strike  120
Thunder Ward  120
Thunder Whip  100
Thunderstorm  219
Tidal Wave  220
Time Stop  124
Tir na n'Og, Land of the Ever Young  254
Tome of High Power  113
Tome of Legends  113
Tome of the Forgotten Masons  113
Tome of the Lower Planes  113
Torpor  126
Totem Shield  105
Touch of Madness  126
Toy Sword  100
Trade Wind  219
Transformation  227
Transmute Fire  217
Treelord's Staff  103
Trident from Beyond  103
Trinities  32
Troll King's Court  145
True Sight  128
Trueshot  120
Trueshot Longbow  104
Trueshot Warriors  120
Tune of Dancing Death  133, 135, 138
Tune of Fear  133, 135, 138
Tune of Growth  133, 135, 138
Turn resolution sequence  55
Twiceborn  225
Twilight  128
Twilight Glaive  103
447

[p.448]
Twin Spear  101
Twist Fate  124
Types of spells  75
U
Ubar, Kingdom of the Unseen  267
Ulm  97
Ulm, Black Forest  383
Ulm, Enigma of Steel  258
Ulm, Forges of Ulm  321
Unconsciousness  62
Undead Mastery  126
Unending Nightmare  128
Unholy Blessing  135, 136, 138
Unholy Command  135, 136, 138
Unholy Power  135, 136, 138
Unholy Protection  135, 136, 138
Unit classes  40
Unit Inventories  46
Units  37
Unleash Imprisoned Ones  232
Unquenched Sword  101
Unraveling  124
Unrest  23, 29
Unseen Sword  100
Ur and Uruk  97
Ur, The First City  269
Uruk, City States  333
Using magic gems in combat  79
Utgård, Well of Urd  412
Utterdark  211
V
Vaettiheim, Wolf Kin Jarldom  414
Vafur Flames  217
Vajra  101
Vanarus, Land of the Chuds  357
Vanheim, Age of Vanir  288
Vanheim, Arrival of Man  356
Vanheim, Helheim, Niefelheim, 
Muspelheim, Jotunheim, Midgård, and 
Utgård  97
Veil of Perpetual Mists  228
Vengeance of the Dead  228
Vengeful Vines  135
Vengeful Water  209
Venomous Death  126
Vermin Feast  227
Vile Water  143
Vine Arrow  126
Vine Bow  104
Vine Shield  105
Vine Whip  100
Vision's Foe  104
Visions of Death  128
Voice of Apsu  220
Voice of Tiamat  220
Void Pattern Labyrinth  223
Volcanic Eruption  217
Vortex of Returning  124
Vortex of Unlife  125
W
Wailing Winds  128
Wall Shaker  111
Wand of Wild Fire  100
Warrior Illusion  128
Warriors of the Dawn  128
Watcher  142
Water Bracelet  112
Water Lens  111
Water Shield  121
Water Strike  121
Water Ward  121
Watery Death  131
Wave Breaker  103
Wave Warriors  121
Weakness  125
Weapon types  61
Weapons of Sharpness  123
Weather  72
Weavers of the Wood  234, 237
Web  126
Weightless Kite Shield  104
Weightless Scale Mail  106
Weightless Tower Shield  104
Welcome Sign  139
Well of Misery  211
Whip of Command  100
Whispers of the Wild  227
White Dragon Scale Mail  106
Wild Growth  126
Wild Hunt  213
Wildness  126
Will o' the Wisp  118
Will of the Fates  124
Wind Guide  120
Wind of Death  125
Wind Ride  219
Windcatcher Sail  111
Windrunner  120
Winds of Arcane Drought  208
Winged Helmet  107
Winged Monkeys  227
Winged Shoes  109
Winter Bringer  101
Winter Ward  121
Winter's Call  188, 204
Winter's Chill  121
Wish  223
Witches' Ointment  110
Wither Bones  125
Wizard's Tower  221
Wolven Winter  220
Wondrous Box of Monsters  113
Wooden Construction  149
Wooden Warriors  126
Word of Bewilderment  131
Word of Power  131
Word of Stone  131
Word of Thorns  131
Wound Fend Amulet  110
Woundflame  101
Wraith Crown  108
Wraith Sword  102
Wrath of Pazuzu  230
Wrath of the Ancestors  133, 134, 139
Wrath of the Sea  209
Wrathful Skies  120
Wyrmskin Boots  109
X
Xibalba  98
Xibalba, Flooded Caves  348
Xibalba, Return of the Zotz  405
Xibalba, Vigil of the Sun  280
XP: Experience points  41
Y
Yomi, Oni Kings  276
Yomi, Shinuyama and Jomon  98
Ys  98
Ys, Morgen Queens  363
448

[p.449]
Z
Ziz  147
449
