# Journal



*Designing characters and environment:*

* The Setting: Medieval fantasy setting, the architecture and zeitgiest is that of an old, stylised medieval society. However, the technology is highly magical, the society is divided into three classes.

* [The Protagonist](Main-Character.webp "This is their appearance"): In this magical world you are part of a common gu master (the middle class of people with awakened primeval powers) family. Despite your talents and projected success, you end up having a terrible talent level. However, in this era, a new age has arisen due to the invention of the "pill path". Essentially, anything and everything, although living and mythical beings are preferred, can have their essence contained in refined "pills" in which you can consume. (hence the name of the game)

* Environment: The game will revolve around a main area:
* -{The Wolf tide}-
 A bunch of wolves - a wolf tide - in your local mountain invade, because your considered cannon fodder your hired to go into the vanguard. Instead, you discover a cave with a inheritance from an deceased demonic cultivator. You can accept their inheritance and get a bunch of items, finally going to defend against the wolf tide. Crucially, while fighting on the front lines, you fall back into the demonic cave looking to secure the end of your inheritance. There, you find the demonic cultivator's final message and recording: The clan's historical records claimed their righteous ancestor heroically defeated the evil cultivator, however the recording proved the opposite - the clan shamelessly ambushed, poisoned, and backstabbed the cultivator during a peaceful trade deal. With this in mind, you fight off the last of the wolf tide and become a respected lord. 
 
 The clan mistakenly thinks you are an immense, once-in-a-century cultivation talent who was hiding his true power. Thus, the clan elders give you access to the ancient inheritance of the clan's ancestor. When he awakens, he reveals his plan. More or less, he turned himself into a zombie for several centuries, now that you are here, he waited for a genius (although you secretly have terrible talent) to steal his body using a forbidden technique, or to put it more bluntly literally eat and consume him, alongside all the ancestors other relatives (that is to say his descendents on the mountain with you). This is because once his arpeture has enough talent, then he will become an 'extreme physique' and his zombie body will naturally revert, allowing him to live and battle again, upon which he would do whatever mischief and deeds he wanted to before he started this plan. Naturally, you must defeat him, allowing yourself and the clan to be saved and becoming the undisputed lord of the mountain.

### Rationale

The Setting: This setting melds well with the strategic, text based gameplay style. It is also distinct and easily explainable in a text format to engage the players.

The Protagonist: The protagonists backstory and motivations sets up a clear gameplay loop. As the player, you are thus motivated to continue to engage in the game and have a clear goal.

The environmental progression: Clear plot progression, such that after you master the basics and defeat the waves of the wolves you get to the final boss. 


*Fin.*

# Project Evaluation & OOP Review

## 1. Implementation of Core OOP Principles
This engine was designed from the ground up to leverage rigorous Object-Oriented Programming (OOP) paradigms to build a clean, modular codebase.

