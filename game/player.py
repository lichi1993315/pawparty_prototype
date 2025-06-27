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
        
        # 钓鱼状态
        self.fishing_active = False
        self.fishing_start_time = 0
        self.fish_bite_time = 0  # 鱼上钩的时间
        self.waiting_for_fish = False  # 是否在等待鱼上钩
        self.fish_on_hook = False  # 是否有鱼上钩
        self.hook_response_time = 2000  # 钓到鱼的响应时间（毫秒）
        self.fish_escape_time = 0  # 鱼逃走的时间
        
        # 钓鱼小游戏状态
        self.fishing_minigame_active = False
        self.fish_stamina = 100  # 鱼的耐力
        self.fish_max_stamina = 100
        self.fish_direction = 0  # 鱼的移动方向 (0=上, 1=右, 2=下, 3=左)
        self.fish_direction_change_time = 0
        self.tension = 50  # 鱼线张力 (0-100)
        self.reel_power = 0  # 收杆力度 (0-100)
        self.reel_power_direction = 1  # 力度条移动方向
        self.perfect_zone_start = 40  # 完美收杆区域开始
        self.perfect_zone_end = 60   # 完美收杆区域结束
        self.minigame_timer = 0
        self.max_minigame_time = 10000  # 小游戏最大时间10秒
        self.fish_struggle_timer = 0
        
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
                self.reset_fishing()
            
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
        """使用钓鱼竿"""
        if not self.fishing_active:
            # Try to start fishing
            if world.start_fishing(self.x, self.y):
                if self.energy >= self.config.energy_consumption["fishing"]:
                    self.fishing_active = True
                    self.waiting_for_fish = True
                    self.fish_on_hook = False
                    current_time = pygame.time.get_ticks()
                    self.fishing_start_time = current_time
                    # 随机2-6秒后鱼上钩
                    self.fish_bite_time = current_time + random.randint(2000, 6000)
                    # 消耗能量
                    self.consume_energy("fishing")
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
    
    def update_fishing(self):
        """更新钓鱼状态"""
        if not self.fishing_active:
            return
        
        current_time = pygame.time.get_ticks()
        
        # 检查是否到了鱼上钩的时间
        if self.waiting_for_fish and current_time >= self.fish_bite_time:
            self.fish_on_hook = True
            self.waiting_for_fish = False
            self.fish_escape_time = current_time + self.hook_response_time
            return "fish_bite"  # 返回鱼上钩的信息
        
        # 如果钓鱼小游戏激活，更新小游戏状态
        if self.fishing_minigame_active:
            return self.update_fishing_minigame()
        
        # 检查鱼是否逃走
        if self.fish_on_hook and current_time >= self.fish_escape_time:
            self.reset_fishing()
            return "fish_escape"  # 返回鱼逃走的信息
        
        return None 
    
    def try_catch_fish(self):
        """尝试钓鱼"""
        if self.fish_on_hook and not self.fishing_minigame_active:
            # 开始钓鱼小游戏
            self.start_fishing_minigame()
            return ("minigame_start", None, 0)
        return (None, None, 0)
    
    def start_fishing_minigame(self):
        """开始钓鱼小游戏"""
        self.fishing_minigame_active = True
        self.fish_stamina = 100
        self.fish_max_stamina = 100
        self.fish_direction = random.randint(0, 3)
        self.fish_direction_change_time = pygame.time.get_ticks() + random.randint(1000, 3000)
        self.tension = 50
        self.reel_power = 0
        self.reel_power_direction = 1
        self.minigame_timer = pygame.time.get_ticks()
        self.fish_struggle_timer = pygame.time.get_ticks()
        
        # 根据鱼的类型调整难度
        fish_types = list(self.config.fish_types.keys())
        # 简单随机选择一种鱼类型来确定难度
        selected_fish = random.choice(fish_types)
        difficulty = self.config.fish_types[selected_fish]["difficulty"]
        
        # 调整完美区域大小和鱼的耐力
        zone_size = max(10, 30 - difficulty * 4)  # 难度越高，完美区域越小
        self.perfect_zone_start = 50 - zone_size // 2
        self.perfect_zone_end = 50 + zone_size // 2
        self.fish_max_stamina = 60 + difficulty * 20  # 难度越高，鱼越强壮
        self.fish_stamina = self.fish_max_stamina
    
    def update_fishing_minigame(self):
        """更新钓鱼小游戏状态"""
        current_time = pygame.time.get_ticks()
        
        # 检查小游戏是否超时
        if current_time - self.minigame_timer > self.max_minigame_time:
            self.reset_fishing()
            return "fish_escape"
        
        # 更新力度条
        self.reel_power += self.reel_power_direction * 2
        if self.reel_power >= 100:
            self.reel_power = 100
            self.reel_power_direction = -1
        elif self.reel_power <= 0:
            self.reel_power = 0
            self.reel_power_direction = 1
        
        # 更新鱼的方向
        if current_time >= self.fish_direction_change_time:
            self.fish_direction = random.randint(0, 3)
            self.fish_direction_change_time = current_time + random.randint(800, 2500)
        
        # 鱼的挣扎会减少张力
        if current_time - self.fish_struggle_timer > 100:  # 每100ms更新一次
            self.tension -= random.randint(2, 5)
            self.fish_struggle_timer = current_time
            
            # 张力过低会让鱼逃走
            if self.tension <= 0:
                self.reset_fishing()
                return "fish_escape"
            
            # 张力过高会断线
            if self.tension >= 100:
                self.reset_fishing()
                return "line_break"
        
        return "minigame_active"
    
    def handle_fishing_input(self, key):
        """处理钓鱼小游戏输入"""
        if not self.fishing_minigame_active:
            return None
            
        # 方向键控制张力
        direction_keys = [pygame.K_w, pygame.K_d, pygame.K_s, pygame.K_a]  # 上右下左
        
        if key in direction_keys:
            pressed_direction = direction_keys.index(key)
            
            # 如果按对了方向，增加张力
            if pressed_direction == self.fish_direction:
                self.tension = min(90, self.tension + 15)
                return "correct_direction"
            else:
                self.tension = max(10, self.tension - 10)
                return "wrong_direction"
                
        # 空格键收杆
        elif key == pygame.K_SPACE:
            return self.attempt_reel()
        
        return None
    
    def attempt_reel(self):
        """尝试收杆"""
        if not self.fishing_minigame_active:
            return None
            
        # 检查力度是否在完美区域
        if self.perfect_zone_start <= self.reel_power <= self.perfect_zone_end:
            # 完美收杆
            self.fish_stamina -= random.randint(15, 25)
            if self.fish_stamina <= 0:
                # 成功钓到鱼
                fish_type, value = self.world.catch_fish(difficulty=0.2)  # 降低失败率
                self.reset_fishing()
                if fish_type:
                    # 添加到背包
                    if fish_type in self.inventory:
                        self.inventory[fish_type] += 1
                    else:
                        self.inventory[fish_type] = 1
                    self.money += value
                return "fish_caught", fish_type, value
            return "perfect_reel"
        else:
            # 普通收杆
            damage = random.randint(5, 12)
            self.fish_stamina -= damage
            
            # 力度过强或过弱会有惩罚
            if self.reel_power < self.perfect_zone_start - 20 or self.reel_power > self.perfect_zone_end + 20:
                self.tension -= random.randint(5, 10)
                
            if self.fish_stamina <= 0:
                # 成功钓到鱼，但质量较低
                fish_type, value = self.world.catch_fish(difficulty=0.5)
                self.reset_fishing()
                if fish_type:
                    # 添加到背包
                    if fish_type in self.inventory:
                        self.inventory[fish_type] += 1
                    else:
                        self.inventory[fish_type] = 1
                    self.money += value
                return "fish_caught", fish_type, value
            return "normal_reel"
    
    def reset_fishing(self):
        """重置钓鱼状态"""
        self.fishing_active = False
        self.waiting_for_fish = False
        self.fish_on_hook = False
        self.fishing_start_time = 0
        self.fish_bite_time = 0
        self.fish_escape_time = 0
        
        # 重置钓鱼小游戏状态
        self.fishing_minigame_active = False
        self.fish_stamina = 100
        self.fish_direction = 0
        self.fish_direction_change_time = 0
        self.tension = 50
        self.reel_power = 0
        self.reel_power_direction = 1
        self.minigame_timer = 0
        self.fish_struggle_timer = 0 