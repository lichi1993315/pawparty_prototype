import pygame
import random
import math

class Cat:
    def __init__(self, config, player):
        self.config = config
        self.player = player
        self.world = player.world  # Store reference to world from player
        
        # Position (initially near player)
        self.x = player.x + 1
        self.y = player.y + 1
        
        # Stats
        self.affection = 50  # Starting affection
        self.hunger = 70     # Starting hunger (higher = less hungry)
        self.max_affection = config.cat_max_affection
        self.max_hunger = config.cat_max_hunger
        
        # Movement variables
        self.follow_distance = config.cat_follow_distance
        self.move_cooldown = 0
        self.random_movement_counter = 0
        
        # Behaviors
        self.is_sleeping = False
        self.is_playing = False
        self.current_behavior = "follow"  # follow, wander, sit, play
        
        # Skills unlocked
        self.skills = {
            "auto_track": True,      # Base skill - follows player
            "charm": False,          # Improves NPC interactions
            "pest_control": False,   # Reduces pests on farm
            "watering": False,       # Helps with watering
            "growth_boost": False,   # Boosts crop growth nearby
            "treasure_finder": False,# Finds hidden items
            "fish_helper": False,    # Improves fishing
            "intimidate": False      # Helps with enemies
        }
    
    def update(self, world, player):
        # Update hunger
        self.hunger -= self.config.cat_hunger_rate
        if self.hunger < 0:
            self.hunger = 0
            # Reduce affection if very hungry
            if random.random() < 0.1:
                self.affection = max(0, self.affection - 1)
        
        # Determine behavior
        self.choose_behavior()
        
        # Move based on behavior
        if self.move_cooldown <= 0:
            if self.current_behavior == "follow":
                self.follow_player(world)
            elif self.current_behavior == "wander":
                self.wander(world)
            elif self.current_behavior == "sit":
                pass  # Do nothing, just sit
            
            self.move_cooldown = 5  # Wait 5 frames before moving again
        else:
            self.move_cooldown -= 1
        
        # Use skills if available
        self.use_skills(world, player)
    
    def choose_behavior(self):
        # Chance to change behavior
        if random.random() < 0.01:  # 1% chance each update
            # Weighted behaviors based on hunger and affection
            behaviors = ["follow", "wander", "sit"]
            weights = [0.6, 0.3, 0.1]  # Default weights
            
            # Adjust weights based on hunger and affection
            if self.hunger < 30:  # Hungry cats are less active
                weights = [0.4, 0.3, 0.3]
            
            if self.affection > 80:  # High affection cats follow more
                weights[0] += 0.2
                weights[1] -= 0.1
                weights[2] -= 0.1
            
            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights]
            
            self.current_behavior = random.choices(behaviors, normalized_weights)[0]
    
    def follow_player(self, world):
        # Calculate direction to player
        dx = self.player.x - self.x
        dy = self.player.y - self.y
        
        # Only move if outside follow distance
        if abs(dx) > self.follow_distance or abs(dy) > self.follow_distance:
            # Move toward player
            move_x = 1 if dx > 0 else (-1 if dx < 0 else 0)
            move_y = 1 if dy > 0 else (-1 if dy < 0 else 0)
            
            # Try to move
            new_x = self.x + move_x
            new_y = self.y + move_y
            
            if world.is_walkable(new_x, new_y):
                self.x = new_x
                self.y = new_y
    
    def wander(self, world):
        # Random movement
        self.random_movement_counter += 1
        
        if self.random_movement_counter >= 10:  # Move every 10 calls
            self.random_movement_counter = 0
            
            # Random direction
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            dx, dy = random.choice(directions)
            
            new_x = self.x + dx
            new_y = self.y + dy
            
            if world.is_walkable(new_x, new_y):
                self.x = new_x
                self.y = new_y
    
    def feed(self):
        # Increase hunger when fed
        self.hunger = min(self.max_hunger, self.hunger + 30)
        
        # Increase affection a bit
        self.affection = min(self.max_affection, self.affection + 2)
        
        return True
    
    def pet(self):
        # Increase affection when petted
        self.affection = min(self.max_affection, self.affection + 5)
        
        # Check for skill unlocks based on affection milestones
        self.check_skill_unlocks()
        
        return True
    
    def play(self):
        # Play with the cat
        self.is_playing = True
        self.affection = min(self.max_affection, self.affection + 10)
        
        # Check for skill unlocks
        self.check_skill_unlocks()
        
        return True
    
    def check_skill_unlocks(self):
        # Unlock skills based on affection level
        if self.affection >= 20 and not self.skills["charm"]:
            self.skills["charm"] = True
        
        if self.affection >= 30 and not self.skills["pest_control"]:
            self.skills["pest_control"] = True
        
        if self.affection >= 40 and not self.skills["watering"]:
            self.skills["watering"] = True
        
        if self.affection >= 50 and not self.skills["growth_boost"]:
            self.skills["growth_boost"] = True
        
        if self.affection >= 60 and not self.skills["treasure_finder"]:
            self.skills["treasure_finder"] = True
        
        if self.affection >= 70 and not self.skills["fish_helper"]:
            self.skills["fish_helper"] = True
        
        if self.affection >= 80 and not self.skills["intimidate"]:
            self.skills["intimidate"] = True
    
    def use_skills(self, world, player):
        # Use cat skills based on what's unlocked
        
        # Water nearby plants
        if self.skills["watering"] and random.random() < 0.01:
            # Water a random tile nearby
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if random.random() < 0.3:
                        world.water_soil(self.x + dx, self.y + dy)
        
        # Growth boost
        if self.skills["growth_boost"] and random.random() < 0.01:
            # Boost growth of crops nearby
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    tile = world.get_tile(self.x + dx, self.y + dy)
                    if tile and tile.crop and not tile.crop.is_ready:
                        # 10% boost
                        if random.random() < 0.1:
                            tile.crop.growth_days += 0.1
        
        # Fishing helper
        if self.skills["fish_helper"] and player.fishing_active:
            player.fishing_success_chance += 0.2
    
    def draw(self, screen):
        # Get the view boundaries from world (assumed to be set during world.draw())
        world_view_x = getattr(self.player.world, 'view_x_start', 0)
        world_view_y = getattr(self.player.world, 'view_y_start', 0)
        
        # Calculate screen position
        screen_x = (self.x - world_view_x) * self.config.tile_size
        screen_y = (self.y - world_view_y) * self.config.tile_size
        
        # Only draw if the cat is within the view
        view_width = self.config.view_width
        view_height = self.config.view_height
        if (0 <= self.x - world_view_x < view_width and 
            0 <= self.y - world_view_y < view_height):
            # Create and render the cat character
            from game.util import get_font
            font = get_font(is_ascii=True, size=self.config.tile_size)
            symbol = self.config.ascii_tiles["cat"]
            text_surface = font.render(symbol, True, self.config.colors["cat"])
            screen.blit(text_surface, (screen_x, screen_y)) 