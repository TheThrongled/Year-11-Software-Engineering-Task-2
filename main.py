import tcod
import numpy as np

class TileType:
    def __init__(self, char, fg, walkable, transparent, teleporter=False, location=None):
        self.char = char
        self.fg = fg
        self.walkable = walkable
        self.transparent = transparent
        self.teleporter = teleporter
        self.location = location

class Actor:
    def __init__(self, x, y, char, fg, name, hp, entities_list=None, dialogue=None):
        self.x = x
        self.y = y
        self.char = char
        self.fg = fg
        self.name =name
        self.hp = hp
        self.max_hp = hp
        self.dialogue = f"{name}: {dialogue}" if dialogue is not None else f"{name}: placeholder"

        if entities_list is not None:
            entities_list.append(self)

    def move(self, dx: int, dy: int, game_map):
    
            new_x = self.x + dx
            new_y = self.y + dy
    
            if 0 <= new_x < game_map.screen_width and 0 <= new_y < game_map.screen_height:
                for entity in game_map.entities:
                    if entity != self and entity.x == new_x and entity.y == new_y:
                        return
                if game_map.walkable[new_x, new_y]:
                    self.x = new_x
                    self.y = new_y

                

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

class Player(Actor):
    def __init__(self, x, y, entities_list=None):
        super().__init__(x, y, "@", (255, 255, 255), "Player", 30, entities_list)
        self.essence = 100
        self.toxicity = 0
        self.inventory = {}
        self.inv_index = 0
        self.inv_open = False
        self.refine_open = False
        self.weapon_equipped = False
        self.strength = 0

    def heal_essence(self, amount):
            # Safely cap your essence at its maximum pool threshold of 100
            self.essence = min(100, self.essence + amount)

    def increase_max_hp(self, amount):
        # Permanently raise your maximum health threshold cap
        self.max_hp += amount
        # Instantly heal for that amount so your current HP grows with it
        self.hp += amount


    def move(self, dx: int, dy: int, game_map):
        new_x = self.x + dx
        new_y = self.y + dy

        for entity in game_map.entities:
            if entity != self and entity.x == new_x and entity.y == new_y:
                global active_dialogue, context_entity, skipped_reset
                active_dialogue = entity.dialogue
                context_entity = entity
                skipped_reset = True

                if isinstance(entity, Wolf):
                    base_damage = 10 if self.weapon_equipped else 2
                    total_damage = base_damage + self.strength
                    entity.take_damage(total_damage)
                    active_dialogue = f"You strike the Wolf for {total_damage} DMG!"
                    
                    if entity.hp <= 0:
                        game_map.entities.remove(entity)
                        WolfCorpse(entity.x, entity.y, game_map.entities)
                        active_dialogue = "The wolf falls! A corpse remains."
                return

        super().move(dx, dy, game_map)

class WeaponRack(Actor):
    def __init__(self, x, y, entities_list=None):
        super().__init__(x, y, "T", (150, 110, 75), "Weapons Rack", 1, entities_list, "(T)ake spear?")
        self.has_spear = True # Tracks whether the rack still holds a weapon asset


class MedicineTable(Actor):
    def __init__(self, x, y, entities_list=None):
        super().__init__(x, y, "&", (100, 200, 150), "Medicine Table", 1, entities_list, "(R)efine?")

        
class WolfCorpse(Actor):
    def __init__(self, x, y, entities_list=None):
        super().__init__(x, y, "%", (140, 140, 140), "Wolf Corpse", 1, entities_list, "(T)ake?")

class Wolf(Actor):
    def __init__(self, x, y, entities_list=None):
        super().__init__(x, y, "w", (255, 50, 50), "Wolf", 20, entities_list, "Grrrr")
        self.target = None

class GreatWolf(Wolf):
    def __init__(self, x, y, entities_list=None):
        # Massive 'W', more health (50 HP), hits for 5 DMG
        Actor.__init__(x, y, "W", (255, 100, 100), "Great Wolf", 50, entities_list, "GROOOAR!")
        self.target = None

class WolfKing(Wolf):
    def __init__(self, x, y, entities_list=None):
        # Boss 'K', supreme health (100 HP), hits for 5 DMG
        Actor.__init__(x, y, "K", (255, 215, 0), "Wolf King", 100, entities_list, "AWOOOOO!")
        self.target = None


