import pygame
import sys
from game.world import World
from game.player import Player
from game.cat import Cat
from game.ui import UI
from game.time_system import TimeSystem
from game.config import Config
from game.util import get_font

class Game:
    def __init__(self):
        pygame.init()
        self.config = Config()
        self.width, self.height = self.config.screen_width, self.config.screen_height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("猫咪小镇 ASCII Prototype")
        
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
            
            # Handle key presses
            if event.type == pygame.KEYDOWN:
                key_name = pygame.key.name(event.key)
                self.add_debug_message(f"按键: {key_name}")
                
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_e:  # 自动交互 - 无需手动切换工具
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
                            elif interaction_type == "fishing":
                                self.add_debug_message(f"互动: 开始钓鱼...")
                                # 当前工具显示为钓鱼竿
                                self.current_tool = "fishing_rod"
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
        
        # Draw debug messages - 将位置移到屏幕右侧
        # 使用支持中文的字体
        font = get_font(is_ascii=False, size=14)
        y_offset = 100
        
        # 创建调试信息面板背景
        debug_panel_width = 300
        debug_panel_x = self.width - debug_panel_width - 10  # 距离右边缘10像素
        pygame.draw.rect(self.screen, (0, 0, 0), 
                        (debug_panel_x, y_offset - 10, debug_panel_width, len(self.debug_messages) * 20 + 20))
        pygame.draw.rect(self.screen, (50, 50, 50), 
                        (debug_panel_x, y_offset - 10, debug_panel_width, len(self.debug_messages) * 20 + 20), 1)
        
        # 绘制调试信息标题
        title_surface = font.render("调试信息", True, (200, 200, 200))
        self.screen.blit(title_surface, (debug_panel_x + 10, y_offset - 5))
        y_offset += 15
        
        for message in self.debug_messages:
            text_surface = font.render(message, True, (255, 255, 255))
            self.screen.blit(text_surface, (debug_panel_x + 10, y_offset))
            y_offset += 20
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        # Add initial debug message
        self.add_debug_message(f"玩家位置: ({self.player.x}, {self.player.y})")
        
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run() 