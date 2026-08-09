# Structure Chart

📁 Year-11-Software-Engineering-Task-2/
│
├── 📄 main.py (Main Execution Script)
│   │
│   ├── 🛠️ Data Framework Classes
│   │   ├── TileType (Stores characters, foreground rgb, walkability, transparency)
│   │   └── MapConfig (Stores file path tracks, area title, default logs)
│   │
│   ├── 🎭 Polymorphic Actor Models (OOP Engine)
│   │   ├── Actor (Base Class: movement loops, health tracking, take_damage, heal)
│   │   │   ├── Player (Child: inventory dicts, stats, overridden move/bumper attack)
│   │   │   ├── Warrior (Child: allied combat bots, automated nearest-target tracker)
│   │   │   ├── Wolf / GreatWolf / WolfKing (Children: hostiles, boss AI pathing, regen)
│   │   │   └── Props: WeaponRack / MedicineTable / WolfCorpse (Stationary interaction items)
│   │
│   └── ⚙️ Core Operational Engine Loops
│       ├── GameMap Classes
│       │   ├── load_from_file() (Loads character txt files via NumPy matrix filters)
│       │   ├── spawn_vanguard_battlefield() (Handles 4-wave progressive tactical triggers)
│       │   ├── process_ai_turns() (Runs wolf biting damage mechanics + toxicity modifiers)
│       │   └── render() (Blits maps, updates infinite FOV culling, partitions HUD rows)
│       │
│       └── main() Execution Thread
│           ├── Setup (Instantiates screen grids, tilesets, configs)
│           └── while True Loop (Listens for KeySyms: i, t, r, comma, period, space, w, a, s, d)
│
└── 📁 maps/
    ├── 🗺️ map-0.txt (Prologue Home Map: Player, Mom, Dad, Clan Elder setup space)
    └── 🗺️ map-1.txt (Vanguard Warzone Map: Portals, tree grids, combat fields)
