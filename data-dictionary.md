# Data Dictionary


| Variable / Property | Data Type | Scope / Class | Description | Example Value |
| :--- | :--- | :--- | :--- | :--- |
| `inventory` | `Dictionary` | `Player` | Stores player items as keys and their stack counts as values. Prevents duplicated slots. | `{"Wolf Soul": 3, "Weak Pill": 1}` |
| `inv_index` | `Integer` | `Player` | Tracks the selector cursor index location when flipping through the item bag pool. | `0` |
| `inv_open` | `Boolean` | `Player` | State toggle flag. `True` locks map movement and opens the scrolling bottom bag panel. | `True` / `False` |
| `refine_open` | `Boolean` | `Player` | State toggle flag. `True` locks map movement and displays the alchemical crafting recipe sub-menu. | `True` / `False` |
| `weapon_equipped`| `Boolean` | `Player` | Tracks active weapon state. Hitting `SPACE` on a spear toggles this to scale bumper attack output. | `True` / `False` |
| `hp` / `max_hp` | `Integer` | `Actor` | Tracks current and maximum health parameters. Triggers a clean game exit loop if `hp <= 0`. | `30` / `50` |
| `essence` | `Integer` | `Player` | Alchemical mana resource consumed at the medicine table to forge pills. Clamped safely between `0` and `100`. | `100` |
| `toxicity` | `Integer` | `Player` | High-risk poison accumulator. Spikes when eating pills; adds directly to the next incoming wolf bite damage total. | `10` |
| `strength` | `Integer` | `Player` | Permanent attribute bonus gained from pills. Automatically updates and stacks onto base bumper damage formulas. | `30` |
| `current_wave` | `Integer` | `GameMap` | Progressive battlefield tracker state. Increments sequentially from `1` to `4` once a wave is fully cleared. | `1` |
| `walkable` | `NumPy Array` | `GameMap` | A 2D grid matrix mask of booleans (`order="F"`) tracking which coordinates block or permit pathing. | `True` (Floor) / `False` (Wall) |
| `transparent` | `NumPy Array` | `GameMap` | A 2D grid matrix mask of booleans (`order="F"`) telling the infinite FOV raycaster which coordinates block sight. | `True` (Grass) / `False` (Tree) |
| `active_dialogue` | `String` | `Global` / `main` | The overarching logging text sequence string displayed in the panel box layout. | `"WAVE 3 HAS BEGUN!"` |
| `active_inv_msg` | `String` | `Local` / `main` | A temporary alert notification string displayed inside the bag interface menu upon item consumption. | `"Equipped Wooden Spear! (SPACE) to return"` |
