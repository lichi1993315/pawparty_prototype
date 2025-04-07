import pygame
from game.util import get_font

class UI:
    def __init__(self, screen, config, player, cat, time_system):
        self.screen = screen
        self.config = config
        self.player = player
        self.cat = cat
        self.time_system = time_system
        
        # UI state
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
        controls_text = "按键说明: [WASD]移动 [E]交互 [I]背包 [Enter]睡觉"
        controls_surface = self.font_small.render(controls_text, True, (200, 200, 200))
        self.screen.blit(controls_surface, (10, help_y))
    
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
        # Cat info panel in top right
        panel_width = 200
        panel_height = 80
        panel_x = self.screen.get_width() - panel_width - 10
        panel_y = 10
        
        pygame.draw.rect(self.screen, (0, 0, 0), 
                         (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, (50, 50, 50), 
                         (panel_x, panel_y, panel_width, panel_height), 1)
        
        # Cat stats (使用中文)
        affection_text = f"好感度: {int(self.cat.affection)}/{self.cat.max_affection}"
        hunger_text = f"饱食度: {int(self.cat.hunger)}/{self.cat.max_hunger}"
        
        # 行为翻译
        behavior_translations = {
            "follow": "跟随",
            "wander": "漫步",
            "sit": "休息"
        }
        behavior = behavior_translations.get(self.cat.current_behavior, self.cat.current_behavior.capitalize())
        behavior_text = f"状态: {behavior}"
        
        # Render text with Chinese font
        affection_surface = self.font_small.render(affection_text, True, self.config.colors["text"])
        hunger_surface = self.font_small.render(hunger_text, True, self.config.colors["text"])
        behavior_surface = self.font_small.render(behavior_text, True, self.config.colors["text"])
        
        # Draw bars for affection and hunger
        # Affection bar
        affection_pct = self.cat.affection / self.cat.max_affection
        bar_width = 150 * affection_pct
        pygame.draw.rect(self.screen, (100, 100, 100), 
                         (panel_x + 10, panel_y + 25, 150, 10))
        pygame.draw.rect(self.screen, (255, 105, 180), 
                         (panel_x + 10, panel_y + 25, bar_width, 10))
        
        # Hunger bar
        hunger_pct = self.cat.hunger / self.cat.max_hunger
        bar_width = 150 * hunger_pct
        pygame.draw.rect(self.screen, (100, 100, 100), 
                         (panel_x + 10, panel_y + 45, 150, 10))
        pygame.draw.rect(self.screen, (255, 165, 0), 
                         (panel_x + 10, panel_y + 45, bar_width, 10))
        
        # Draw text
        self.screen.blit(affection_surface, (panel_x + 10, panel_y + 5))
        self.screen.blit(hunger_surface, (panel_x + 10, panel_y + 35))
        self.screen.blit(behavior_surface, (panel_x + 10, panel_y + 60)) 