* **Inheritance**: Established a robust base class hierarchy using `Actor`. General properties (`x`, `y`, `char`, `fg`, `hp`) and vital mechanics (`take_damage`, `heal`) are defined once. Specialized child classes (`Player`, `Warrior`, `Wolf`, `GreatWolf`, `WolfKing`) inherit these attributes automatically, completely removing duplicate data definitions.
* **Polymorphism (Method Overriding)**: Leveraged method overriding within the child `Player` class. While the generic `Actor.move` method handles structural tile boundary validation and grid blocking, `Player.move` overrides this path to intercept spatial collisions, trigger dialogue states, and calculate active bumper-attack modifiers before executing `super().move()`.
* **Encapsulation**: Game data configurations, map layouts, and rendering logic are cleanly compartmentalized within independent object models (`MapConfig` and `GameMap`). Individual entities maintain their own internal state pools (such as the player's dictionary-tracked `inventory`, item cursors, and custom attribute metrics like `strength` and `toxicity`).
* **Abstraction**: Hidden data layer complexities are completely masked behind clean interface methods. The player simply steps onto a coordinate cell or hits a hotkey, while the underlying engine handles complex operations—like multidimensional NumPy matrix lookups, field-of-view raycasting, and automated algorithmic AI target searches—entirely behind the scenes.

## 2. Game Progression & Loop Architecture
The application runs on a cohesive state machine that splits the narrative experience into distinct, highly functional phases:
1. **The Prologue**: Serves as a peaceful interactive environment. The player navigates their family home, engages in contextual dialogue with NPCs, and uses a portal tile to trigger a seamless transition.
2. **The Vanguard Battlefield (The Wolf Tide)**: Upon loading the wilderness, a dynamic multi-tiered wave handler takes over. It manages allied `Warrior` bots alongside custom target-tracking algorithms that battle incoming hostiles.
3. **The Combat & Economy Cycle**: Defeating hostiles creates interactable `WolfCorpse` entities to harvest stackable resources. These resources, combined with `essence` points spent at the medicine table, allow the player to forge stat-boosting pills.
4. **The Boss Finale**: Progression culminates in a multi-wave climax, challenging the player to out-damage the final `WolfKing` boss's turn-based health regeneration loop.

## 3. Utilisation of Technical Research
The architectural stability of this game heavily relies on the practical application of core industry-standard libraries:
* **`tcod` (The Roguelike Toolkit)**: Researched and integrated high-speed terminal blitting structures (`console.blit`) to layer complex graphics onto the root terminal without sacrificing frames. Utilized native field-of-view pathfinding modules (`tcod.map.compute_fov`) with infinite ranges (`radius=0`) to implement a realistic line-of-sight culling filter.
* **`NumPy` (Vectorised Data Handling)**: Leveraged fast Fortran-ordered multidimensional array slicing masks (`order="F"`) to parse raw text map layouts into coordinate arrays. This bypasses slow, nested Python `for` loops, handling walkability matrices and rendering text updates instantly in a single clock cycle.

## 4. Technical Pitfalls & Engineering Hotfixes

### Pitfall A: Volatile Indexing Crashes (`IndexError`)
* **The Issue**: When the inventory container structure was upgraded from a static string list to a dynamic dictionary engine (to track item stack counts), dropping or using the final item of a specific type caused the dictionary keys array to instantly shrink. If the player's cursor index (`inv_index`) was left hanging at the old length boundary, the next rendering loop crashed the script.
* **The Fix**: Engineered an automatic index safety-clamp layout filter at the very peak of the main gameplay loop thread. It continuously forces the tracking cursor to remain safely bounded within the current dictionary length limits (`len(items_list) - 1`) *before* any draw calls execute, completely preventing runtime crashes.

### Pitfall B: Unintended Loop State Locks
* **The Issue**: Opening the alchemical crafting screen modal layout via the `R` key caused the input handling listeners to freeze. Because the keyboard polling checks were locked within a rigid sequential chain, the engine became trapped—requiring the player to toggle their separate inventory screen on and off just to force the menu to update.
* **The Fix**: Refactored the core input matching branch to isolate the sub-menus into explicit, independent state modules. The refinement panel was given top-level priority inside the event stack, and keyboard inputs (`R`, `ESCAPE`, or step movements `W, A, S, D`) were mapped as rapid, single-frame exit commands to make the entire UI instantly responsive.

### Pitfall C: Structural Memory Reset Overwrites
* **The Issue**: A frame-reset loop error caused NPC dialogue to instantly vanish. Because the exploration loop was designed to wipe target locks and reset text panels back to the map's default description every time a movement key was registered, walking into a family member updated the text box and immediately erased it on the very same frame tick.
* **The Fix**: Re-engineered the movement validation checks to cache the player's relative spatial layout coordinates before a step runs (`old_x`, `old_y`). The text-reset handler was wrapped in a conditional guard: if a movement key is pressed but the player's physical coordinates do not actually change tiles (confirming they ran into a solid NPC), the reset gate is bypassed—locking the dialogue perfectly on screen.


# Potential sequel
* Add more story
* Add more kinds of enemies
* Add archery