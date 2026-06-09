import os
import json
import pygame
from src.core.config import resource_path

# Theme Presets
THEME_PRESETS = {
    "Dark (Default)": {
        "editor.background": (14, 17, 23),
        "editor.foreground": (201, 209, 217),
        "sideBar.background": (22, 27, 34),
        "sideBar.border": (48, 54, 61),
        "button.background": (33, 38, 45),
        "button.foreground": (201, 209, 217),
        "button.hoverBackground": (48, 54, 61),
        "button.accentBackground": (35, 134, 54),
        "button.accentForeground": (255, 255, 255),
        "input.background": (13, 17, 23),
        "input.foreground": (201, 209, 217),
        "input.border": (48, 54, 61),
        "input.focusBorder": (88, 166, 255),
        "list.hoverBackground": (33, 38, 45),
        "list.activeSelectionBackground": (31, 111, 235),
        "list.activeSelectionForeground": (255, 255, 255),
        "syntax.keyword": (255, 123, 114),
        "syntax.type": (255, 123, 114),
        "syntax.name": (121, 192, 255),
        "syntax.number": (210, 168, 255),
        "syntax.comment": (139, 148, 158),
        "syntax.string": (165, 214, 255),
        "ports.clock": (0, 229, 255),
        "ports.reset": (255, 0, 127),
        "ports.reset_light": (255, 128, 191),
        "ports.input": (59, 130, 246),
        "ports.output": (16, 185, 129),
        "ports.inout": (245, 158, 11)
    },
    "Light": {
        "editor.background": (250, 250, 250),
        "editor.foreground": (36, 41, 47),
        "sideBar.background": (246, 248, 250),
        "sideBar.border": (208, 215, 222),
        "button.background": (243, 244, 246),
        "button.foreground": (36, 41, 47),
        "button.hoverBackground": (229, 231, 235),
        "button.accentBackground": (46, 164, 79),
        "button.accentForeground": (255, 255, 255),
        "input.background": (255, 255, 255),
        "input.foreground": (36, 41, 47),
        "input.border": (208, 215, 222),
        "input.focusBorder": (9, 105, 218),
        "list.hoverBackground": (234, 238, 242),
        "list.activeSelectionBackground": (9, 105, 218),
        "list.activeSelectionForeground": (255, 255, 255),
        "syntax.keyword": (207, 34, 46),
        "syntax.type": (207, 34, 46),
        "syntax.name": (5, 66, 138),
        "syntax.number": (5, 66, 138),
        "syntax.comment": (106, 115, 125),
        "syntax.string": (10, 48, 105),
        "ports.clock": (0, 150, 180),
        "ports.reset": (200, 0, 100),
        "ports.reset_light": (230, 100, 150),
        "ports.input": (9, 105, 218),
        "ports.output": (46, 164, 79),
        "ports.inout": (180, 100, 0)
    },
    "Solarized": {
        "editor.background": (7, 54, 66),
        "editor.foreground": (147, 161, 161),
        "sideBar.background": (0, 43, 54),
        "sideBar.border": (88, 110, 117),
        "button.background": (7, 54, 66),
        "button.foreground": (147, 161, 161),
        "button.hoverBackground": (88, 110, 117),
        "button.accentBackground": (133, 153, 0),
        "button.accentForeground": (253, 246, 227),
        "input.background": (0, 43, 54),
        "input.foreground": (131, 148, 150),
        "input.border": (88, 110, 117),
        "input.focusBorder": (38, 139, 210),
        "list.hoverBackground": (7, 54, 66),
        "list.activeSelectionBackground": (38, 139, 210),
        "list.activeSelectionForeground": (253, 246, 227),
        "syntax.keyword": (203, 75, 22),
        "syntax.type": (181, 137, 0),
        "syntax.name": (38, 139, 210),
        "syntax.number": (42, 161, 152),
        "syntax.comment": (101, 123, 131),
        "syntax.string": (42, 161, 152),
        "ports.clock": (42, 161, 152),
        "ports.reset": (220, 50, 47),
        "ports.reset_light": (211, 54, 130),
        "ports.input": (38, 139, 210),
        "ports.output": (133, 153, 0),
        "ports.inout": (181, 137, 0)
    }
}

