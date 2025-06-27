import pygame
from game.util import get_font
import pygame_gui
import time

class UI:
    def __init__(self, screen, config, player, cat, time_system):
        self.screen = screen
        self.config = config
        self.player = player
        self.cat = cat
        self.time_system = time_system
        
        # 交互菜单
        self.show_interaction_menu = False
        self.interaction_options = []
        self.selected_interaction = 0
        
        # 文本输入框
        self.show_text_input = False
        self.input_text = ""
        self.input_active = False
        self.input_rect = pygame.Rect(100, 100, 600, 40)
        
        # UI states
        self.show_inventory = False
        self.show_notifications = True
        self.notifications = []
        self.notification_timer = 0
        
        # Fonts - 使用支持中文的字体
        self.font_small = get_font(is_ascii=False, size=14)
        self.font_medium = get_font(is_ascii=False, size=18)
        self.font_large = get_font(is_ascii=False, size=24)
        
        # ASCII字体 - 用于游戏符号
        self.ascii_font_small = get_font(is_ascii=True, size=14)
        self.ascii_font_medium = get_font(is_ascii=True, size=18)
        self.ascii_font_large = get_font(is_ascii=True, size=24)
        
        # 初始化pygame_gui
        self.ui_manager = pygame_gui.UIManager((self.screen.get_width(), self.screen.get_height()))
        # 创建底部状态栏面板
        self.status_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, self.screen.get_height() - 60), (self.screen.get_width(), 60)),
            manager=self.ui_manager
        )
        self.energy_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 10), (120, 30)),
            text="能量: 100/100",
            manager=self.ui_manager,
            container=self.status_panel
        )
        self.money_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((140, 10), (120, 30)),
            text="金钱: $500",
            manager=self.ui_manager,
            container=self.status_panel
        )
        self.time_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.screen.get_width() - 150, 10), (140, 30)),
            text="08:00",
            manager=self.ui_manager,
            container=self.status_panel
        )
        self.date_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((self.screen.get_width() - 300, 10), (140, 30)),
            text="春季 1日, 第1年",
            manager=self.ui_manager,
            container=self.status_panel
        )
        # 创建操作提示栏（controls_label），放在底部状态栏下方
        self.controls_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, self.screen.get_height() - 25), (400, 20)),
            text="按键说明: [WASD]移动 [E]交互 [I]背包 [T]对话 [Enter]睡觉",
            manager=self.ui_manager
        )
        self.inventory_window = None  # pygame_gui背包窗口
        self.cat_menu_panel = None  # pygame_gui猫咪互动菜单面板
        self.cat_menu_buttons = []  # 按钮列表
        self.dialog_input_panel = None
        self.dialog_text_entry = None
        self.dialog_submit_btn = None
        self.active_notifications = []  # [(panel, expire_time)]
        self.debug_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((self.screen.get_width()-310, 100), (300, 170)),
            manager=self.ui_manager
        )
        self.debug_title = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 0), (120, 22)),
            text="调试信息",
            manager=self.ui_manager,
            container=self.debug_panel
        )
        self.debug_labels = [
            pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect((10, 30+i*25), (280, 22)),
                text="",
                manager=self.ui_manager,
                container=self.debug_panel
            ) for i in range(5)
        ]
    
    def add_notification(self, message, duration=180):  # 3 seconds at 60 FPS
        panel_width, panel_height = 300, 40
        x = (self.screen.get_width() - panel_width) // 2
        y = 60 + len(self.active_notifications) * (panel_height + 10)
        panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((x, y), (panel_width, panel_height)),
            manager=self.ui_manager
        )
        label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 5), (panel_width-20, 30)),
            text=message,
            manager=self.ui_manager,
            container=panel
        )
        expire_time = time.time() + duration/60.0  # duration帧转秒
        self.active_notifications.append((panel, expire_time))
    
    def toggle_inventory(self):
        if self.inventory_window is not None:
            self.inventory_window.kill()
            self.inventory_window = None
            self.show_inventory = False
        else:
            self.show_inventory = True
            # 创建背包窗口
            self.inventory_window = pygame_gui.elements.UIWindow(
                rect=pygame.Rect((self.screen.get_width()//2-200, self.screen.get_height()//2-150), (400, 300)),
                manager=self.ui_manager,
                window_display_title="物品栏"
            )
            # 物品名称的中文翻译
            item_translations = {
                "turnip_seeds": "萝卜种子",
                "potato_seeds": "土豆种子",
                "tomato_seeds": "番茄种子",
                "cat_food": "猫粮",
                "turnip": "萝卜",
                "potato": "土豆",
                "tomato": "番茄",
                "anchovy": "凤尾鱼",
                "tuna": "金枪鱼",
                "salmon": "三文鱼",
                "mushroom": "蘑菇",
                "berry": "浆果",
                "herb": "草药"
            }
            items_y = 40
            items_x = 20
            for item_name, count in self.player.inventory.items():
                if count > 0:
                    display_name = item_translations.get(item_name, item_name.replace('_', ' ').title())
                    item_text = f"{display_name}: {count}"
                    pygame_gui.elements.UILabel(
                        relative_rect=pygame.Rect((items_x, items_y), (160, 24)),
                        text=item_text,
                        manager=self.ui_manager,
                        container=self.inventory_window
                    )
                    items_y += 28
                    if items_y > 240:
                        items_y = 40
                        items_x += 180
    
    def show_cat_interaction_menu(self):
        # 强制重新创建菜单，确保新布局生效
        if self.cat_menu_panel is not None:
            self.cat_menu_panel.kill()
            self.cat_menu_panel = None
            self.cat_menu_buttons = []
        
        panel_width, panel_height = 200, 300  # 再增高
        panel_x = (self.screen.get_width() - panel_width) // 2
        panel_y = (self.screen.get_height() - panel_height) // 2
        self.cat_menu_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((panel_x, panel_y), (panel_width, panel_height)),
            manager=self.ui_manager
        )
        # 标题
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((0, 10), (panel_width, 30)),
            text="猫咪互动",
            manager=self.ui_manager,
            container=self.cat_menu_panel
        )
        options = ["抚摸", "喂食", "举起", "取消"]
        self.cat_menu_buttons = []
        for i, option in enumerate(options):
            btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((30, 40 + i*40), (140, 32)),  # 起始40，间距40
                text=option,
                manager=self.ui_manager,
                container=self.cat_menu_panel,
                object_id=f"#cat_menu_{option}"
            )
            self.cat_menu_buttons.append(btn)
        self.show_interaction_menu = True
        self.interaction_options = options
        self.selected_interaction = 0
    
    def hide_interaction_menu(self):
        if self.cat_menu_panel is not None:
            self.cat_menu_panel.kill()
            self.cat_menu_panel = None
            self.cat_menu_buttons = []
        self.show_interaction_menu = False
        self.interaction_options = []
    
    def select_next_interaction(self):
        """选择下一个交互选项"""
        if self.interaction_options:
            self.selected_interaction = (self.selected_interaction + 1) % len(self.interaction_options)
    
    def select_prev_interaction(self):
        """选择上一个交互选项"""
        if self.interaction_options:
            self.selected_interaction = (self.selected_interaction - 1) % len(self.interaction_options)
    
    def get_selected_interaction(self):
        """获取当前选中的交互选项"""
        if self.interaction_options:
            return self.interaction_options[self.selected_interaction]
        return None
    
    def toggle_text_input(self):
        if self.dialog_input_panel is not None:
            self.dialog_input_panel.kill()
            self.dialog_input_panel = None
            self.dialog_text_entry = None
            self.dialog_submit_btn = None
            self.show_text_input = False
            self.input_active = False
        else:
            self.show_text_input = True
            self.input_active = True
            # 创建输入框面板
            panel_width, panel_height = 400, 80
            panel_x = (self.screen.get_width() - panel_width) // 2
            panel_y = self.screen.get_height() - 120
            self.dialog_input_panel = pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect((panel_x, panel_y), (panel_width, panel_height)),
                manager=self.ui_manager
            )
            # 输入框
            self.dialog_text_entry = pygame_gui.elements.UITextEntryLine(
                relative_rect=pygame.Rect((100, 20), (200, 30)),
                manager=self.ui_manager,
                container=self.dialog_input_panel
            )
            self.dialog_text_entry.set_text("")
            # 提交按钮
            self.dialog_submit_btn = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((310, 20), (70, 30)),
                text="发送",
                manager=self.ui_manager,
                container=self.dialog_input_panel,
                object_id="#dialog_submit_btn"
            )
    
    def handle_text_input(self, event):
        """处理文本输入事件"""
        if not self.show_text_input or not self.input_active:
            return False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # 处理完成的输入文本
                input_text = self.input_text
                self.input_text = ""
                self.toggle_text_input()
                return input_text
            elif event.key == pygame.K_BACKSPACE:
                # 删除字符
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_ESCAPE:
                # 取消输入
                self.toggle_text_input()
                return False
            else:
                # 添加字符
                if len(self.input_text) < 30:  # 限制输入长度
                    if event.unicode.isprintable():  # 只添加可打印字符
                        self.input_text += event.unicode
        return False
    
    def draw_text_input(self):
        """绘制文本输入框"""
        if not self.show_text_input:
            return
            
        # 将输入框放在屏幕底部
        self.input_rect.x = 100
        self.input_rect.y = self.screen.get_height() - 100
        
        # 绘制半透明背景
        bg_surface = pygame.Surface((self.input_rect.width + 20, self.input_rect.height + 20))
        bg_surface.set_alpha(200)
        bg_surface.fill((30, 30, 30))
        self.screen.blit(bg_surface, (self.input_rect.x - 10, self.input_rect.y - 10))
        
        # 绘制输入框边框
        border_color = (255, 255, 255) if self.input_active else (150, 150, 150)
        pygame.draw.rect(self.screen, border_color, self.input_rect, 2)
        
        # 绘制提示文本
        prompt_text = "对猫咪说: "
        prompt_surface = self.font_medium.render(prompt_text, True, (255, 255, 255))
        self.screen.blit(prompt_surface, (self.input_rect.x - prompt_surface.get_width() - 10, self.input_rect.y + 5))
        
        # 绘制输入的文本
        if self.input_text:
            text_surface = self.font_medium.render(self.input_text, True, (255, 255, 255))
            self.screen.blit(text_surface, (self.input_rect.x + 5, self.input_rect.y + 5))
        
        # 绘制光标
        if self.input_active and int(pygame.time.get_ticks() / 500) % 2 == 0:
            # 计算光标位置
            cursor_pos = self.font_medium.size(self.input_text)[0]
            pygame.draw.line(self.screen, (255, 255, 255),
                           (self.input_rect.x + cursor_pos + 5, self.input_rect.y + 5),
                           (self.input_rect.x + cursor_pos + 5, self.input_rect.y + self.input_rect.height - 5), 2)
                           
    def draw(self, current_tool):
        # Draw status bar at the bottom
        self.draw_status_bar(current_tool)
        
        # Draw notifications
        self.draw_notifications()
        
        # Draw inventory if open
        if self.show_inventory:
            self.draw_inventory()
        
        # Draw cat info in top right
        self.draw_cat_info()
        
        # 绘制交互菜单
        if self.show_interaction_menu:
            self.draw_interaction_menu()
            
        # 绘制文本输入框
        if self.show_text_input:
            self.draw_text_input()
            
        # 绘制钓鱼小游戏界面
        if self.player.fishing_minigame_active:
            self.draw_fishing_minigame()
    
    def draw_status_bar(self, current_tool):
        # Draw a black bar at the bottom
        pygame.draw.rect(self.screen, (0, 0, 0), 
                         (0, self.screen.get_height() - 60, self.screen.get_width(), 60))
        pygame.draw.rect(self.screen, (50, 50, 50), 
                         (0, self.screen.get_height() - 60, self.screen.get_width(), 60), 1)
        
        # Draw player info - energy, money, time
        energy_text = f"能量: {int(self.player.energy)}/{self.config.max_energy}"
        money_text = f"金钱: ${self.player.money}"
        time_text = self.time_system.get_time_string()
        date_text = self.time_system.get_date_string()
        
        # Energy bar
        energy_pct = self.player.energy / self.config.max_energy
        energy_width = 150 * energy_pct
        pygame.draw.rect(self.screen, (100, 100, 100), 
                         (10, self.screen.get_height() - 55, 150, 15))
        pygame.draw.rect(self.screen, self.config.colors["energy"], 
                         (10, self.screen.get_height() - 55, energy_width, 15))
        
        # Texts - 使用中文字体
        energy_surface = self.font_small.render(energy_text, True, self.config.colors["text"])
        money_surface = self.font_small.render(money_text, True, self.config.colors["text"])
        time_surface = self.font_small.render(time_text, True, self.config.colors["time"])
        date_surface = self.font_small.render(date_text, True, self.config.colors["time"])
        
        # Position and draw texts
        self.screen.blit(energy_surface, (165, self.screen.get_height() - 55))
        self.screen.blit(money_surface, (165, self.screen.get_height() - 35))
        self.screen.blit(time_surface, (self.screen.get_width() - 150, self.screen.get_height() - 55))
        self.screen.blit(date_surface, (self.screen.get_width() - 200, self.screen.get_height() - 35))
        
        # Draw current tool
        if current_tool:
            tool_name = {
                "hoe": "锄头",
                "watering_can": "浇水壶",
                "seeds": "种子",
                "fishing_rod": "钓鱼竿"
            }.get(current_tool, current_tool.capitalize())
            
            tool_text = f"工具: {tool_name}"
            tool_surface = self.font_small.render(tool_text, True, self.config.colors["text"])
            self.screen.blit(tool_surface, (350, self.screen.get_height() - 45))
    
    def draw_notifications(self):
        # 清理过期通知
        now = time.time()
        for panel, expire in self.active_notifications[:]:
            if now > expire:
                panel.kill()
                self.active_notifications.remove((panel, expire))
    
    def draw_inventory(self):
        # Semi-transparent background
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Inventory panel
        panel_width = 400
        panel_height = 300
        panel_x = (self.screen.get_width() - panel_width) // 2
        panel_y = (self.screen.get_height() - panel_height) // 2
        
        pygame.draw.rect(self.screen, (30, 30, 30), 
                         (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, (100, 100, 100), 
                         (panel_x, panel_y, panel_width, panel_height), 2)
        
        # Title (使用中文)
        title_surface = self.font_large.render("物品栏", True, self.config.colors["text"])
        self.screen.blit(title_surface, (panel_x + (panel_width - title_surface.get_width()) // 2, panel_y + 10))
        
        # 物品名称的中文翻译
        item_translations = {
            "turnip_seeds": "萝卜种子",
            "potato_seeds": "土豆种子",
            "tomato_seeds": "番茄种子",
            "cat_food": "猫粮",
            "turnip": "萝卜",
            "potato": "土豆",
            "tomato": "番茄",
            "anchovy": "凤尾鱼",
            "tuna": "金枪鱼",
            "salmon": "三文鱼",
            "mushroom": "蘑菇",
            "berry": "浆果",
            "herb": "草药"
        }
        
        # List items
        items_y = panel_y + 50
        items_x = panel_x + 20
        
        for item_name, count in self.player.inventory.items():
            if count > 0:  # Only show items with quantity > 0
                # 使用翻译后的名称
                display_name = item_translations.get(item_name, item_name.replace('_', ' ').title())
                item_text = f"{display_name}: {count}"
                item_surface = self.font_medium.render(item_text, True, self.config.colors["text"])
                self.screen.blit(item_surface, (items_x, items_y))
                items_y += 25
                
                # Create another column if we run out of space
                if items_y > panel_y + panel_height - 30:
                    items_y = panel_y + 50
                    items_x += 200
    
    def draw_cat_info(self):
        """绘制猫咪信息"""
        if self.cat.is_picked_up:
            # 如果猫被举起，在玩家上方绘制猫
            world_view_x = self.player.world.view_x_start
            world_view_y = self.player.world.view_y_start
            
            # 计算玩家位置
            player_screen_x = (self.player.x - world_view_x) * self.config.tile_size
            player_screen_y = (self.player.y - world_view_y) * self.config.tile_size
            
            # 在玩家头上绘制猫
            from game.util import get_font
            font = get_font(is_ascii=True, size=self.config.tile_size)
            cat_surface = font.render(self.cat.symbol, True, self.cat.color)
            self.screen.blit(cat_surface, (player_screen_x, player_screen_y - self.config.tile_size))
            
        # 绘制猫咪状态信息
        hunger_text = f"猫咪饥饿: {int(self.cat.hunger)}/{self.cat.max_hunger}"
        affection_text = f"猫咪好感: {int(self.cat.affection)}/{self.cat.max_affection}"
        
        # 计算位置（屏幕左上角）
        info_x = 10
        info_y = 10
        
        # 绘制背景
        bg_width = max(self.font_small.size(hunger_text)[0], self.font_small.size(affection_text)[0]) + 20
        bg_height = 50
        s = pygame.Surface((bg_width, bg_height))
        s.set_alpha(150)
        s.fill((0, 0, 0))
        self.screen.blit(s, (info_x, info_y))
        
        # 绘制文本
        hunger_surface = self.font_small.render(hunger_text, True, (255, 255, 255))
        affection_surface = self.font_small.render(affection_text, True, (255, 255, 255))
        
        self.screen.blit(hunger_surface, (info_x + 10, info_y + 10))
        self.screen.blit(affection_surface, (info_x + 10, info_y + 30))

    def draw_interaction_menu(self):
        """绘制交互菜单"""
        if not self.show_interaction_menu:
            return
            
        # 菜单背景
        menu_width = 150
        menu_height = len(self.interaction_options) * 30 + 20
        menu_x = (self.screen.get_width() - menu_width) // 2
        menu_y = (self.screen.get_height() - menu_height) // 2
        
        # 绘制半透明背景
        s = pygame.Surface((menu_width, menu_height))
        s.set_alpha(200)
        s.fill((50, 50, 50))
        self.screen.blit(s, (menu_x, menu_y))
        
        # 绘制边框
        pygame.draw.rect(self.screen, (200, 200, 200), 
                        (menu_x, menu_y, menu_width, menu_height), 2)
        
        # 绘制标题
        title = "猫咪互动"
        title_surface = self.font_medium.render(title, True, (255, 255, 255))
        title_x = menu_x + (menu_width - title_surface.get_width()) // 2
        self.screen.blit(title_surface, (title_x, menu_y + 10))
        
        # 绘制选项
        for i, option in enumerate(self.interaction_options):
            color = (255, 255, 0) if i == self.selected_interaction else (255, 255, 255)
            option_surface = self.font_small.render(option, True, color)
            option_x = menu_x + 20
            option_y = menu_y + 40 + i * 30
            self.screen.blit(option_surface, (option_x, option_y))
    
    def update_status_bar(self):
        self.energy_label.set_text(f"能量: {int(self.player.energy)}/{self.config.max_energy}")
        self.money_label.set_text(f"金钱: ${self.player.money}")
        self.time_label.set_text(self.time_system.get_time_string())
        self.date_label.set_text(self.time_system.get_date_string())
        self.controls_label.set_text("按键说明: [WASD]移动 [E]交互 [I]背包 [T]对话 [Enter]睡觉")
        # 清理过期通知
        now = time.time()
        for panel, expire in self.active_notifications[:]:
            if now > expire:
                panel.kill()
                self.active_notifications.remove((panel, expire)) 
    
    def update_debug_panel(self, debug_messages):
        for i, label in enumerate(self.debug_labels):
            label.set_text(debug_messages[i] if i < len(debug_messages) else "")
    
    def draw_fishing_minigame(self):
        """绘制钓鱼小游戏界面"""
        if not self.player.fishing_minigame_active:
            return
            
        # 小游戏面板位置和大小
        panel_width = 400
        panel_height = 300
        panel_x = (self.screen.get_width() - panel_width) // 2
        panel_y = (self.screen.get_height() - panel_height) // 2
        
        # 绘制半透明背景
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # 绘制主面板
        pygame.draw.rect(self.screen, (30, 30, 30), 
                         (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, (100, 100, 100), 
                         (panel_x, panel_y, panel_width, panel_height), 3)
        
        # 标题
        title = "钓鱼小游戏"
        title_surface = self.font_large.render(title, True, (255, 255, 255))
        title_x = panel_x + (panel_width - title_surface.get_width()) // 2
        self.screen.blit(title_surface, (title_x, panel_y + 10))
        
        # 绘制鱼的耐力条
        stamina_y = panel_y + 50
        stamina_width = panel_width - 40
        stamina_height = 20
        stamina_x = panel_x + 20
        
        # 耐力条背景
        pygame.draw.rect(self.screen, (60, 60, 60), 
                         (stamina_x, stamina_y, stamina_width, stamina_height))
        
        # 耐力条前景
        stamina_pct = self.player.fish_stamina / self.player.fish_max_stamina
        pygame.draw.rect(self.screen, (255, 100, 100), 
                         (stamina_x, stamina_y, stamina_width * stamina_pct, stamina_height))
        
        # 耐力条标签
        stamina_text = f"鱼的体力: {int(self.player.fish_stamina)}/{self.player.fish_max_stamina}"
        stamina_surface = self.font_medium.render(stamina_text, True, (255, 255, 255))
        self.screen.blit(stamina_surface, (stamina_x, stamina_y - 25))
        
        # 绘制张力条
        tension_y = panel_y + 100
        tension_width = panel_width - 40
        tension_height = 20
        tension_x = panel_x + 20
        
        # 张力条背景
        pygame.draw.rect(self.screen, (60, 60, 60), 
                         (tension_x, tension_y, tension_width, tension_height))
        
        # 张力条前景 - 颜色根据张力值变化
        tension_pct = self.player.tension / 100
        if self.player.tension < 30:
            tension_color = (255, 100, 100)  # 红色 - 危险
        elif self.player.tension > 70:
            tension_color = (255, 200, 100)  # 橙色 - 警告
        else:
            tension_color = (100, 255, 100)  # 绿色 - 安全
            
        pygame.draw.rect(self.screen, tension_color, 
                         (tension_x, tension_y, tension_width * tension_pct, tension_height))
        
        # 张力条标签
        tension_text = f"鱼线张力: {int(self.player.tension)}/100"
        tension_surface = self.font_medium.render(tension_text, True, (255, 255, 255))
        self.screen.blit(tension_surface, (tension_x, tension_y - 25))
        
        # 绘制力度条
        power_y = panel_y + 150
        power_width = panel_width - 40
        power_height = 30
        power_x = panel_x + 20
        
        # 力度条背景
        pygame.draw.rect(self.screen, (60, 60, 60), 
                         (power_x, power_y, power_width, power_height))
        
        # 完美区域标记
        perfect_start_x = power_x + (self.player.perfect_zone_start / 100) * power_width
        perfect_end_x = power_x + (self.player.perfect_zone_end / 100) * power_width
        pygame.draw.rect(self.screen, (100, 255, 100), 
                         (perfect_start_x, power_y, perfect_end_x - perfect_start_x, power_height))
        
        # 当前力度指示器
        current_power_x = power_x + (self.player.reel_power / 100) * power_width
        pygame.draw.rect(self.screen, (255, 255, 255), 
                         (current_power_x - 2, power_y - 5, 4, power_height + 10))
        
        # 力度条标签
        power_text = f"收杆力度: {int(self.player.reel_power)}/100"
        power_surface = self.font_medium.render(power_text, True, (255, 255, 255))
        self.screen.blit(power_surface, (power_x, power_y - 25))
        
        # 绘制鱼的方向指示
        direction_y = panel_y + 200
        direction_names = ["↑ 上", "→ 右", "↓ 下", "← 左"]
        direction_text = f"鱼游向: {direction_names[self.player.fish_direction]}"
        direction_surface = self.font_medium.render(direction_text, True, (255, 255, 100))
        direction_x = panel_x + (panel_width - direction_surface.get_width()) // 2
        self.screen.blit(direction_surface, (direction_x, direction_y))
        
        # 绘制操作说明
        instructions = [
            "用 WASD 跟随鱼的游动方向",
            "按 空格键 收杆 (在绿色区域内效果最佳)",
            "保持张力避免断线或鱼逃跑"
        ]
        
        for i, instruction in enumerate(instructions):
            instruction_surface = self.font_small.render(instruction, True, (200, 200, 200))
            instruction_x = panel_x + 20
            instruction_y = panel_y + 230 + i * 18
            self.screen.blit(instruction_surface, (instruction_x, instruction_y))
        
        # 绘制时间进度条
        current_time = pygame.time.get_ticks()
        time_elapsed = current_time - self.player.minigame_timer
        time_progress = min(1.0, time_elapsed / self.player.max_minigame_time)
        
        time_bar_y = panel_y + panel_height - 15
        time_bar_width = panel_width - 40
        time_bar_x = panel_x + 20
        
        pygame.draw.rect(self.screen, (60, 60, 60), 
                         (time_bar_x, time_bar_y, time_bar_width, 10))
        pygame.draw.rect(self.screen, (255, 255, 0), 
                         (time_bar_x, time_bar_y, time_bar_width * time_progress, 10)) 