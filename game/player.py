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
        return False
    
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
        # 自动检测前方物体并使用合适的工具
        
        # 确定玩家面前的位置（根据朝向）
        front_positions = [
            (self.x, self.y-1),  # 上
            (self.x, self.y+1),  # 下
            (self.x-1, self.y),  # 左
            (self.x+1, self.y)   # 右
        ]
        
        # 尝试每个可能的位置
        for front_x, front_y in front_positions:
            # 检查是否超出地图边界
            if front_x < 0 or front_x >= world.width or front_y < 0 or front_y >= world.height:
                continue
            
            # 获取前方物体
            front_tile = world.get_tile(front_x, front_y)
            if not front_tile:
                continue
                
            # 检查物体类型并执行对应操作
            
            # 1. 水域 - 使用钓鱼竿
            if front_tile.type == "water":
                if self.energy >= self.config.energy_consumption["fishing"]:
                    # 设置前往水边的位置
                    self.x, self.y = self.get_adjacent_position(front_x, front_y)
                    # 使用钓鱼竿
                    if self.use_fishing_rod(world):
                        return True, "fishing"
                    return False, "water"
            
            # 2. 未耕作的土地 - 使用锄头
            elif front_tile.type == "grass" and not front_tile.tilled:
                if self.energy >= self.config.energy_consumption["hoe"]:
                    # 设置玩家位置
                    self.x, self.y = self.get_adjacent_position(front_x, front_y)
                    # 使用锄头
                    if self.use_hoe(world):
                        return True, "tilling"
            
            # 3. 已耕作但未浇水的土地 - 使用浇水壶
            elif front_tile.tilled and not front_tile.watered and not front_tile.crop:
                if self.energy >= self.config.energy_consumption["watering_can"]:
                    # 设置玩家位置
                    self.x, self.y = self.get_adjacent_position(front_x, front_y)
                    # 使用浇水壶
                    if self.use_watering_can(world):
                        return True, "watering"
            
            # 4. 已耕作且已浇水的土地 - 种植种子
            elif front_tile.tilled and front_tile.watered and not front_tile.crop:
                seeds_available = False
                for item in self.inventory.keys():
                    if item.endswith("_seeds") and self.inventory[item] > 0:
                        self.selected_seed = item
                        seeds_available = True
                        break
                
                if seeds_available and self.energy >= self.config.energy_consumption["seeds"]:
                    # 设置玩家位置
                    self.x, self.y = self.get_adjacent_position(front_x, front_y)
                    # 种植种子
                    if self.plant_seeds(world):
                        return True, "planting"
            
            # 5. 成熟的作物 - 收获
            elif front_tile.crop and front_tile.crop.is_ready:
                if self.energy >= self.config.energy_consumption["harvest"]:
                    # 设置玩家位置
                    self.x, self.y = self.get_adjacent_position(front_x, front_y)
                    # 收获作物
                    if self.harvest(world):
                        return True, "harvest"
            
            # 6. 可采集的物品
            elif front_tile.has_forage:
                if self.energy >= self.config.energy_consumption["gathering"]:
                    # 设置玩家位置
                    self.x, self.y = self.get_adjacent_position(front_x, front_y)
                    # 采集物品
                    if self.collect_forage(world):
                        return True, "forage"
            
            # 7. 其他障碍物
            elif not world.is_walkable(front_x, front_y):
                # 确定障碍物类型
                obstacle_type = "未知"
                if front_tile.type == "water":
                    obstacle_type = "water"
                elif front_tile.type == "tree":
                    obstacle_type = "tree"
                elif front_tile.type == "rock":
                    obstacle_type = "rock"
                
                return True, obstacle_type
        
        # 与猫互动 (如果猫在附近)
        if cat and abs(cat.x - self.x) <= 1 and abs(cat.y - self.y) <= 1:
            cat.pet()
            return True, "cat"
        
        return False, None
    
    def get_adjacent_position(self, target_x, target_y):
        """获取与目标相邻的可行走位置"""
        # 计算相对位置
        dx = target_x - self.x
        dy = target_y - self.y
        
        # 如果已经相邻，则不需要移动
        if abs(dx) <= 1 and abs(dy) <= 1:
            return self.x, self.y
        
        # 尝试移动到最近的相邻位置
        directions = [
            (target_x-1, target_y), (target_x+1, target_y),
            (target_x, target_y-1), (target_x, target_y+1)
        ]
        
        for nx, ny in directions:
            if self.world.is_walkable(nx, ny):
                return nx, ny
        
        # 如果没有找到可行走位置，则返回当前位置
        return self.x, self.y
    
    def draw(self, screen):
        # Get the view boundaries from world
        view_x_start = self.world.view_x_start
        view_y_start = self.world.view_y_start
        
        # Calculate screen position
        screen_x = (self.x - view_x_start) * self.config.tile_size
        screen_y = (self.y - view_y_start) * self.config.tile_size
        
        # Create and render the player character
        from game.util import get_font
        font = get_font(is_ascii=True, size=self.config.tile_size)
        text_surface = font.render(self.symbol, True, self.color)
        screen.blit(text_surface, (screen_x, screen_y))
        
        # Also draw a little indicator for which way the player is facing
        # This is useful for determining which tile the player will interact with
        if self.fishing_active:
            # Draw fishing animation - use simple ASCII instead of emoji
            fishing_text = ">"
            fishing_surface = font.render(fishing_text, True, (255, 255, 255))
            screen.blit(fishing_surface, (screen_x + self.config.tile_size, screen_y)) 