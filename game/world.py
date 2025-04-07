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
        self.is_fish_spot = False

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
        self.fishing_spots = []
        self.foraging_areas = []
        
        # Home position - define this BEFORE calling generate_world
        self.home_position = (12, 12)
        
        # Now generate the world
        self.generate_world()
        
        # Create fishing spots (in water areas)
        for _ in range(5):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            if self.tiles[x][y].type == "water":
                self.tiles[x][y].is_fish_spot = True
                self.fishing_spots.append((x, y))
        
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
                
                # Create a lake
                lake_center_x, lake_center_y = 45, 15
                lake_radius = 5
                if (x - lake_center_x) ** 2 + (y - lake_center_y) ** 2 <= lake_radius ** 2:
                    tile_type = "water"
                
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
        tile = self.get_tile(x, y)
        if tile and tile.is_fish_spot:
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
        # 使用支持ASCII字符的字体
        from game.util import get_font
        font = get_font(is_ascii=True, size=tile_size)
        
        # Store these values as attributes so player and cat classes can use them
        self.view_x_start = view_x_start
        self.view_y_start = view_y_start
        
        # Draw visible tiles
        for x in range(view_x_start, view_x_end):
            for y in range(view_y_start, view_y_end):
                # Skip drawing the tile if it's the player's position
                if x == player.x and y == player.y:
                    continue
                
                screen_x = (x - view_x_start) * tile_size
                screen_y = (y - view_y_start) * tile_size
                
                tile = self.tiles[x][y]
                
                # Determine the character to display
                char = self.config.ascii_tiles["grass"]  # Default
                color = self.config.colors["grass"]
                
                if tile.type == "water":
                    char = self.config.ascii_tiles["water"]
                    color = self.config.colors["water"]
                elif tile.type == "untilled_soil":
                    char = self.config.ascii_tiles["untilled_soil"]
                    color = self.config.colors["soil"]
                elif tile.type == "tilled_soil":
                    char = self.config.ascii_tiles["tilled_soil"]
                    color = self.config.colors["soil"]
                elif tile.type == "watered_soil":
                    char = self.config.ascii_tiles["watered_soil"]
                    color = self.config.colors["soil"]
                elif tile.type == "tree":
                    char = self.config.ascii_tiles["tree"]
                    color = self.config.colors["tree"]
                elif tile.type == "rock":
                    char = self.config.ascii_tiles["rock"]
                    color = self.config.colors["rock"]
                elif tile.type == "house":
                    char = self.config.ascii_tiles["house"]
                    color = self.config.colors["house"]
                
                # Fish spots
                if tile.is_fish_spot:
                    char = self.config.ascii_tiles["fish_spot"]
                    color = self.config.colors["fish_spot"]
                
                # Forage items
                if tile.has_forage:
                    char = self.config.ascii_tiles["forage"]
                    color = self.config.colors["forage"]
                
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
                    color = self.config.colors["crop"]
                
                # Draw the character
                text_surface = font.render(char, True, color)
                screen.blit(text_surface, (screen_x, screen_y)) 