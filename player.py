import pygame
import random

class Player:
    def __init__(self, config, world):
        self.config = config
        self.world = world  # Store reference to world
        self.x = world.home_position[0]
        self.y = world.home_position[1]
        self.home_position = world.home_position
        self.energy = config.max_energy
        self.money = 500  # Starting money
        
        self.inventory = {
            "turnip_seeds": 5,
            "potato_seeds": 3,
            "tomato_seeds": 2,
            "cat_food": 10
        }
        
        self.fishing_active = False
        self.fishing_progress = 0
        self.fishing_success_chance = 0.7  # Base chance of catching a fish
        
        self.selected_seed = "turnip_seeds"
        
        # Visual representation
        self.symbol = config.ascii_tiles["player"]
        self.color = config.colors["player"]
    
    def move(self, dx, dy, world):
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Debug output
        print(f"Trying to move from ({self.x}, {self.y}) to ({new_x}, {new_y})")
        
        # Check if the destination is walkable
        walkable = world.is_walkable(new_x, new_y)
        
        # 如果不可通行，获取障碍物类型
        obstacle_type = None
        if not walkable:
            tile = world.get_tile(new_x, new_y)
            if tile:
                obstacle_type = tile.type
                print(f"Obstacle encountered: {obstacle_type}")
            else:
                obstacle_type = "边界"
                print("Obstacle encountered: map boundary")
        
        print(f"Destination walkable: {walkable}")
        
        if walkable:
            self.x = new_x
            self.y = new_y
            
            # Consume energy for walking
            self.consume_energy("walking")
            
            # Cancel fishing if active
            if self.fishing_active:
                self.fishing_active = False
                self.fishing_progress = 0
            
            return True
        else:
            # 返回障碍物信息，以便在UI中显示
            return (False, obstacle_type)
    
    def consume_energy(self, action):
        energy_cost = self.config.energy_consumption.get(action, 0)
        self.energy = max(0, self.energy - energy_cost)
    
    def energy_tick(self):
        # Natural energy drain over time
        self.energy = max(0, self.energy - 0.01)
    
    def sleep(self):
        self.energy = self.config.max_energy
    
    def at_home(self):
        # Check if player is at or near their home
        return abs(self.x - self.home_position[0]) <= 1 and abs(self.y - self.home_position[1]) <= 1
    
    def use_tool(self, tool, world):
        if tool is None:
            return False
        
        result = False
        
        if tool == "hoe":
            result = self.use_hoe(world)
        elif tool == "watering_can":
            result = self.use_watering_can(world)
        elif tool == "seeds":
            result = self.plant_seeds(world)
        elif tool == "fishing_rod":
            result = self.use_fishing_rod(world)
        
        return result
    
    def use_hoe(self, world):
        # Till the soil in front of the player
        if self.energy >= self.config.energy_consumption["hoe"]:
            if world.till_soil(self.x, self.y):
                self.consume_energy("hoe")
                return True
        return False
    
    def use_watering_can(self, world):
        # Water the soil in front of the player
        if self.energy >= self.config.energy_consumption["watering_can"]:
            if world.water_soil(self.x, self.y):
                self.consume_energy("watering_can")
                return True
        return False
    
    def plant_seeds(self, world):
        # Plant seeds in the tilled soil
        if self.energy >= self.config.energy_consumption["seeds"]:
            # Get the crop type from the seed
            if self.selected_seed not in self.inventory or self.inventory[self.selected_seed] <= 0:
                return False
            
            crop_type = self.selected_seed.split("_")[0]  # e.g., "turnip_seeds" -> "turnip"
            
            if world.plant_crop(self.x, self.y, crop_type):
                self.consume_energy("seeds")
                self.inventory[self.selected_seed] -= 1
                return True
        return False
    
    def harvest(self, world):
        # Harvest a crop if it's ready
        if self.energy >= self.config.energy_consumption["harvest"]:
            crop_type, value = world.harvest_crop(self.x, self.y)
            if crop_type:
                self.consume_energy("harvest")
                
                # Add to inventory
                if crop_type in self.inventory:
                    self.inventory[crop_type] += 1
                else:
                    self.inventory[crop_type] = 1
                
                self.money += value
                return True
        return False
    
    def collect_forage(self, world):
        # Collect forageable items
        if self.energy >= self.config.energy_consumption["gathering"]:
            forage_type, value = world.collect_forage(self.x, self.y)
            if forage_type:
                self.consume_energy("gathering")
                
                # Add to inventory
                if forage_type in self.inventory:
                    self.inventory[forage_type] += 1
                else:
                    self.inventory[forage_type] = 1
                
                self.money += value
                return True
        return False
    
    def use_fishing_rod(self, world):
        # Start/continue fishing
        if not self.fishing_active:
            # Try to start fishing
            if world.start_fishing(self.x, self.y):
                if self.energy >= self.config.energy_consumption["fishing"]:
                    self.fishing_active = True
                    self.fishing_progress = 0
                    return True
        else:
            # Continue fishing
            self.fishing_progress += 1
            
            # Consume energy
            self.consume_energy("fishing")
            
            # Check for success
            if self.fishing_progress >= 30:  # After 30 ticks
                self.fishing_active = False
                self.fishing_progress = 0
                
                # Determine if player caught something
                fish_type, value = world.catch_fish(difficulty=0.3)
                if fish_type:
                    # Add to inventory
                    if fish_type in self.inventory:
                        self.inventory[fish_type] += 1
                    else:
                        self.inventory[fish_type] = 1
                    
                    self.money += value
                    return True
        
        return False
    
    def interact(self, world, cat=None):
        # Try to interact with objects/NPCs in front of the player
        
        # Try to harvest crops
        if self.harvest(world):
            return True
        
        # Try to collect forage
        if self.collect_forage(world):
            return True
        
        # Pet interaction (if cat is nearby)
        if cat and abs(cat.x - self.x) <= 1 and abs(cat.y - self.y) <= 1:
            cat.pet()
            return True
        
        return False
    
    def draw(self, screen):
        # Get the view boundaries from world
        view_x_start = self.world.view_x_start
        view_y_start = self.world.view_y_start
        
        # Calculate screen position
        screen_x = (self.x - view_x_start) * self.config.tile_size
        screen_y = (self.y - view_y_start) * self.config.tile_size
        
        # Create and render the player character
        pygame.font.init()
        default_font = pygame.font.get_default_font()
        font = pygame.font.Font(default_font, self.config.tile_size)
        text_surface = font.render(self.symbol, True, self.color)
        screen.blit(text_surface, (screen_x, screen_y))
        
        # Also draw a little indicator for which way the player is facing
        # This is useful for determining which tile the player will interact with
        if self.fishing_active:
            # Draw fishing animation - use simple ASCII instead of emoji
            fishing_text = ">"
            fishing_surface = font.render(fishing_text, True, (255, 255, 255))
            screen.blit(fishing_surface, (screen_x + self.config.tile_size, screen_y)) 