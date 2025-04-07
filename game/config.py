class Config:
    def __init__(self):
        # Screen settings
        self.screen_width = 800
        self.screen_height = 600
        self.tile_size = 24  # Size of ASCII tiles
        
        # Map settings
        self.map_width = 50
        self.map_height = 40
        self.view_width = 20  # How many tiles to show horizontally
        self.view_height = 15  # How many tiles to show vertically
        
        # Player settings
        self.max_energy = 100
        self.energy_consumption = {
            "hoe": 2,
            "watering_can": 1,
            "seeds": 1,
            "harvest": 1,
            "fishing": 5,  # Per minute
            "gathering": 3,
            "mining": 5,
            "walking": 0.1
        }
        
        # Time settings
        self.time_scale = 16  # 16:1 ratio (1 real second = 16 game seconds)
        self.day_length = 24 * 60  # 24 hours in minutes
        self.sleep_time_start = 22 * 60  # 10 PM
        
        # Cat settings
        self.cat_follow_distance = 3
        self.cat_max_affection = 100
        self.cat_max_hunger = 100
        self.cat_hunger_rate = 0.05  # Per game minute
        
        # Farm settings
        self.crop_types = {
            "turnip": {
                "growth_time": 4,  # Days
                "value": 35,
                "season": "spring"
            },
            "potato": {
                "growth_time": 6,
                "value": 80,
                "season": "spring"
            },
            "tomato": {
                "growth_time": 8,
                "value": 60,
                "season": "summer"
            }
        }
        
        # Fish settings
        self.fish_types = {
            "anchovy": {
                "difficulty": 1,
                "value": 30,
                "season": "all"
            },
            "tuna": {
                "difficulty": 3,
                "value": 100,
                "season": "summer"
            },
            "salmon": {
                "difficulty": 4,
                "value": 150,
                "season": "fall"
            }
        }
        
        # Foraging items
        self.forage_types = {
            "mushroom": {
                "value": 40,
                "season": "fall"
            },
            "berry": {
                "value": 20,
                "season": "summer"
            },
            "herb": {
                "value": 10,
                "season": "all"
            }
        }
        
        # ASCII representation - 使用简单的ASCII字符替代特殊字符
        self.ascii_tiles = {
            "player": "@",
            "cat": "C",
            "water": "~",
            "grass": ".",
            "untilled_soil": ",",
            "tilled_soil": "#",
            "watered_soil": "=",
            "crop_stage_1": "1",
            "crop_stage_2": "2",
            "crop_stage_3": "3",
            "crop_ready": "$",
            "tree": "T",
            "rock": "O",
            "forage": "*",
            "house": "H",
            "npc": "&",
            "fence": "|",
            "fish_spot": "F"
        }
        
        # Colors (RGB)
        self.colors = {
            "player": (255, 255, 255),  # White
            "cat": (255, 165, 0),       # Orange
            "water": (30, 144, 255),    # Blue
            "grass": (0, 128, 0),       # Green
            "soil": (139, 69, 19),      # Brown
            "crop": (0, 255, 0),        # Bright green
            "tree": (34, 139, 34),      # Forest green
            "rock": (128, 128, 128),    # Gray
            "forage": (255, 0, 255),    # Magenta
            "house": (165, 42, 42),     # Brown
            "text": (255, 255, 255),    # White
            "energy": (255, 215, 0),    # Gold
            "time": (135, 206, 250),    # Light blue
            "fish_spot": (0, 191, 255)  # Deep sky blue
        } 