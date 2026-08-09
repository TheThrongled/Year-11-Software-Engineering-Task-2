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
    def __init__(self, x, y, char, fg, name, hp, entities_list=None):
        self.x = x
        self.y = y
        self.char = char
        self.fg = fg
        self.name =name
        self.hp = hp
        self.max_hp = hp

        if entities_list is not None:
            entities_list.append(self)

    def move(self, dx: int, dy: int, game_map):
    
            new_x = self.x + dx
            new_y = self.y + dy
    
            if 0 <= new_x < game_map.screen_width and 0 <= new_y < game_map.screen_height:
                if game_map.walkable[new_x, new_y]:
                    self.x = new_x
                    self.y = new_y

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

class Player(Actor):
    def __init__(self, x, y, entities_list=None):
        super().__init__(x, y, "@", (255, 255, 255), "Player", 100, entities_list)
        self.essence = 100
        self.toxicity = 0


class MapConfig:
    def __init__(self, file_path, legend_dict):
        self.file_path = file_path
        self.legend_dict = legend_dict



class GameMap:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height

        self.entities = []

        self.player = Player(23, 12, self.entities)
        self.dad = Actor(22, 11, "P", (50, 150, 255), "Father", 150, self.entities)
        self.mom = Actor(26, 11, "M", (255, 100, 180), "Mother", 100, self.entities)
        self.elder = Actor(23, 9, "E", (200, 180, 100), "Clan Elder", 300, self.entities)
        
        

        self.console = tcod.console.Console(screen_width, screen_height, order="F")
        self.walkable = np.zeros((screen_width, screen_height), dtype=bool, order="F")
        self.transparent = np.zeros((screen_width, screen_height), dtype=bool, order="F")


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

    def render(self, root_console: tcod.console.Console):
        self.console.blit(dest=root_console, dest_x=0, dest_y=0)

        fov_map = tcod.map.compute_fov(
            transparency=self.transparent,
            pov=(self.player.x, self.player.y),
            radius=0,
            light_walls=True,
            algorithm=tcod.FOV_BASIC
        )

        root_console.rgb["ch"][~fov_map] = ord(' ')

        for entity in self.entities:
            if fov_map[entity.x, entity.y]:
                root_console.print(x=entity.x, y=entity.y, string=entity.char, fg=entity.fg)

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
                
                self.player.x = 24
                self.player.y = 13
                return next_area 
                
        return current_config






def main() -> None:
    map_width = 80
    map_height = 21

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

    vanguard_area = MapConfig("maps/map-1.txt", vanguard_legend)
    
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
    house_area = MapConfig("maps/map-0.txt", house_legend)

    game_map = GameMap(map_width, map_height)
    game_map.load_from_file(house_area, house_legend[' '])

    current_area = house_area

    with tcod.context.new(
        columns=map_width,
        rows=map_height,
        title="DNR: The Golden Age of War",
        vsync=True,
        tileset=tileset,

    ) as context:
        
        root_console = tcod.console.Console(map_width, map_height, order="F")

        while True:
            game_map.render(root_console)
            
            context.present(root_console)
            
            root_console.clear()

            for event in tcod.event.wait():
                if isinstance(event, tcod.event.Quit):
                    raise SystemExit()
                
                elif isinstance(event, tcod.event.KeyDown):
                    moved = False
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
                    elif event.sym == tcod.event.KeySym.ESCAPE:
                        raise SystemExit()

                    if moved:
                        current_area = game_map.check_tile_triggers(current_area, current_area.legend_dict[' '])


if __name__ == "__main__":
    main()


    