class Warrior(Actor):
    def __init__(self, x, y, name, entities_list=None):
        super().__init__(x, y, str(name), (200, 200, 200), f"Warrior {name}", 9999, entities_list, f"Stand firm!")
        self.target = None


class MapConfig:
    def __init__(self, file_path, legend_dict, area_name, default_dialogue):
        self.file_path = file_path
        self.legend_dict = legend_dict
        self.area_name = area_name
        self.default_dialogue = default_dialogue



class GameMap:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.entities = []

        self.player = Player(23, 12, self.entities)
        self.dad = Actor(21, 11, "P", (50, 150, 255), "Father", 150, self.entities, "Son, you must prove our family's worth. Hehehe.")
        self.mom = Actor(25, 11, "M", (255, 100, 180), "Mother", 100, self.entities, "Theres not much a trash talent like you can do!")
        self.elder = Actor(23, 9, "E", (200, 180, 100), "Clan Elder", 300, self.entities, "Child, the wolf tide is here. You have been recruited as a 'special conscript', now go.")
        
        

        self.console = tcod.console.Console(screen_width, screen_height, order="F")
        self.walkable = np.zeros((screen_width, screen_height), dtype=bool, order="F")
        self.transparent = np.zeros((screen_width, screen_height), dtype=bool, order="F")

        self.current_wave = 1


    def load_from_file(self, config: MapConfig, default_tile: TileType):
        with open(config.file_path, "r") as file_handle:
            rows = [line.rstrip('\n') for line in file_handle.readlines()]

        char_matrix = np.array([list(row) for row in rows], dtype="U1").T

        self.console.clear()
        self.walkable.fill(False)
        self.transparent.fill(False)

        for symbol, tile_rule in config.legend_dict.items():
            match_mask = (char_matrix == symbol)
            
            self.console.rgb["ch"][match_mask] = ord(tile_rule.char)
            self.console.rgb["fg"][match_mask] = tile_rule.fg
            self.walkable[match_mask] = tile_rule.walkable
            self.transparent[match_mask] = tile_rule.transparent

        self.current_char_matrix = char_matrix

    def render(self, root_console: tcod.console.Console, offset_y: int, area_title: str, dialogue: str, inv_msg):
        root_console.draw_rect(x=0, y=0, width=self.screen_width, height=1, ch=ord(' '), bg=(20, 20, 30))
        root_console.print(x=2, y=0, string=f"=== {area_title} ===", fg=(255, 215, 0))
        
        if self.player.inv_open:
            root_console.print(x=55, y=0, string="[INVENTORY ACTIVE]", fg=(50, 255, 100))
        elif len(self.player.inventory) > 1:
            root_console.print(x=55, y=0, string="Check (I)nventory", fg=(220, 200, 100))

        self.console.blit(dest=root_console, dest_x=0, dest_y=offset_y)

        fov_map = tcod.map.compute_fov(self.transparent, pov=(self.player.x, self.player.y), radius=0, light_walls=True, algorithm=tcod.FOV_BASIC)
        for x in range(self.screen_width):
            for y in range(self.screen_height):
                if not fov_map[x, y]:
                    root_console.rgb["ch"][x, y + offset_y] = ord(' ')

        for entity in self.entities:
            if fov_map[entity.x, entity.y]:
                root_console.print(x=entity.x, y=entity.y + offset_y, string=entity.char, fg=entity.fg)

                # 5. RENDER BOTTOM HUD PANEL COMPONENT
        hud_top_y = self.screen_height + offset_y
        root_console.draw_rect(x=0, y=hud_top_y, width=self.screen_width, height=5, ch=ord(' '), bg=(15, 15, 20))
        for x in range(self.screen_width):
            root_console.print(x=x, y=hud_top_y, string="─", fg=(50, 50, 60))

        root_console.print(x=2, y=hud_top_y + 1, string=f"HEALTH:  {self.player.hp}/{self.player.max_hp}", fg=(255, 50, 50))
        root_console.print(x=2, y=hud_top_y + 2, string=f"ESSENCE: {self.player.essence}", fg=(50, 150, 255))
        root_console.print(x=2, y=hud_top_y + 3, string=f"TOXICITY:{self.player.toxicity}", fg=(50, 255, 100))

        for h in range(1, 5):
            root_console.print(x=25, y=hud_top_y + h, string="│", fg=(50, 50, 60))

        # ALCHEMICAL REFINEMENT VIEW SCREEN MODE
        if self.player.refine_open:
            root_console.print(x=28, y=hud_top_y + 1, string="ALCHEMICAL REFINEMENT MENU:", fg=(200, 100, 255))
            root_console.print(x=28, y=hud_top_y + 2, string="(1) Weak Pill: 3 Souls + 50 Essence", fg=(240, 240, 240))
            root_console.print(x=28, y=hud_top_y + 3, string="(2) Strong Pill: 10 Souls + 100 Essence", fg=(240, 240, 240))
            
        # PLAYER INVENTORY VIEW SCREEN MODE
        elif self.player.inv_open:
            root_console.print(x=28, y=hud_top_y + 1, string="PLAYER INVENTORY MANAGER:", fg=(50, 255, 100))
            if inv_msg:
                root_console.print(x=28, y=hud_top_y + 2, string=inv_msg, fg=(50, 255, 100))
            elif self.player.inventory:
                # Convert active item tracking back into an index string list layout array matching counts
                items_list = list(self.player.inventory.keys())
                current_item = items_list[self.player.inv_index]
                item_count = self.player.inventory[current_item]
                
                # FIXED: Stack counts display format (xN) cleanly added here!
                root_console.print(x=28, y=hud_top_y + 2, string=f"< {current_item} (x{item_count}) >", fg=(255, 255, 255))
                root_console.print(x=28, y=hud_top_y + 3, string="[SPACE] to Use/Equip", fg=(150, 150, 150))
            else:
                root_console.print(x=28, y=hud_top_y + 2, string="Empty Bag Space", fg=(100, 100, 100))
        else:
            root_console.print(x=28, y=hud_top_y + 1, string="DIALOGUE:", fg=(200, 180, 140))
            root_console.print(x=28, y=hud_top_y + 2, string=dialogue, fg=(240, 240, 240), width=50)

    def check_tile_triggers(self, current_config: MapConfig, default_tile: TileType) -> MapConfig:
        if not hasattr(self, "current_char_matrix"):
            return current_config
            
 
        if 0 <= self.player.x < self.current_char_matrix.shape[0] and 0 <= self.player.y < self.current_char_matrix.shape[1]:
            player_symbol = self.current_char_matrix[self.player.x, self.player.y]
            current_tile_object = current_config.legend_dict.get(player_symbol)

            if current_tile_object and current_tile_object.teleporter:
                print(f"LOG: Portal Triggered! Traveling straight to file path...")

                
                next_area = current_tile_object.location
                self.entities = [self.player]
                
                self.load_from_file(next_area, default_tile)

                if next_area.area_name == "VANGUARD":
                    self.spawn_vanguard_battlefield()
                
                self.player.x = 24
                self.player.y = 13

                global active_dialogue
                active_dialogue = next_area.default_dialogue

                return next_area 
                
        return current_config

    def spawn_vanguard_battlefield(self):
        import random

        if self.current_wave == 1:
            self.rack = WeaponRack(77, 7, self.entities)      # Armor Stand 'T'
            self.table = MedicineTable(77, 11, self.entities)

        self.entities = [e for e in self.entities if e == self.player or isinstance(e, WeaponRack) or isinstance(e, MedicineTable)]
        for i in range(6):
            Warrior(x=random.randint(40, 55), y=random.randint(5, 15), name=i, entities_list=self.entities)

        global active_dialogue
        active_dialogue = f"WAVE {self.current_wave} HAS BEGUN!"

        if self.current_wave in (1, 2):
            for _ in range(6):
                Wolf(x=random.randint(5, 20), y=random.randint(3, 18), entities_list=self.entities)
            
            for _ in range(2):
                w = Wolf(x=random.randint(5, 20), y=random.randint(3, 18), entities_list=self.entities)
                w.target = self.player # Heatseeker tags player specifically

        elif self.current_wave == 3:
            # Wave 3: Spawns 4 Regular Wolves and 2 massive Great Wolves ('W')
            for _ in range(4):
                Wolf(x=random.randint(5, 20), y=random.randint(3, 18), entities_list=self.entities)
            for _ in range(2):
                w = GreatWolf(x=random.randint(5, 20), y=random.randint(3, 18), entities_list=self.entities)
                w.target = self.player

        elif self.current_wave == 4:
            # Wave 4: Final Boss Fight! Spawns 2 Regular Wolves and the Wolf King ('K')
            for _ in range(2):
                Wolf(x=random.randint(5, 20), y=random.randint(3, 18), entities_list=self.entities)
            wk = WolfKing(x=random.randint(5, 12), y=random.randint(5, 15), entities_list=self.entities)
            wk.target = self.player
            active_dialogue = "THE WOLF KING HAS AWOKEN! STAND FIRM!"

    def process_ai_turns(self):
        import random
        global active_dialogue
        wolves = [e for e in self.entities if isinstance(e, Wolf)]
        warriors = [e for e in self.entities if isinstance(e, Warrior)]

        for warrior in warriors:
            if not warrior.target or warrior.target not in self.entities:
                if wolves:
                    warrior.target = min(wolves, key=lambda w: abs(w.x - warrior.x) + abs(w.y - warrior.y))
            
            if warrior.target:
                dx = np.sign(warrior.target.x - warrior.x)
                dy = np.sign(warrior.target.y - warrior.y)
                if abs(warrior.x - warrior.target.x) <= 1 and abs(warrior.y - warrior.target.y) <= 1:
                    if random.random() < 0.2:  
                        warrior.target.take_damage(2)
                        if warrior.target.hp <= 0 and warrior.target in self.entities:
                            self.entities.remove(warrior.target)
                            WolfCorpse(warrior.target.x, warrior.target.y, self.entities)
                else:
                    warrior.move(dx, 0, self) or warrior.move(0, dy, self)

                # AI Loop Rules for Wolves / Bosses
        for wolf in wolves:
            # NEW: If this entity is the Wolf King, execute his turn-based health regeneration pass
            if isinstance(wolf, WolfKing):
                wolf.heal(5)

            if wolf.target is None:
                if warriors:
                    wolf.target = min(warriors, key=lambda wa: abs(wa.x - wolf.x) + abs(wa.y - wolf.y))
            
            if wolf.target:
                dx = np.sign(wolf.target.x - wolf.x)
                dy = np.sign(wolf.target.y - wolf.y)
                
                if abs(wolf.x - wolf.target.x) <= 1 and abs(wolf.y - wolf.target.y) <= 1:
                    # FIXED: Wolf bosses strike for higher baseline values
                    base_bite = 5 if isinstance(wolf, (GreatWolf, WolfKing)) else 2
                    
                    if wolf.target == self.player:
                        
                        total_damage = base_bite + self.player.toxicity
                        self.player.take_damage(total_damage)
                        active_dialogue = f"A hostile target mauled you for {total_damage} DMG! (Toxicity cleared!)"
                        self.player.toxicity = 0
                        
                        if self.player.hp <= 0:
                            print("GAME OVER - YOU DIED")
                            raise SystemExit()
                    else:
                        wolf.target.take_damage(base_bite)
                else:
                    wolf.move(dx, 0, self) or wolf.move(0, dy, self)

        # FIXED: WAVE MONITOR HOOK SYSTEM
        # Re-check if any hostile creature types are still standing on map coordinates
                # FIXED: Only check for wave progression if we are actually out in the VANGUARD area!
        # (This prevents it from triggering inside your family home during the PROLOGUE)
        if hasattr(self, "current_char_matrix") and len(wolves) == 0:
            # We can check if any warriors exist on map to confirm we are on the battlefield
            active_hostiles = [e for e in self.entities if isinstance(e, (Wolf, GreatWolf, WolfKing))]
            active_warriors = [e for e in self.entities if isinstance(e, Warrior)]
            
            # Only progress waves if there are active warriors present but no hostiles left
            if active_warriors and not active_hostiles:
                if self.current_wave < 4:
                    self.current_wave += 1
                    self.spawn_vanguard_battlefield()
                else:
                    active_dialogue = "VICTORY! The Wolf Tide has been completely routed! You have saved the Clan!"








