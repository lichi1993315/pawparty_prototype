import pygame
import sys
from game.world import World
from game.player import Player
from game.cat import Cat
from game.ui import UI
from game.time_system import TimeSystem
from game.config import Config
# 注释掉原来的导入，直接在这里实现字体加载
# from game.util import get_font
import pygame_gui

class Game:
    def __init__(self):
        pygame.init()
        self.config = Config()
        self.width, self.height = self.config.screen_width, self.config.screen_height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("猫咪小镇 ASCII Prototype")
        
        # 初始化字体
        self.initialize_fonts()
        
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Initialize game systems
        self.time_system = TimeSystem()
        self.world = World(self.config)
        self.player = Player(self.config, self.world)
        self.cat = Cat(self.config, self.player)
        self.ui = UI(self.screen, self.config, self.player, self.cat, self.time_system)
        
        # Game state
        self.running = True
        self.current_tool = None
        self.holding_item = None
        
        # Debug messages
        self.debug_messages = []
        
        # 障碍物类型翻译字典
        self.obstacle_types = {
            "water": "水域",
            "tree": "树木",
            "rock": "岩石",
            "house": "房屋",
            "边界": "地图边界"
        }
    
    def initialize_fonts(self):
        """初始化字体并添加错误处理"""
        try:
            # 尝试加载系统字体，支持中文
            self.debug_font = pygame.font.SysFont('microsoftyahei', 14)
            print("成功加载系统字体")
        except Exception as e:
            print(f"加载系统字体失败: {e}")
            # 回退到默认字体
            self.debug_font = pygame.font.Font(None, 14)
            print("使用默认字体代替")
    
    def translate_obstacle(self, obstacle_type):
        """将障碍物类型翻译为中文显示"""
        return self.obstacle_types.get(obstacle_type, obstacle_type)
    
    def add_debug_message(self, message):
        self.debug_messages.append(message)
        if len(self.debug_messages) > 5:  # Keep only the last 5 messages
            self.debug_messages.pop(0)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # 如果文本输入框激活，优先处理文本输入
            if self.ui.show_text_input:
                input_result = self.ui.handle_text_input(event)
                if input_result:
                    # 处理完成的输入文本
                    self.process_cat_dialog(input_result)
                continue
            
                        # Handle key presses
        if event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key)
            self.add_debug_message(f"按键: {key_name}")
            
            # 如果钓鱼小游戏激活，优先处理小游戏输入
            if self.player.fishing_minigame_active:
                fishing_result = self.player.handle_fishing_input(event.key)
                if fishing_result == "correct_direction":
                    direction_names = ["上", "右", "下", "左"]
                    self.add_debug_message(f"钓鱼: 跟对了方向! 鱼向{direction_names[self.player.fish_direction]}游")
                elif fishing_result == "wrong_direction":
                    self.add_debug_message(f"钓鱼: 方向错了! 张力下降")
                elif fishing_result == "perfect_reel":
                    self.add_debug_message(f"钓鱼: 完美收杆! 鱼的体力下降")
                elif fishing_result == "normal_reel":
                    self.add_debug_message(f"钓鱼: 普通收杆")
                elif isinstance(fishing_result, tuple) and fishing_result[0] == "fish_caught":
                    _, fish_type, value = fishing_result
                    self.add_debug_message(f"钓鱼: 小游戏成功! 钓到了{fish_type}! 获得{value}金币")
                return
            
            # 如果正在显示交互菜单，处理菜单操作
                if self.ui.show_interaction_menu:
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        self.ui.select_prev_interaction()
                    elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        self.ui.select_next_interaction()
                    elif event.key == pygame.K_e or event.key == pygame.K_RETURN:
                        self.handle_cat_interaction(self.ui.get_selected_interaction())
                    elif event.key == pygame.K_ESCAPE:
                        self.ui.hide_interaction_menu()
                    # 阻止其他按键处理
                    return
                
                # 如果猫被举起，处理猫的投掷
                if self.cat.is_picked_up:
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        self.cat.throw(0)  # 向上丢
                        self.add_debug_message(f"互动: 将猫丢向上方")
                    elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        self.cat.throw(1)  # 向右丢
                        self.add_debug_message(f"互动: 将猫丢向右方")
                    elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        self.cat.throw(2)  # 向下丢
                        self.add_debug_message(f"互动: 将猫丢向下方")
                    elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        self.cat.throw(3)  # 向左丢
                        self.add_debug_message(f"互动: 将猫丢向左方")
                    elif event.key == pygame.K_e:
                        # 放下猫
                        self.cat.is_picked_up = False
                        self.cat.x = self.player.x
                        self.cat.y = self.player.y
                        self.add_debug_message(f"互动: 放下了猫")
                    return
                
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_t:  # 打开文本输入框
                    self.ui.toggle_text_input()
                elif event.key == pygame.K_e:  # 自动交互 - 无需手动切换工具
                    if self.player.fishing_active:
                        # 如果正在钓鱼，尝试收杆
                        result, fish_type, value = self.player.try_catch_fish()
                        if result == "fish_caught":
                            self.add_debug_message(f"钓鱼: 成功钓到了{fish_type}! 获得{value}金币")
                        elif result == "fish_escape":
                            self.add_debug_message(f"钓鱼: 鱼跑掉了...")
                    else:
                        # 检查是否与猫交互
                        if self.is_near_cat():
                            # 打开猫咪交互菜单
                            self.ui.show_cat_interaction_menu()
                            return
                        
                        # 尝试开始钓鱼或其他交互
                        if self.player.use_fishing_rod(self.world):  # 使用use_fishing_rod替代start_fishing
                            self.add_debug_message(f"钓鱼: 开始钓鱼...")
                        else:
                            # 如果不能钓鱼，尝试其他交互
                            interact_result = self.player.interact(self.world, self.cat)
                            
                            # 处理交互结果
                            if isinstance(interact_result, tuple):
                                # 返回了(True/False, 交互类型)
                                success, interaction_type = interact_result
                                
                                if success:
                                    # 障碍物交互反馈
                                    if interaction_type == "tree":
                                        translated_obstacle = self.translate_obstacle(interaction_type)
                                        self.add_debug_message(f"互动: 发现{translated_obstacle}")
                                        self.add_debug_message(f"这棵{translated_obstacle}很高大，需要斧头才能砍伐")
                                    elif interaction_type == "rock":
                                        translated_obstacle = self.translate_obstacle(interaction_type)
                                        self.add_debug_message(f"互动: 发现{translated_obstacle}")
                                        self.add_debug_message(f"这块{translated_obstacle}很坚硬，需要镐才能开采")
                                    elif interaction_type == "water":
                                        translated_obstacle = self.translate_obstacle(interaction_type)
                                        self.add_debug_message(f"互动: 发现{translated_obstacle}")
                                        self.add_debug_message(f"这片{translated_obstacle}很深，需要桥或船才能通过")
                                    # 自动工具使用反馈
                                    elif interaction_type == "harvest":
                                        self.add_debug_message(f"互动: 成功收获了农作物")
                                    elif interaction_type == "forage":
                                        self.add_debug_message(f"互动: 成功采集了野生物品") 
                                    elif interaction_type == "cat":
                                        self.add_debug_message(f"互动: 与猫咪互动，好感度提升")
                                    elif interaction_type == "tilling":
                                        self.add_debug_message(f"互动: 使用锄头耕作了土地")
                                    elif interaction_type == "watering":
                                        self.add_debug_message(f"互动: 使用浇水壶浇了水")
                                    elif interaction_type == "planting":
                                        seed_name = self.player.selected_seed.split("_")[0]
                                        self.add_debug_message(f"互动: 种植了{seed_name}种子")
                                else:
                                    if interaction_type:
                                        translated_type = self.translate_obstacle(interaction_type)
                                        self.add_debug_message(f"互动: 无法与{translated_type}互动")
                                    else:
                                        self.add_debug_message(f"互动: 这里没有可以互动的物体")
                elif event.key == pygame.K_i:  # Inventory
                    # Toggle inventory view
                    self.ui.toggle_inventory()
                
                # Movement
                elif event.key == pygame.K_w:
                    self.player.move(0, -1, self.world)
                    self.add_debug_message(f"玩家位置: ({self.player.x}, {self.player.y})")
                elif event.key == pygame.K_s:
                    self.player.move(0, 1, self.world)
                    self.add_debug_message(f"玩家位置: ({self.player.x}, {self.player.y})")
                elif event.key == pygame.K_a:
                    self.player.move(-1, 0, self.world)
                    self.add_debug_message(f"玩家位置: ({self.player.x}, {self.player.y})")
                elif event.key == pygame.K_d:
                    self.player.move(1, 0, self.world)
                    self.add_debug_message(f"玩家位置: ({self.player.x}, {self.player.y})")
                elif event.key == pygame.K_RETURN:
                    if self.time_system.is_sleep_time() and self.player.at_home():
                        self.time_system.advance_day()
                        self.player.sleep()
                        self.world.update_day()
                        self.add_debug_message(f"睡眠: 进入下一天")
    
    def update(self):
        # Update time
        self.time_system.update()
        
        # Update world (crops grow, etc.)
        self.world.update(self.time_system)
        
        # Update cat behavior
        self.cat.update(self.world, self.player)
        
        # 如果猫被举起，更新猫的位置为玩家位置
        if self.cat.is_picked_up:
            self.cat.x = self.player.x
            self.cat.y = self.player.y
        
        # Update fishing status
        if self.player.fishing_active:
            result = self.player.update_fishing()
            if result == "fish_bite":
                self.add_debug_message("钓鱼: 鱼上钩了！快按E收杆！")
            elif result == "fish_escape":
                self.add_debug_message("钓鱼: 鱼跑掉了...")
            elif result == "line_break":
                self.add_debug_message("钓鱼: 线断了! 张力太高了")
        
        # Natural energy drain over time
        self.player.energy_tick()
        
        # Check sleep condition
        if self.player.energy <= 0:
            if self.player.at_home():
                self.time_system.advance_day()
                self.player.sleep()
                self.world.update_day()
            else:
                # Player passed out - penalty
                self.player.energy = 20
                self.player.position = self.player.home_position
    
    def draw(self):
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Draw world
        self.world.draw(self.screen, self.player)
        
        # Draw player and cat
        self.player.draw(self.screen)
        self.cat.draw(self.screen)
        
        # Draw UI elements
        self.ui.draw(self.current_tool)
        
        pygame.display.flip()
    
    def run(self):
        # Add initial debug message
        self.add_debug_message(f"玩家位置: ({self.player.x}, {self.player.y})")
        while self.running:
            for event in pygame.event.get():
                self.handle_events_single(event)
                self.ui.ui_manager.process_events(event)
            self.update()
            time_delta = self.clock.tick(self.fps) / 1000.0
            self.ui.ui_manager.update(time_delta)
            self.ui.update_status_bar()
            self.ui.update_debug_panel(self.debug_messages)
            self.draw()
            self.ui.ui_manager.draw_ui(self.screen)
        pygame.quit()
        sys.exit()

    def is_near_cat(self):
        """检查玩家是否在猫附近"""
        return (abs(self.player.x - self.cat.x) <= 1 and 
                abs(self.player.y - self.cat.y) <= 1 and
                not self.cat.is_picked_up and
                not self.cat.is_thrown and
                not self.cat.is_swimming)
                
    def handle_cat_interaction(self, option):
        """处理猫咪交互菜单的选择"""
        if option == "抚摸":
            self.cat.pet()
            self.add_debug_message("互动: 抚摸了猫咪，好感度提升")
        elif option == "喂食":
            # 检查玩家是否有鱼
            has_fish = False
            fish_type = None
            for item in list(self.player.inventory.keys()):
                if item in self.config.fish_types and self.player.inventory[item] > 0:
                    has_fish = True
                    fish_type = item
                    break
                    
            if has_fish:
                self.player.inventory[fish_type] -= 1
                self.cat.feed()
                self.add_debug_message(f"互动: 喂食了{fish_type}，猫咪饱食度提升")
            else:
                self.add_debug_message("互动: 没有鱼可以喂食")
        elif option == "举起":
            if self.cat.pick_up():
                self.add_debug_message("互动: 将猫咪举起，按方向键丢出或按E放下")
        
        # 隐藏菜单
        self.ui.hide_interaction_menu()

    def process_cat_dialog(self, text):
        """处理玩家对猫咪的对话"""
        if not text or len(text.strip()) == 0:
            return
            
        # 显示玩家说的话
        self.add_debug_message(f"玩家: {text}")
        
        # 检测猫是否在附近
        if not self.is_cat_nearby_for_chat():
            self.add_debug_message("猫咪没有在附近，听不到你说话...")
            return
            
        # 将输入转给猫处理
        response = self.cat.respond_to_dialog(text)
        self.add_debug_message(f"猫咪: {response}")
        
    def is_cat_nearby_for_chat(self):
        """检查猫是否在附近可以对话（更宽松的范围）"""
        return (abs(self.player.x - self.cat.x) <= 5 and 
                abs(self.player.y - self.cat.y) <= 5 and
                not self.cat.is_thrown)

    # 新增单事件处理方法，原handle_events内容迁移到此
    def handle_events_single(self, event):
        if event.type == pygame.QUIT:
            self.running = False
        # 处理pygame_gui按钮点击事件（猫咪互动菜单）
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if hasattr(event.ui_element, 'object_id') and event.ui_element.object_id.startswith('#cat_menu_'):
                option = event.ui_element.text
                self.handle_cat_interaction(option)
                self.ui.hide_interaction_menu()
                return
            # 处理对话输入框提交按钮
            if hasattr(event.ui_element, 'object_id') and event.ui_element.object_id == '#dialog_submit_btn':
                if self.ui.dialog_text_entry is not None:
                    text = self.ui.dialog_text_entry.get_text()
                    if text.strip():
                        self.process_cat_dialog(text)
                self.ui.toggle_text_input()
                return
        # 处理对话输入框回车提交
        if event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            if self.ui.dialog_text_entry is not None and event.ui_element == self.ui.dialog_text_entry:
                text = event.text
                if text.strip():
                    self.process_cat_dialog(text)
                self.ui.toggle_text_input()
                return
        # 如果文本输入框激活，优先处理文本输入（已迁移为pygame_gui，不再需要原逻辑）
        if self.ui.show_text_input:
            return
        # Handle key presses
        if event.type == pygame.KEYDOWN:
            key_name = pygame.key.name(event.key)
            self.add_debug_message(f"按键: {key_name}")
            # 如果正在显示交互菜单，处理菜单操作
            if self.ui.show_interaction_menu:
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    self.ui.select_prev_interaction()
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    self.ui.select_next_interaction()
                elif event.key == pygame.K_e or event.key == pygame.K_RETURN:
                    self.handle_cat_interaction(self.ui.get_selected_interaction())
                elif event.key == pygame.K_ESCAPE:
                    self.ui.hide_interaction_menu()
                return
            # 如果猫被举起，处理猫的投掷
            if self.cat.is_picked_up:
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    self.cat.throw(0)  # 向上丢
                    self.add_debug_message(f"互动: 将猫丢向上方")
                elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    self.cat.throw(1)  # 向右丢
                    self.add_debug_message(f"互动: 将猫丢向右方")
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    self.cat.throw(2)  # 向下丢
                    self.add_debug_message(f"互动: 将猫丢向下方")
                elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    self.cat.throw(3)  # 向左丢
                    self.add_debug_message(f"互动: 将猫丢向左方")
                elif event.key == pygame.K_e:
                    # 放下猫
                    self.cat.is_picked_up = False
                    self.cat.x = self.player.x
                    self.cat.y = self.player.y
                    self.add_debug_message(f"互动: 放下了猫")
                return
            if event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.key == pygame.K_t:  # 打开文本输入框
                self.ui.toggle_text_input()
            elif event.key == pygame.K_e:  # 自动交互 - 无需手动切换工具
                if self.player.fishing_active:
                    # 如果正在钓鱼，尝试收杆
                    result, fish_type, value = self.player.try_catch_fish()
                    if result == "fish_caught":
                        self.add_debug_message(f"钓鱼: 成功钓到了{fish_type}! 获得{value}金币")
                    elif result == "fish_escape":
                        self.add_debug_message(f"钓鱼: 鱼跑掉了...")
                    elif result == "minigame_start":
                        self.add_debug_message(f"钓鱼: 开始钓鱼小游戏! 用WASD跟随鱼的移动，空格键收杆!")
                else:
                    # 检查是否与猫交互
                    if self.is_near_cat():
                        # 打开猫咪交互菜单
                        self.ui.show_cat_interaction_menu()
                        return
                    # 尝试开始钓鱼或其他交互
                    if self.player.use_fishing_rod(self.world):  # 使用use_fishing_rod替代start_fishing
                        self.add_debug_message(f"钓鱼: 开始钓鱼...")
                    else:
                        # 如果不能钓鱼，尝试其他交互
                        interact_result = self.player.interact(self.world, self.cat)
                        # 处理交互结果
                        if isinstance(interact_result, tuple):
                            # 返回了(True/False, 交互类型)
                            success, interaction_type = interact_result
                            if success:
                                # 障碍物交互反馈
                                if interaction_type == "tree":
                                    translated_obstacle = self.translate_obstacle(interaction_type)
                                    self.add_debug_message(f"互动: 发现{translated_obstacle}")
                                    self.add_debug_message(f"这棵{translated_obstacle}很高大，需要斧头才能砍伐")
                                elif interaction_type == "rock":
                                    translated_obstacle = self.translate_obstacle(interaction_type)
                                    self.add_debug_message(f"互动: 发现{translated_obstacle}")
                                    self.add_debug_message(f"这块{translated_obstacle}很坚硬，需要镐才能开采")
                                elif interaction_type == "water":
                                    translated_obstacle = self.translate_obstacle(interaction_type)
                                    self.add_debug_message(f"互动: 发现{translated_obstacle}")
                                    self.add_debug_message(f"这片{translated_obstacle}很深，需要桥或船才能通过")
                                # 自动工具使用反馈
                                elif interaction_type == "harvest":
                                    self.add_debug_message(f"互动: 成功收获了农作物")
                                elif interaction_type == "forage":
                                    self.add_debug_message(f"互动: 成功采集了野生物品") 
                                elif interaction_type == "cat":
                                    self.add_debug_message(f"互动: 与猫咪互动，好感度提升")
                                elif interaction_type == "tilling":
                                    self.add_debug_message(f"互动: 使用锄头耕作了土地")
                                elif interaction_type == "watering":
                                    self.add_debug_message(f"互动: 使用浇水壶浇了水")
                                elif interaction_type == "planting":
                                    seed_name = self.player.selected_seed.split("_")[0]
                                    self.add_debug_message(f"互动: 种植了{seed_name}种子")
                            else:
                                if interaction_type:
                                    translated_type = self.translate_obstacle(interaction_type)
                                    self.add_debug_message(f"互动: 无法与{translated_type}互动")
                                else:
                                    self.add_debug_message(f"互动: 这里没有可以互动的物体")
            elif event.key == pygame.K_i:  # Inventory
                # Toggle inventory view
                self.ui.toggle_inventory()
            # Movement
            elif event.key == pygame.K_w:
                self.player.move(0, -1, self.world)
                self.add_debug_message(f"玩家位置: ({self.player.x}, {self.player.y})")
            elif event.key == pygame.K_s:
                self.player.move(0, 1, self.world)
                self.add_debug_message(f"玩家位置: ({self.player.x}, {self.player.y})")
            elif event.key == pygame.K_a:
                self.player.move(-1, 0, self.world)
                self.add_debug_message(f"玩家位置: ({self.player.x}, {self.player.y})")
            elif event.key == pygame.K_d:
                self.player.move(1, 0, self.world)
                self.add_debug_message(f"玩家位置: ({self.player.x}, {self.player.y})")
            elif event.key == pygame.K_RETURN:
                if self.time_system.is_sleep_time() and self.player.at_home():
                    self.time_system.advance_day()
                    self.player.sleep()
                    self.world.update_day()
                    self.add_debug_message(f"睡眠: 进入下一天")

if __name__ == "__main__":
    game = Game()
    game.run() 