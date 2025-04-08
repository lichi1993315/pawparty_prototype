import random
import pygame

class Tile:
    def __init__(self, type, x, y):
        self.type = type
        self.x = x
        self.y = y
        self.tilled = False
        self.watered = False
        self.crop = None
        self.growth_stage = 0
        self.growth_time = 0
        self.has_forage = False
        self.forage_type = None

class Crop:
    def __init__(self, type, growth_time):
        self.type = type
        self.growth_time = growth_time
        self.growth_days = 0
        self.watered_today = False
        self.is_ready = False
    
    def grow(self):
        if self.watered_today:
            self.growth_days += 1
            if self.growth_days >= self.growth_time:
                self.is_ready = True
        self.watered_today = False  # Reset for the new day

class World:
    def __init__(self, config):
        self.config = config
        self.width = config.map_width
        self.height = config.map_height
        self.tiles = [[None for _ in range(self.height)] for _ in range(self.width)]
        
        # Areas
        self.farm_area = (10, 10, 20, 15)  # x, y, width, height
        self.foraging_areas = []
        
        # Home position - define this BEFORE calling generate_world
        self.home_position = (12, 12)
        
        # Now generate the world
        self.generate_world()
        
        # Create foraging areas
        for _ in range(20):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.tiles[x][y].type == "grass":
                forage_types = list(self.config.forage_types.keys())
                chosen_type = random.choice(forage_types)
                self.tiles[x][y].has_forage = True
                self.tiles[x][y].forage_type = chosen_type
                self.foraging_areas.append((x, y))
    
    def generate_world(self):
        # Generate a basic world with grass, water, and other features
        for x in range(self.width):
            for y in range(self.height):
                # Generate mostly grass
                tile_type = "grass"
                
                # Create a river
                if 35 <= x <= 38:
                    tile_type = "water"
                
                # Create multiple lakes
                lakes = [
                    (45, 15, 5),  # x, y, radius
                    (15, 30, 4),
                    (25, 8, 3),
                    (8, 20, 3)
                ]
                
                for lake_x, lake_y, radius in lakes:
                    if (x - lake_x) ** 2 + (y - lake_y) ** 2 <= radius ** 2:
                        tile_type = "water"
                        break
                
                # Create some trees and rocks
                if tile_type == "grass" and random.random() < 0.05:
                    tile_type = "tree"
                elif tile_type == "grass" and random.random() < 0.03:
                    tile_type = "rock"
                
                # Create farmland
                if 10 <= x < 30 and 10 <= y < 25:
                    if random.random() < 0.7:
                        tile_type = "untilled_soil"
                
                self.tiles[x][y] = Tile(tile_type, x, y)
        
        # Place house
        house_x, house_y = self.home_position
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                x, y = house_x + dx, house_y + dy
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.tiles[x][y].type = "house"
    
    def get_tile(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[x][y]
        return None
    
    def is_walkable(self, x, y):
        tile = self.get_tile(x, y)
        if tile is None:
            return False
        
        # Add more walkable tile types, including house and any other non-obstacle tiles
        walkable_types = ["grass", "untilled_soil", "tilled_soil", "watered_soil", "house"]
        
        # Block only solid obstacles like water, trees, and rocks
        non_walkable_types = ["water", "tree", "rock"]
        
        return tile.type not in non_walkable_types
    
    def till_soil(self, x, y):
        tile = self.get_tile(x, y)
        if tile and tile.type == "untilled_soil":
            tile.type = "tilled_soil"
            tile.tilled = True
            return True
        return False
    
    def water_soil(self, x, y):
        tile = self.get_tile(x, y)
        if tile and tile.type == "tilled_soil":
            tile.type = "watered_soil"
            tile.watered = True
            if tile.crop:
                tile.crop.watered_today = True
            return True
        return False
    
    def plant_crop(self, x, y, crop_type):
        tile = self.get_tile(x, y)
        if tile and (tile.type == "tilled_soil" or tile.type == "watered_soil") and not tile.crop:
            growth_time = self.config.crop_types[crop_type]["growth_time"]
            tile.crop = Crop(crop_type, growth_time)
            return True
        return False
    
    def harvest_crop(self, x, y):
        tile = self.get_tile(x, y)
        if tile and tile.crop and tile.crop.is_ready:
            crop_type = tile.crop.type
            value = self.config.crop_types[crop_type]["value"]
            tile.crop = None
            tile.type = "tilled_soil"  # Reset to tilled state
            tile.tilled = True
            tile.watered = False
            return crop_type, value
        return None, 0
    
    def collect_forage(self, x, y):
        tile = self.get_tile(x, y)
        if tile and tile.has_forage:
            forage_type = tile.forage_type
            value = self.config.forage_types[forage_type]["value"]
            tile.has_forage = False
            tile.forage_type = None
            if (x, y) in self.foraging_areas:
                self.foraging_areas.remove((x, y))
            return forage_type, value
        return None, 0
    
    def start_fishing(self, x, y):
        """检查是否可以在指定位置钓鱼
        现在任何水域都可以钓鱼，不再需要特定的钓鱼点
        """
        # 检查玩家周围是否有水
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                check_x = x + dx
                check_y = y + dy
                tile = self.get_tile(check_x, check_y)
                if tile and tile.type == "water":
                    return True
        return False
    
    def catch_fish(self, difficulty=1.0):
        # Simple fishing minigame simulation
        # Difficulty is from 0.0 to 1.0
        # Returns fish_type, value
        
        if random.random() > difficulty:
            fish_types = list(self.config.fish_types.keys())
            weights = [1.0 / self.config.fish_types[ft]["difficulty"] for ft in fish_types]
            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights]
            
            fish_type = random.choices(fish_types, normalized_weights)[0]
            value = self.config.fish_types[fish_type]["value"]
            return fish_type, value
        
        return None, 0
    
    def update(self, time_system):
        # Grow crops
        for x in range(self.width):
            for y in range(self.height):
                tile = self.tiles[x][y]
                if tile.crop:
                    tile.crop.watered_today = tile.watered
    
    def update_day(self):
        # Called when a new day starts
        # Grow crops
        for x in range(self.width):
            for y in range(self.height):
                tile = self.tiles[x][y]
                if tile.crop and tile.watered:
                    tile.crop.grow()
                
                # Reset watered state
                if tile.watered:
                    tile.watered = False
                    if tile.type == "watered_soil":
                        tile.type = "tilled_soil"
        
        # Randomly add new forage items
        while len(self.foraging_areas) < 20:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.tiles[x][y].type == "grass" and not self.tiles[x][y].has_forage:
                forage_types = list(self.config.forage_types.keys())
                chosen_type = random.choice(forage_types)
                self.tiles[x][y].has_forage = True
                self.tiles[x][y].forage_type = chosen_type
                self.foraging_areas.append((x, y))
    
    def draw(self, screen, player):
        # Calculate view boundaries
        view_x_start = max(0, player.x - self.config.view_width // 2)
        view_y_start = max(0, player.y - self.config.view_height // 2)
        view_x_end = min(self.width, view_x_start + self.config.view_width)
        view_y_end = min(self.height, view_y_start + self.config.view_height)
        
        tile_size = self.config.tile_size
        
        # 在类外部只导入一次get_font，不要在每次draw时导入
        font = self.config.ascii_font
        if font is None:
            from game.util import get_font
            font = get_font(is_ascii=True, size=tile_size)
            self.config.ascii_font = font  # 存储在config中重复使用
        
        # Store these values as attributes so player and cat classes can use them
        self.view_x_start = view_x_start
        self.view_y_start = view_y_start
        
        # Draw visible tiles
        for x in range(view_x_start, view_x_end):
            for y in range(view_y_start, view_y_end):
                # 跳过玩家所在位置
                if x == player.x and y == player.y:
                    continue
                    
                tile = self.tiles[x][y]
                # Calculate screen position
                screen_x = (x - view_x_start) * tile_size
                screen_y = (y - view_y_start) * tile_size
                
                # Get the appropriate ASCII character for this tile
                tile_symbol = self.get_tile_symbol(tile)
                
                # Get the appropriate color for this tile
                tile_color = self.get_tile_color(tile)
                
                # Draw the tile using ASCII art
                text_surface = font.render(tile_symbol, True, tile_color)
                screen.blit(text_surface, (screen_x, screen_y))
    
    def get_tile_symbol(self, tile):
        """获取瓦片的ASCII符号"""
        char = self.config.ascii_tiles["grass"]  # Default
        
        if tile.type == "water":
            char = self.config.ascii_tiles["water"]
        elif tile.type == "untilled_soil":
            char = self.config.ascii_tiles["untilled_soil"]
        elif tile.type == "tilled_soil":
            char = self.config.ascii_tiles["tilled_soil"]
        elif tile.type == "watered_soil":
            char = self.config.ascii_tiles["watered_soil"]
        elif tile.type == "tree":
            char = self.config.ascii_tiles["tree"]
        elif tile.type == "rock":
            char = self.config.ascii_tiles["rock"]
        elif tile.type == "house":
            char = self.config.ascii_tiles["house"]
        
        # Forage items
        if tile.has_forage:
            char = self.config.ascii_tiles["forage"]
        
        # Crops
        if tile.crop:
            if tile.crop.is_ready:
                char = self.config.ascii_tiles["crop_ready"]
            else:
                # Calculate growth stage (0-3)
                growth_pct = tile.crop.growth_days / tile.crop.growth_time
                if growth_pct < 0.33:
                    char = self.config.ascii_tiles["crop_stage_1"]
                elif growth_pct < 0.66:
                    char = self.config.ascii_tiles["crop_stage_2"]
                else:
                    char = self.config.ascii_tiles["crop_stage_3"]
        
        return char
    
    def get_tile_color(self, tile):
        """获取瓦片的颜色"""
        color = self.config.colors["grass"]  # Default
        
        if tile.type == "water":
            color = self.config.colors["water"]
        elif tile.type in ["untilled_soil", "tilled_soil", "watered_soil"]:
            color = self.config.colors["soil"]
        elif tile.type == "tree":
            color = self.config.colors["tree"]
        elif tile.type == "rock":
            color = self.config.colors["rock"]
        elif tile.type == "house":
            color = self.config.colors["house"]
        
        # Forage items
        if tile.has_forage:
            color = self.config.colors["forage"]
        
        # Crops
        if tile.crop:
            color = self.config.colors["crop"]
        
        return color
    
    def has_adjacent_land(self, x, y):
        """检查水域周围是否有可站立的陆地"""
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                    
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < self.width and 0 <= new_y < self.height:
                    tile = self.tiles[new_x][new_y]
                    if tile.type in ["grass", "untilled_soil", "tilled_soil", "watered_soil"]:
                        return True
        return False 