def main() -> None:
    map_width = 80
    map_height = 21

    header_height = 1
    hud_height = 5
    screen_height = map_height + header_height + hud_height

    global active_dialogue
    global context_entity

    context_entity = None

    active_inv_msg = ""


    tileset = tcod.tileset.load_tilesheet(
        "dejavu16x16_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
    )

    vanguard_legend = {
        ' ': TileType(' ', (40, 40, 40), walkable=False, transparent=True),
        '.': TileType('.', (50, 60, 50), walkable=True, transparent=True),
        '#': TileType('#', (139, 69, 19), walkable=False, transparent=True),
        '^': TileType('^', (34, 139, 34), walkable=False, transparent=False),  
        '~': TileType('~', (139, 90, 43), walkable=False, transparent=True),   
        'o': TileType('o', (139, 90, 43), walkable=False, transparent=True),   
        '+': TileType('+', (139, 69, 19), walkable=True, transparent=True),   
        '`': TileType('`', (220, 200, 100), walkable=True, transparent=True),  
        '-': TileType('-', (139, 69, 19), walkable=True, transparent=True),    
        '_': TileType('_', (120, 90, 60), walkable=False, transparent=True),   
        'T': TileType('T', (150, 110, 75), walkable=False, transparent=True),  
        '&': TileType('&', (100, 200, 150), walkable=False, transparent=True),
        '(': TileType('(', (230, 115, 0), walkable=False, transparent=True),
    }

    vanguard_area = MapConfig("maps/map-1.txt", vanguard_legend, "VANGUARD", "You entered the frontlines. Stay alert.")
    
    house_legend = {
        ' ': TileType(' ', (40, 40, 40), walkable=False, transparent=True),
        '.': TileType('.', (40, 40, 40), walkable=True, transparent=True),
        '#': TileType('#', (120, 120, 120), walkable=False, transparent=True),
        '+': TileType('+', (139, 69, 19), walkable=True, transparent=True),
        '│': TileType('│', (80, 80, 80), walkable=False, transparent=True),
        'h': TileType('h', (160, 120, 90), walkable=False, transparent=True),
        'H': TileType('H', (200, 100, 50), walkable=False, transparent=True),
        '═': TileType('═', (120, 90, 60), walkable=False, transparent=True),
        '-': TileType('-', (80, 80, 80), walkable=True, transparent=True),
        '_': TileType('_', (120, 90, 60), walkable=False, transparent=True),
        '`': TileType('`', (220, 200, 100), walkable=True, transparent=True),
        '*': TileType('*', (100, 100, 100), walkable=False, transparent=True),
        ',': TileType(',', (60, 60, 60), walkable=False, transparent=True),
        '0': TileType('0', (140, 140, 140), walkable=False, transparent=True),
        '~': TileType('~', (139, 90, 43), walkable=False, transparent=True),
        '(': TileType('(', (230, 115, 0), walkable=False, transparent=True),
        '=': TileType('=', (150, 110, 75), walkable=True, transparent=True),
        '>': TileType('>', (150, 110, 75), walkable=True, transparent=True, teleporter=True, location=vanguard_area),


    }
    house_area = MapConfig("maps/map-0.txt", house_legend, "PROLOGUE", "You awaken in your clan home. Speak with your family members...")

    game_map = GameMap(map_width, map_height)
    game_map.load_from_file(house_area, house_legend[' '])

    current_area = house_area
    active_dialogue = current_area.default_dialogue

    active_inv_msg = ""

    with tcod.context.new(
        columns=map_width,
        rows=screen_height,
        title="DNR: The Golden Age of War",
        vsync=True,
        tileset=tileset,
    ) as context:
        
        root_console = tcod.console.Console(map_width, screen_height, order="F")

        while True:
            # FIXED: Extract dictionary keys as a valid list array first!
            items_list = list(game_map.player.inventory.keys())
            if items_list:
                # Snap your selector cursor index back to the valid item list size constraints
                game_map.player.inv_index = max(0, min(game_map.player.inv_index, len(items_list) - 1))
            else:
                # Clear pointer if your bag goes completely empty
                game_map.player.inv_index = 0

            game_map.render(root_console, offset_y=1, area_title=current_area.area_name, dialogue=active_dialogue, inv_msg=active_inv_msg)            
            context.present(root_console)
            root_console.clear()

            for event in tcod.event.wait():
                if isinstance(event, tcod.event.Quit):
                    raise SystemExit()
                
                elif isinstance(event, tcod.event.KeyDown):
                    moved = False
                    
                     # 1. TOGGLE INVENTORY LAYOUT
                    if event.sym == tcod.event.KeySym.i:
                        # Close refinement screen if you pop open the bag panel
                        game_map.player.refine_open = False
                        game_map.player.inv_open = not game_map.player.inv_open
                        active_inv_msg = ""
                    
                    # NEW: REFINEMENT SELECTION HANDLER (Sit right at top level)
                                        # 2. ALCHEMICAL REFINEMENT MENU MODAL PANEL SCREEN CONTROLS
                    elif game_map.player.refine_open:
                        # FIXED: Pressing R again, ESCAPE, or a movement key drops you out instantly
                        if event.sym in (tcod.event.KeySym.r, tcod.event.KeySym.ESCAPE, tcod.event.KeySym.w, tcod.event.KeySym.s, tcod.event.KeySym.a, tcod.event.KeySym.d):
                            game_map.player.refine_open = False
                            active_dialogue = current_area.default_dialogue
                        
                        elif event.sym == tcod.event.KeySym.N1: # Recipe 1
                            souls = game_map.player.inventory.get("Wolf Soul", 0)
                            if souls >= 3 and game_map.player.essence >= 50:
                                game_map.player.inventory["Wolf Soul"] -= 3
                                if game_map.player.inventory["Wolf Soul"] == 0:
                                    del game_map.player.inventory["Wolf Soul"]
                                game_map.player.essence -= 50
                                game_map.player.inventory["Weak Pill"] = game_map.player.inventory.get("Weak Pill", 0) + 1
                                active_dialogue = "Success! Created Weak Pill alchemical asset!"
                            else:
                                active_dialogue = "Not enough materials for that recipe!"
                                
                        elif event.sym == tcod.event.KeySym.N2: # Recipe 2
                            souls = game_map.player.inventory.get("Wolf Soul", 0)
                            if souls >= 10 and game_map.player.essence >= 100:
                                game_map.player.inventory["Wolf Soul"] -= 10
                                if game_map.player.inventory["Wolf Soul"] == 0:
                                    del game_map.player.inventory["Wolf Soul"]
                                game_map.player.essence -= 100
                                game_map.player.inventory["Strong Pill"] = game_map.player.inventory.get("Strong Pill", 0) + 1
                                active_dialogue = "Success! Created Strong Pill alchemical asset!"
                            else:
                                active_dialogue = "Not enough materials for that recipe!"

                                        # 2. NAVIGATE ACTIVE INVENTORY VIA COMMA AND PERIOD KEYS
                    elif game_map.player.inv_open:
                        items_list = list(game_map.player.inventory.keys())
                        
                        if event.sym == tcod.event.KeySym.COMMA:
                            if items_list:
                                game_map.player.inv_index = (game_map.player.inv_index - 1) % len(items_list)
                                active_inv_msg = ""
                        elif event.sym == tcod.event.KeySym.PERIOD:
                            if items_list:
                                game_map.player.inv_index = (game_map.player.inv_index + 1) % len(items_list)
                                active_inv_msg = ""
                                
                        elif event.sym == tcod.event.KeySym.SPACE:
                            if items_list:
                                active_item = items_list[game_map.player.inv_index]
                                if active_inv_msg:
                                    active_inv_msg = ""
                                else:
                                    if active_item == "Weak Pill":
                                        game_map.player.inventory["Weak Pill"] -= 1
                                        if game_map.player.inventory["Weak Pill"] == 0:
                                            del game_map.player.inventory["Weak Pill"]
                                        game_map.player.strength += 10
                                        game_map.player.toxicity += 10
                                        game_map.player.increase_max_hp(10)

                                        active_dialogue = "Consumed Weak Pill. Gained 10 Strength. + 10 MAX HP Toxicity +10!"
                                        active_inv_msg = "Consumed Weak Pill! (SPACE) to return"
                                        
                                    elif active_item == "Strong Pill":
                                        game_map.player.inventory["Strong Pill"] -= 1
                                        if game_map.player.inventory["Strong Pill"] == 0:
                                            del game_map.player.inventory["Strong Pill"]
                                        game_map.player.strength += 40
                                        game_map.player.toxicity += 25
                                        game_map.player.increase_max_hp(30)
                                        active_dialogue = "Consumed Strong Pill. Gained 40 Strength. + 30 MAX HP Toxicity +25!"
                                        active_inv_msg = "Consumed Strong Pill! (SPACE) to return"

                                    elif active_item == "Wolf Soul":
                                        game_map.player.inventory["Wolf Soul"] -= 1
                                        if game_map.player.inventory["Wolf Soul"] == 0:
                                            del game_map.player.inventory["Wolf Soul"]
                                        # Heals the player for 15 HP using your Actor.heal method
                                        game_map.player.heal(15)
                                        game_map.player.heal_essence(50) 
                                        active_dialogue = "Utilized Wolf Soul. Absorbed essence to heal 15 HP!"
                                        active_inv_msg = "Utilized Wolf Soul! (SPACE) to return"
                                        
                                    elif active_item == "Wooden Spear":
                                        game_map.player.weapon_equipped = not game_map.player.weapon_equipped
                                        status = "Equipped" if game_map.player.weapon_equipped else "Unequipped"
                                        active_dialogue = f"You {status} your Wooden Spear!"
                                        active_inv_msg = f"{status} Wooden Spear! (SPACE) to return"
                                        
                                    else:
                                        active_dialogue = f"You utilized item: {active_item}"
                                        active_inv_msg = f"Utilized {active_item}! (SPACE) to return"

                                


                    

                                
                    # 3. BASE OVERWORLD MOVEMENT AND HOTKEYS
                    else:
                        # Capture position memory before running movement rules
                        old_x, old_y = game_map.player.x, game_map.player.y
                        
                        if event.sym == tcod.event.KeySym.w:
                            game_map.player.move(dx=0, dy=-1, game_map=game_map)
                            moved = True
                        elif event.sym == tcod.event.KeySym.s:
                            game_map.player.move(dx=0, dy=1, game_map=game_map)
                            moved = True
                        elif event.sym == tcod.event.KeySym.a:
                            game_map.player.move(dx=-1, dy=0, game_map=game_map)
                            moved = True
                        elif event.sym == tcod.event.KeySym.d:
                            game_map.player.move(dx=1, dy=0, game_map=game_map)
                            moved = True
                        
                                                # OBJECT-ORIENTED PROPERTY HOOKS
                        elif event.sym == tcod.event.KeySym.t: 
                            if context_entity and isinstance(context_entity, WeaponRack):
                                if context_entity.has_spear:
                                    # Add to stack dictionary cleanly
                                    game_map.player.inventory["Wooden Spear"] = game_map.player.inventory.get("Wooden Spear", 0) + 1
                                    context_entity.has_spear = False
                                    context_entity.dialogue = "You have already taken a spear"
                                    active_dialogue = "Obtained Wooden Spear from the weapon stand!"
                                else:
                                    active_dialogue = "You have already taken a spear."
                                    
                            elif context_entity and isinstance(context_entity, WolfCorpse):
                                # Tracks stack dictionary count increments for your harvested souls
                                game_map.player.inventory["Wolf Soul"] = game_map.player.inventory.get("Wolf Soul", 0) + 1
                                game_map.entities.remove(context_entity)
                                context_entity = None
                                active_dialogue = "Harvested Wolf Soul from the corpse!"
                                
                        elif event.sym == tcod.event.KeySym.r: 
                            if context_entity and isinstance(context_entity, MedicineTable):
                                # FIXED: Opens your alchemical menu modal panel screen cleanly on click!
                                game_map.player.refine_open = True
                                active_dialogue = "Accessing refinement table workspace formulas..."
                            else:
                                active_dialogue = "You are not near a refinement table."
                                    
                        elif event.sym == tcod.event.KeySym.ESCAPE:
                            raise SystemExit()

                        # CLEAN CONTEXT CHECK: Only wipe text if player successfully moved to a new cell
                        if moved and (game_map.player.x != old_x or game_map.player.y != old_y):
                            context_entity = None
                            active_dialogue = current_area.default_dialogue

                    # 4. RESOLVE GAME ENGINE TICKS
                    if moved:
                        current_area = game_map.check_tile_triggers(current_area, current_area.legend_dict[' '])
                        game_map.process_ai_turns()


if __name__ == "__main__":
    main()

