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
        
        # Visual representation
        self.symbol = config.ascii_tiles["cat"]
        self.color = config.colors["cat"]
        
        # Stats
        self.affection = 50  # Starting affection
        self.hunger = 0     # Starting hunger (higher = less hungry)
        self.max_affection = config.cat_max_affection
        self.max_hunger = config.cat_max_hunger
        
        # 对话状态
        self.last_dialog_time = 0
        self.dialog_mood = "normal"  # normal, happy, angry, sleepy
        
        # Movement variables
        self.follow_distance = config.cat_follow_distance
        self.move_cooldown = 0
        self.random_movement_counter = 0
        
        # Behaviors
        self.is_sleeping = False
        self.is_playing = False
        self.current_behavior = "follow"  # follow, wander, sit, play
        
        # 交互状态
        self.is_picked_up = False  # 是否被玩家举起
        self.is_thrown = False  # 是否被丢出
        self.throw_start_pos = (0, 0)  # 丢出的起始位置
        self.throw_target_pos = (0, 0)  # 丢出的目标位置
        self.throw_progress = 0  # 丢出的进度 (0-1)
        self.throw_speed = 0.1  # 丢出的速度
        self.is_swimming = False  # 是否在游泳
        self.swim_time = 0  # 游泳时间
        
        # Fishing behavior
        self.is_fishing = False
        self.fishing_progress = 0
        self.fishing_cooldown = 0
        self.fish_caught = 0
        
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
        # 更新对话情绪（随时间恢复正常）
        current_time = pygame.time.get_ticks()
        if current_time - self.last_dialog_time > 20000:  # 20秒后恢复正常情绪
            self.dialog_mood = "normal"
        
        # 如果被举起，直接跟随玩家位置
        if self.is_picked_up:
            return
            
        # 如果被丢出，更新丢出状态
        if self.is_thrown:
            self.update_throw()
            return
            
        # 如果在游泳，更新游泳状态
        if self.is_swimming:
            self.update_swimming()
            return
    
        # Update hunger
        self.hunger = min(self.config.cat_max_hunger, 
                         self.hunger + self.config.cat_hunger_rate)
        
        # Reset fishing state if player is too far
        if self.is_fishing and self.distance_to_player() > self.config.cat_follow_distance * 2:
            self.is_fishing = False
            self.fishing_progress = 0
        
        # Decide what to do
        if self.is_fishing:
            self.continue_fishing(world)
        elif self.fishing_cooldown > 0:
            self.fishing_cooldown -= 1
        elif self.hunger > 50 and random.random() < 0.1:  # 10% chance to start fishing when hungry
            self.try_start_fishing(world)
        elif self.current_behavior == "follow":
            self.follow_player(world)
        
        # If not fishing and too far from player, start following
        if not self.is_fishing and self.distance_to_player() > self.config.cat_follow_distance:
            self.current_behavior = "follow"
        
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
        """跟随玩家"""
        if self.distance_to_player() > self.config.cat_follow_distance:
            # Calculate direction to player
            dx = self.player.x - self.x
            dy = self.player.y - self.y
            
            # Normalize direction
            if abs(dx) > abs(dy):
                dx = 1 if dx > 0 else -1 if dx < 0 else 0
                dy = 0
            else:
                dx = 0
                dy = 1 if dy > 0 else -1 if dy < 0 else 0
            
            # Try to move
            new_x = self.x + dx
            new_y = self.y + dy
            
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
        """被玩家抚摸"""
        self.affection = min(self.max_affection, self.affection + 5)
        self.current_behavior = "follow"
        
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
        # 如果被玩家举起，不需要单独绘制
        if self.is_picked_up:
            return
        
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
            
            # 根据不同状态显示不同的符号和颜色
            symbol = self.symbol
            color = self.color
            
            if self.is_thrown:
                symbol = "*"  # 飞行中的猫
            elif self.is_swimming:
                symbol = "~"  # 游泳中的猫
                color = (0, 100, 255)  # 蓝色调
            elif self.is_fishing:
                symbol = "F"  # 钓鱼中的猫
            
            # 绘制猫咪
            text_surface = font.render(symbol, True, color)
            screen.blit(text_surface, (screen_x, screen_y))
            
            # 根据情绪显示不同的表情符号
            current_time = pygame.time.get_ticks()
            if current_time - self.last_dialog_time < 5000:  # 5秒内显示情绪
                mood_symbols = {
                    "happy": "♥",   # 爱心
                    "angry": "!",    # 感叹号
                    "sleepy": "z",   # 睡觉符号
                    "normal": "?"    # 问号
                }
                
                mood_symbol = mood_symbols.get(self.dialog_mood, "?")
                mood_color = {
                    "happy": (255, 105, 180),  # 粉色
                    "angry": (255, 0, 0),      # 红色
                    "sleepy": (100, 149, 237), # 蓝色
                    "normal": (255, 255, 255)  # 白色
                }.get(self.dialog_mood, (255, 255, 255))
                
                # 创建小一号的字体
                small_font = get_font(is_ascii=True, size=int(self.config.tile_size * 0.7))
                mood_surface = small_font.render(mood_symbol, True, mood_color)
                
                # 在猫咪头上方显示情绪符号
                screen.blit(mood_surface, (screen_x + self.config.tile_size - 5, screen_y - 10))
    
    def try_start_fishing(self, world):
        """尝试开始捕鱼"""
        # 检查周围的水域
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                new_x, new_y = self.x + dx, self.y + dy
                tile = world.get_tile(new_x, new_y)
                if tile and tile.type == "water":
                    # 找到水域，开始捕鱼
                    self.is_fishing = True
                    self.fishing_progress = 0
                    return True
        return False
    
    def continue_fishing(self, world):
        """继续捕鱼动作"""
        self.fishing_progress += 1
        if self.fishing_progress >= 60:  # 2秒后完成捕鱼
            # 40%的概率捕到鱼
            if random.random() < 0.4:
                self.fish_caught += 1
                self.hunger = max(0, self.hunger - 30)  # 吃掉鱼，减少饥饿
            
            # 重置状态
            self.is_fishing = False
            self.fishing_progress = 0
            self.fishing_cooldown = 180  # 设置6秒冷却时间
    
    def distance_to_player(self):
        """计算与玩家的距离"""
        return max(abs(self.x - self.player.x), abs(self.y - self.player.y))
        
    def pick_up(self):
        """被玩家举起"""
        if not self.is_picked_up and not self.is_thrown and not self.is_swimming:
            self.is_picked_up = True
            self.affection = max(0, self.affection - 2)  # 猫不太喜欢被举起
            return True
        return False
        
    def throw(self, direction):
        """被玩家丢出
        direction: 0=上, 1=右, 2=下, 3=左
        """
        if not self.is_picked_up:
            return False
            
        self.is_picked_up = False
        self.is_thrown = True
        self.throw_progress = 0
        self.affection = max(0, self.affection - 5)  # 猫很不喜欢被丢出
        
        # 设置起点和终点
        self.throw_start_pos = (self.player.x, self.player.y)
        
        # 根据方向设置目标位置（最远3格）
        throw_distance = min(3, 3)  # 丢出距离
        if direction == 0:  # 上
            target_x = self.player.x
            target_y = self.player.y - throw_distance
        elif direction == 1:  # 右
            target_x = self.player.x + throw_distance
            target_y = self.player.y
        elif direction == 2:  # 下
            target_x = self.player.x
            target_y = self.player.y + throw_distance
        else:  # 左
            target_x = self.player.x - throw_distance
            target_y = self.player.y
            
        # 确保目标位置在地图范围内
        target_x = max(0, min(self.world.width - 1, target_x))
        target_y = max(0, min(self.world.height - 1, target_y))
        
        self.throw_target_pos = (target_x, target_y)
        return True
        
    def update_throw(self):
        """更新猫被丢出的状态"""
        if not self.is_thrown:
            return
            
        # 更新丢出进度
        self.throw_progress += self.throw_speed
        
        if self.throw_progress >= 1.0:
            # 丢出结束
            self.is_thrown = False
            self.x, self.y = self.throw_target_pos
            
            # 检查是否落入水中
            tile = self.world.get_tile(self.x, self.y)
            if tile and tile.type == "water":
                self.start_swimming()
                
        else:
            # 计算当前位置
            start_x, start_y = self.throw_start_pos
            target_x, target_y = self.throw_target_pos
            
            # 模拟抛物线
            # 使用插值计算位置
            t = self.throw_progress
            height_factor = 4 * t * (1 - t)  # 抛物线高度系数
            
            self.x = int(start_x + (target_x - start_x) * t)
            self.y = int(start_y + (target_y - start_y) * t)
            
    def start_swimming(self):
        """开始游泳"""
        self.is_swimming = True
        self.swim_time = 0
        
    def update_swimming(self):
        """更新猫的游泳状态"""
        if not self.is_swimming:
            return
            
        self.swim_time += 1
        
        # 随机移动
        if self.swim_time % 10 == 0:  # 每10帧移动一次
            # 寻找最近的陆地
            found_land = False
            
            # 检查周围的瓦片
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                        
                    check_x = self.x + dx
                    check_y = self.y + dy
                    
                    # 确保位置在地图范围内
                    if 0 <= check_x < self.world.width and 0 <= check_y < self.world.height:
                        tile = self.world.get_tile(check_x, check_y)
                        if tile and tile.type != "water":
                            # 找到陆地，游向陆地
                            self.x = check_x
                            self.y = check_y
                            self.is_swimming = False
                            found_land = True
                            break
                            
                if found_land:
                    break
                    
            if not found_land:
                # 没找到陆地，随机移动
                directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                dx, dy = random.choice(directions)
                
                new_x = self.x + dx
                new_y = self.y + dy
                
                # 确保位置在地图范围内
                if 0 <= new_x < self.world.width and 0 <= new_y < self.world.height:
                    self.x = new_x
                    self.y = new_y
    
    def respond_to_dialog(self, text):
        """响应玩家的对话"""
        import pygame
        import time
        
        # 记录对话时间
        self.last_dialog_time = pygame.time.get_ticks()
        
        # 转换为小写，便于匹配关键词
        text = text.lower()
        
        # 根据对话内容调整情绪
        if any(word in text for word in ["喵", "猫", "可爱", "乖", "漂亮", "好看"]):
            self.dialog_mood = "happy"
            self.affection = min(self.max_affection, self.affection + 2)
        elif any(word in text for word in ["傻", "笨", "丑", "蠢", "讨厌"]):
            self.dialog_mood = "angry"
            self.affection = max(0, self.affection - 3)
        elif any(word in text for word in ["睡觉", "累", "困", "休息"]):
            self.dialog_mood = "sleepy"
        else:
            self.dialog_mood = "normal"
        
        # 检查是否包含食物相关词
        food_words = ["食物", "吃的", "吃饭", "饿", "鱼", "猫粮"]
        if any(word in text for word in food_words):
            self.hunger = min(self.max_hunger, self.hunger + 5)
            if self.dialog_mood != "angry":
                self.dialog_mood = "happy"
        
        # 根据情绪和状态生成回应
        responses = {
            "happy": [
                "喵~！", "喵喵~", "咪~ (蹭蹭)", "喵！ (尾巴摇动)", "咪咪~ (眯眼微笑)",
                "Meow~!", "Purr~", "Meow meow~", "Mrrow! (tail wags)", "Mew~ (happy eyes)"
            ],
            "angry": [
                "喵！(炸毛)", "呜... (背过身去)", "哈气！", "喵... (不满地甩尾巴)", "...",
                "HISS!", "Meow! (fur standing)", "Grr...", "Mrr... (angry tail flick)", "..."
            ],
            "sleepy": [
                "呼噜噜...", "喵~~ (打哈欠)", "(无视并继续睡觉)", "喵... (慵懒地眨眼)",
                "Purrrr...", "Meow~~ (yawning)", "(ignores you and continues sleeping)", "Mew... (lazy blink)"
            ],
            "normal": [
                "喵？", "喵喵？", "(歪头)", "喵~", "(专注地看着你)",
                "Meow?", "Meow meow?", "(tilts head)", "Mew~", "(stares at you intently)"
            ]
        }
        
        # 如果饥饿，偶尔会表达饥饿感
        if self.hunger > 70 and random.random() < 0.4:
            hunger_responses = [
                "喵喵喵！(盯着你的口袋)", "喵~ (围着你的脚转圈)", "(可怜巴巴地望着你)",
                "Meow meow meow! (stares at your pocket)", "Mrrp~ (circles around your feet)", "(gives you pitiful eyes)"
            ]
            return random.choice(hunger_responses)
        
        # 如果被丢过，会表现出不满
        if self.is_thrown or (self.throw_progress > 0 and pygame.time.get_ticks() - self.last_dialog_time < 10000):
            return random.choice(["喵！！！(生气地瞪着你)", "MEOW!!! (glares at you angrily)"])
        
        # 如果在游泳，回应会不同
        if self.is_swimming:
            return random.choice(["喵呜！喵呜！(急促地叫着)", "Mrow! Mrow! (calls urgently)"])
        
        # 随机选择一个对应情绪的回应
        return random.choice(responses[self.dialog_mood]) 