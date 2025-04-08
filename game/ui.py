import pygame
from game.util import get_font

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
    
    def add_notification(self, message, duration=180):  # 3 seconds at 60 FPS
        self.notifications.append({"message": message, "duration": duration})
    
    def toggle_inventory(self):
        self.show_inventory = not self.show_inventory
    
    def show_cat_interaction_menu(self):
        """显示与猫互动的菜单"""
        self.show_interaction_menu = True
        self.interaction_options = ["抚摸", "喂食", "举起", "取消"]
        self.selected_interaction = 0
    
    def hide_interaction_menu(self):
        """隐藏交互菜单"""
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
        """切换文本输入框的显示状态"""
        self.show_text_input = not self.show_text_input
        if self.show_text_input:
            self.input_active = True
            self.input_text = ""  # 重置输入文本
        else:
            self.input_active = False
    
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
        
        # Draw game controls help
        help_y = self.screen.get_height() - 60
        controls_text = "按键说明: [WASD]移动 [E]交互 [I]背包 [T]对话 [Enter]睡觉"
        controls_surface = self.font_small.render(controls_text, True, (200, 200, 200))
        self.screen.blit(controls_surface, (10, help_y))
        
        # 绘制交互菜单
        if self.show_interaction_menu:
            self.draw_interaction_menu()
            
        # 绘制文本输入框
        if self.show_text_input:
            self.draw_text_input()
    
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
        # Update notification timers and remove expired ones
        i = 0
        while i < len(self.notifications):
            self.notifications[i]["duration"] -= 1
            if self.notifications[i]["duration"] <= 0:
                self.notifications.pop(i)
            else:
                i += 1
        
        # Draw active notifications
        y_offset = 10
        for notification in self.notifications:
            message = notification["message"]
            
            # Calculate alpha based on remaining duration
            alpha = min(255, notification["duration"] * 3)
            
            # Create a text surface with Chinese font
            text_surface = self.font_medium.render(message, True, self.config.colors["text"])
            
            # Create a transparent surface for the background
            background = pygame.Surface((text_surface.get_width() + 20, text_surface.get_height() + 10))
            background.set_alpha(150)
            background.fill((0, 0, 0))
            
            # Position in center top
            x = (self.screen.get_width() - text_surface.get_width()) // 2
            
            # Draw background and text
            self.screen.blit(background, (x - 10, y_offset))
            self.screen.blit(text_surface, (x, y_offset + 5))
            
            y_offset += text_surface.get_height() + 15
    
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