class Theme:
    def __init__(self, theme_path=None):
        self.colors = {}
        self.fallback_colors = {
            "editor.background": (14, 17, 23),
            "editor.foreground": (201, 209, 217),
            "sideBar.background": (22, 27, 34),
            "sideBar.border": (48, 54, 61),
            "button.background": (33, 38, 45),
            "button.foreground": (201, 209, 217),
            "button.hoverBackground": (48, 54, 61),
            "button.accentBackground": (35, 134, 54),
            "button.accentForeground": (255, 255, 255),
            "input.background": (13, 17, 23),
            "input.foreground": (201, 209, 217),
            "input.border": (48, 54, 61),
            "input.focusBorder": (88, 166, 255),
            "list.hoverBackground": (33, 38, 45),
            "list.activeSelectionBackground": (31, 111, 235),
            "list.activeSelectionForeground": (255, 255, 255),
            "syntax.keyword": (255, 123, 114),
            "syntax.type": (255, 123, 114),
            "syntax.name": (121, 192, 255),
            "syntax.number": (210, 168, 255),
            "syntax.comment": (139, 148, 158),
            "syntax.string": (165, 214, 255),
            "ports.clock": (0, 229, 255),
            "ports.reset": (255, 0, 127),
            "ports.reset_light": (255, 128, 191),
            "ports.input": (59, 130, 246),
            "ports.output": (16, 185, 129),
            "ports.inout": (245, 158, 11)
        }
        self.fonts = {}
        self.sans_name = None
        self.mono_name = None
        self.load_theme(theme_path)

    def load_theme(self, theme_path):
        for k, v in self.fallback_colors.items():
            self.colors[k] = v

        if theme_path and os.path.exists(theme_path):
            try:
                with open(theme_path, 'r') as f:
                    data = json.load(f)
                for key, val in data.items():
                    if isinstance(val, str) and val.startswith("#"):
                        h = val.lstrip("#")
                        if len(h) == 6:
                            self.colors[key] = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
                        elif len(h) == 8:
                            self.colors[key] = tuple(int(h[i:i+2], 16) for i in (0, 2, 4, 6))
            except Exception as e:
                print(f"Warning: Failed to load theme file: {e}. Using defaults.")

    def apply_preset(self, preset_name):
        if preset_name in THEME_PRESETS:
            for k, v in THEME_PRESETS[preset_name].items():
                self.colors[k] = v

    def init_fonts(self, ui_scale=1.0):
        pygame.font.init()
        sys_sans = ["segoeui", "arial", "helvetica"]
        sys_mono = ["consolas", "sfmono", "couriernew", "courier"]
        
        sans_name = None
        for f in sys_sans:
            if f in pygame.font.get_fonts():
                sans_name = f
                break
                
        mono_name = None
        for f in sys_mono:
            if f in pygame.font.get_fonts():
                mono_name = f
                break

        self.sans_name = sans_name
        self.mono_name = mono_name

        self.fonts["header"] = pygame.font.SysFont(sans_name, int(20 * ui_scale), bold=True)
        self.fonts["body"] = pygame.font.SysFont(sans_name, int(14 * ui_scale))
        self.fonts["body_bold"] = pygame.font.SysFont(sans_name, int(14 * ui_scale), bold=True)
        self.fonts["small"] = pygame.font.SysFont(sans_name, int(11 * ui_scale))
        
        # Keep custom font sizes if already adjusted
        code_sz = self.fonts["code"].get_height() if "code" in self.fonts else 14
        # sys font height matches the requested size closely
        self.fonts["code"] = pygame.font.SysFont(mono_name, code_sz)
        self.fonts["code_large"] = pygame.font.SysFont(mono_name, code_sz + 2)

# Global theme instance
theme = Theme(resource_path("theme.json"))
image_cache = {}
