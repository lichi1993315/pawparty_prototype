import pygame

class TimeSystem:
    def __init__(self):
        self.minutes = 6 * 60  # Start at 6:00 AM
        self.day = 1
        self.season = "spring"
        self.year = 1
        self.season_days = 28
        self.seasons = ["spring", "summer", "fall", "winter"]
        
        # 季节的中文名称
        self.season_names_cn = {
            "spring": "春季",
            "summer": "夏季",
            "fall": "秋季",
            "winter": "冬季"
        }
        
        # Time tracking
        self.real_time_accumulator = 0
        self.last_time = pygame.time.get_ticks()
        self.time_scale = 16  # 16:1 ratio (real seconds to game minutes)
    
    def update(self):
        current_time = pygame.time.get_ticks()
        delta_time = (current_time - self.last_time) / 1000.0  # Convert to seconds
        self.last_time = current_time
        
        # Accumulate real time and convert to game time
        self.real_time_accumulator += delta_time
        
        # If we've accumulated enough real time for a game minute to pass
        if self.real_time_accumulator >= 1.0 / self.time_scale:
            game_minutes = int(self.real_time_accumulator * self.time_scale)
            self.minutes += game_minutes
            self.real_time_accumulator -= game_minutes / self.time_scale
            
            # Handle day change
            if self.minutes >= 24 * 60:
                self.minutes = 0
                self.advance_day()
    
    def advance_day(self):
        self.day += 1
        
        # Handle season change
        if self.day > self.season_days:
            self.day = 1
            season_index = (self.seasons.index(self.season) + 1) % len(self.seasons)
            self.season = self.seasons[season_index]
            
            # Handle year change
            if self.season == "spring":
                self.year += 1
    
    def get_time_string(self):
        hours = self.minutes // 60
        mins = self.minutes % 60
        # 使用24小时制显示，更符合中文习惯
        return f"{hours:02d}:{mins:02d}"
    
    def get_date_string(self):
        # 返回中文日期格式
        season_cn = self.season_names_cn.get(self.season, self.season.capitalize())
        return f"{season_cn} {self.day}日, 第{self.year}年"
    
    def is_sleep_time(self):
        return self.minutes >= 22 * 60 or self.minutes < 6 * 60 