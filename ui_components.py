import pygame
import json
import os
import time
import tkinter as tk
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# Translations system
current_language = "en"

TRANSLATIONS = {
    "en": {
        "title": "SystemVerilog Designer",
        "module_name": "Module Name:",
        "active_low": "Active Low Reset",
        "sync_reset": "Synchronous Reset",
        "add_clk": "Add Clock",
        "add_rst": "Add Reset",
        "tb_settings": "Testbench Settings",
        "module_ports": "Module Ports",
        "Standalone": "Standalone",
        "With Master": "With Master",
        "Block Diagram": "Block Diagram",
        "Code Preview": "Code Preview",
        "Paste or Import": "Paste or Import",
        "Module Code": "Module Code",
        "Testbench Code": "Testbench Code",
        "Master TB Code": "Master TB Code",
        "Import SV File": "Import SV File",
        "Parse Pasted Code": "Parse Pasted Code",
        "Copy Code": "Copy Code",
        "Preferences": "Preferences",
        "pref_title": "Preferences",
        "pref_ui_scale": "UI Size:",
        "pref_lang": "Language:",
        "pref_editor_size": "Editor Font Size:",
        "pref_theme": "Theme:",
        "Close": "Close",
        "Active Low Reset": "Active Low Reset",
        "Synchronous Reset": "Synchronous Reset",
        "Add Clock": "Add Clock",
        "Add Reset": "Add Reset",
        "+ Input": "+ Input",
        "+ Output": "+ Output",
        "close": "Close",
    },
    "fr": {
        "title": "Concepteur SystemVerilog",
        "module_name": "Nom du Module :",
        "active_low": "Reset Actif Bas",
        "sync_reset": "Reset Synchrone",
        "add_clk": "Ajouter Horloge",
        "add_rst": "Ajouter Reset",
        "tb_settings": "Paramètres Testbench",
        "module_ports": "Ports du Module",
        "Standalone": "Autonome",
        "With Master": "Avec Master",
        "Block Diagram": "Schéma Bloc",
        "Code Preview": "Aperçu du Code",
        "Paste or Import": "Coller ou Importer",
        "Module Code": "Code Module",
        "Testbench Code": "Code Testbench",
        "Master TB Code": "Code Master TB",
        "Import SV File": "Importer Fichier SV",
        "Parse Pasted Code": "Analyser Code Collé",
        "Copy Code": "Copier Code",
        "Preferences": "Préférences",
        "pref_title": "Préférences",
        "pref_ui_scale": "Taille UI :",
        "pref_lang": "Langue :",
        "pref_editor_size": "Taille Code :",
        "pref_theme": "Thème :",
        "Close": "Fermer",
        "Active Low Reset": "Reset Actif Bas",
        "Synchronous Reset": "Reset Synchrone",
        "Add Clock": "Ajouter Horloge",
        "Add Reset": "Ajouter Reset",
        "+ Input": "+ Entrée",
        "+ Output": "+ Sortie",
        "close": "Fermer",
    }
}

def tr(key):
    if key in TRANSLATIONS[current_language]:
        return TRANSLATIONS[current_language][key]
    return key

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

# Tkinter clipboard access
def get_clipboard_text():
    try:
        root = tk.Tk()
        root.withdraw()
        text = root.clipboard_get()
        root.destroy()
        return text
    except Exception:
        return ""

def set_clipboard_text(text):
    try:
        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        root.destroy()
    except Exception:
        pass

def find_word_boundary(text, pos, direction):
    """
    Finds word boundaries for Ctrl+Arrow movement/deletion.
    direction: -1 for left, 1 for right.
    """
    if direction == -1:
        i = pos - 1
        while i >= 0 and text[i].isspace():
            i -= 1
        if i >= 0:
            is_al = text[i].isalnum() or text[i] == '_'
            while i >= 0 and ((text[i].isalnum() or text[i] == '_') == is_al) and not text[i].isspace():
                i -= 1
        return i + 1
    else:
        i = pos
        while i < len(text) and text[i].isspace():
            i += 1
        if i < len(text):
            is_al = text[i].isalnum() or text[i] == '_'
            while i < len(text) and ((text[i].isalnum() or text[i] == '_') == is_al) and not text[i].isspace():
                i += 1
        return i

class Theme:
    def __init__(self, theme_path=None):
        self.colors = {}
        # Built-in fallback theme
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
        
        if "code" not in self.fonts:
            self.fonts["code"] = pygame.font.SysFont(mono_name, 14)
        if "code_large" not in self.fonts:
            self.fonts["code_large"] = pygame.font.SysFont(mono_name, 16)

# Globals for access
theme = Theme(resource_path("theme.json"))
image_cache = {}

def draw_highlighted_line(surface, font, line_text, x, y):
    import re
    words = re.split(r'(\s+|[;,().#`]|//.*)', line_text)
    curr_x = x
    
    for word in words:
        if not word:
            continue
            
        color = theme.colors["editor.foreground"]
        
        if word.startswith("//"):
            color = theme.colors["syntax.comment"]
        elif word in ["module", "endmodule", "input", "output", "inout", "logic", "reg", "wire", "parameter", "localparam", "initial", "begin", "end", "always", "forever", "wait", "posedge", "negedge", "repeat", "timescale", "`timescale", "task", "endtask"]:
            color = theme.colors["syntax.keyword"]
        elif word.startswith("`"):
            color = theme.colors["syntax.keyword"]
        elif word.replace("_","").isalnum() and word[0].isalpha() and word not in ["logic","reg","wire"]:
            color = theme.colors["syntax.name"]
        elif word.isdigit() or word.startswith("'h") or word.startswith("'d") or word.startswith("'b") or (len(word) > 1 and word[1] == "'"):
            color = theme.colors["syntax.number"]
        elif word.startswith('"') and word.endswith('"'):
            color = theme.colors["syntax.string"]
            
        w_surf = font.render(word, True, color)
        surface.blit(w_surf, (curr_x, y))
        curr_x += w_surf.get_width()

class Widget:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.focused = False
        self.hovered = False

    def handle_event(self, event, offset_mouse_pos=None):
        pass

    def update(self):
        pass

    def draw(self, surface):
        pass

class Button(Widget):
    def __init__(self, rect, text, callback=None, is_accent=False, bg_color_key=None, icon=None, no_bg=False, fg_color_key=None, hover_fg_color_key=None):
        super().__init__(rect)
        self.text = text
        self.callback = callback
        self.is_accent = is_accent
        self.bg_color_key = bg_color_key
        self.icon = icon
        self.no_bg = no_bg
        self.fg_color_key = fg_color_key
        self.hover_fg_color_key = hover_fg_color_key
        self.alpha_hover = 0
        
    def handle_event(self, event, offset_mouse_pos=None):
        pos = offset_mouse_pos if offset_mouse_pos else pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and self.callback:
                pygame.key.start_text_input()
                self.callback()
                return True
        return False

    def update(self):
        target = 255 if self.hovered else 0
        if self.alpha_hover != target:
            diff = target - self.alpha_hover
            step = 30 if diff > 0 else -30
            if abs(diff) <= abs(step):
                self.alpha_hover = target
            else:
                self.alpha_hover += step

    def draw(self, surface):
        global image_cache
        factor = self.alpha_hover / 255.0

        if self.no_bg:
            base_fg = theme.colors[self.fg_color_key] if self.fg_color_key else theme.colors["button.foreground"]
            hover_fg = theme.colors[self.hover_fg_color_key] if self.hover_fg_color_key else theme.colors["ports.reset"]
            fg_curr = tuple(int(base_fg[i] * (1 - factor) + hover_fg[i] * factor) for i in range(3))
            
            if self.icon == "X":
                cx, cy = self.rect.center
                size = 5
                pygame.draw.line(surface, fg_curr, (cx - size, cy - size), (cx + size, cy + size), 2)
                pygame.draw.line(surface, fg_curr, (cx + size, cy - size), (cx - size, cy + size), 2)
            else:
                font = theme.fonts["body"]
                txt_surf = font.render(tr(self.text), True, fg_curr)
                txt_rect = txt_surf.get_rect(center=self.rect.center)
                surface.blit(txt_surf, txt_rect)
        else:
            # Standard background button
            if self.icon == "save":
                # Lighter background based on theme border so it stands out
                bg_base = theme.colors["sideBar.border"]
                bg_hover = tuple(min(255, int(c * 1.25)) if c > 50 else min(255, int(c * 1.6)) for c in bg_base)
                fg_color = theme.colors["button.accentForeground"]
            elif self.bg_color_key:
                bg_base = theme.colors[self.bg_color_key]
            elif self.is_accent:
                bg_base = theme.colors["button.accentBackground"]
            else:
                bg_base = theme.colors["button.background"]

            if self.icon != "save":
                fg_color = theme.colors["button.accentForeground"] if (self.is_accent or self.bg_color_key) else theme.colors["button.foreground"]
            
            if self.icon == "save":
                pass
            elif self.is_accent:
                bg_hover = tuple(min(255, int(c * 1.2)) for c in bg_base)
            elif self.bg_color_key:
                bg_hover = tuple(min(255, int(c * 1.2)) for c in bg_base)
            else:
                bg_hover = theme.colors["button.hoverBackground"]

            bg_curr = tuple(int(bg_base[i] * (1 - factor) + bg_hover[i] * factor) for i in range(3))

            pygame.draw.rect(surface, bg_curr, self.rect, border_radius=6)
            border_color = theme.colors["sideBar.border"]
            pygame.draw.rect(surface, border_color, self.rect, width=1, border_radius=6)

            if self.icon == "save":
                # Check for diskette.png in assets/images/
                path = resource_path(os.path.join("assets", "images", "diskette.png"))
                if path not in image_cache:
                    if os.path.exists(path):
                        try:
                            image_cache[path] = pygame.image.load(path).convert_alpha()
                        except Exception:
                            image_cache[path] = None
                    else:
                        # Auto generate if missing (as floppy disk icon)
                        # We save it as diskette.png first
                        try:
                            os.makedirs(os.path.dirname(path), exist_ok=True)
                            temp_s = pygame.Surface((32, 32), pygame.SRCALPHA)
                            # Draw floppy shape
                            pygame.draw.rect(temp_s, (201, 209, 217), (4, 4, 24, 24), border_radius=2)
                            pygame.draw.rect(temp_s, (20, 24, 33), (8, 6, 16, 6))
                            pygame.draw.rect(temp_s, (20, 24, 33), (10, 18, 12, 10))
                            pygame.image.save(temp_s, path)
                            image_cache[path] = temp_s
                        except Exception:
                            image_cache[path] = None
                
                img = image_cache[path]
                if img:
                    # Render loaded scaled icon image (Almost full frame, e.g. padding of 4px)
                    sz_w = self.rect.width - 8
                    sz_h = self.rect.height - 8
                    scaled = pygame.transform.smoothscale(img, (sz_w, sz_h))
                    r_img = scaled.get_rect(center=self.rect.center)
                    surface.blit(scaled, r_img)
                else:
                    # Simple fallback floppy disk shape
                    r = self.rect.inflate(-8, -6)
                    pygame.draw.rect(surface, fg_color, r, width=2, border_radius=2)
                    lbl_r = pygame.Rect(r.x + 4, r.y + 2, r.width - 8, 4)
                    pygame.draw.rect(surface, fg_color, lbl_r, width=1)
                    sld_r = pygame.Rect(r.x + 5, r.bottom - 7, 5, 7)
                    pygame.draw.rect(surface, fg_color, sld_r)
            else:
                font = theme.fonts["body_bold"] if self.is_accent else theme.fonts["body"]
                txt_surf = font.render(tr(self.text), True, fg_color)
                txt_rect = txt_surf.get_rect(center=self.rect.center)
                surface.blit(txt_surf, txt_rect)

class ToggleButton(Widget):
    def __init__(self, rect, options, initial_index=0, callback=None):
        super().__init__(rect)
        self.options = options
        self.index = initial_index
        self.callback = callback

    def handle_event(self, event, offset_mouse_pos=None):
        pos = offset_mouse_pos if offset_mouse_pos else pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.index = (self.index + 1) % len(self.options)
                if self.callback:
                    self.callback(self.options[self.index])
                return True
        return False

    def getValue(self):
        return self.options[self.index]

    def setValue(self, val):
        if val in self.options:
            self.index = self.options.index(val)

    def draw(self, surface):
        bg_base = theme.colors["button.background"]
        if self.hovered:
            bg_base = theme.colors["button.hoverBackground"]

        pygame.draw.rect(surface, bg_base, self.rect, border_radius=6)
        border_color = theme.colors["sideBar.border"]
        pygame.draw.rect(surface, border_color, self.rect, width=1, border_radius=6)

        val_str = self.options[self.index]
        
        if val_str == "IN":
            fg_color = theme.colors["ports.input"]
        elif val_str == "OUT":
            fg_color = theme.colors["ports.output"]
        elif val_str == "With Master":
            fg_color = theme.colors["ports.clock"]
        else:
            fg_color = theme.colors["button.foreground"]

        font = theme.fonts["body_bold"]
        txt_surf = font.render(tr(val_str), True, fg_color)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

class InputBox(Widget):
    def __init__(self, rect, text="", placeholder="", is_number_range=False, max_len=60):
        super().__init__(rect)
        self.text = text
        self.placeholder = placeholder
        self.is_number_range = is_number_range
        self.max_len = max_len
        
        self.cursor_pos = len(text)
        self.select_start = -1
        self.select_end = -1
        self.is_dragging_selection = False
        
        self.cursor_visible = True
        self.last_blink = time.time()
        self.last_click_time = 0
        
    def get_selection_range(self):
        if self.select_start != -1 and self.select_end != -1 and self.select_start != self.select_end:
            return min(self.select_start, self.select_end), max(self.select_start, self.select_end)
        return None
        
    def delete_selection(self):
        sel = self.get_selection_range()
        if sel:
            self.text = self.text[:sel[0]] + self.text[sel[1]:]
            self.cursor_pos = sel[0]
            self.select_start = -1
            self.select_end = -1
            return True
        return False

    def handle_event(self, event, offset_mouse_pos=None):
        pos = offset_mouse_pos if offset_mouse_pos else pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            old_focus = self.focused
            self.focused = self.hovered
            
            if self.focused:
                pygame.key.start_text_input()
                curr_time = time.time()
                
                if curr_time - self.last_click_time < 0.28:
                    self.select_start = 0
                    self.select_end = len(self.text)
                    self.cursor_pos = len(self.text)
                else:
                    self.cursor_pos = self.estimate_cursor_pos(pos[0] - self.rect.x - 8)
                    self.select_start = self.cursor_pos
                    self.select_end = self.cursor_pos
                    self.is_dragging_selection = True
                    
                self.last_blink = time.time()
                self.cursor_visible = True
                self.last_click_time = curr_time
            elif old_focus:
                pygame.key.stop_text_input()
            return self.focused

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_dragging_selection = False
            if self.select_start == self.select_end:
                self.select_start = -1
                self.select_end = -1

        elif event.type == pygame.MOUSEMOTION:
            if self.focused and self.is_dragging_selection:
                self.select_end = self.estimate_cursor_pos(pos[0] - self.rect.x - 8)
                self.cursor_pos = self.select_end

        elif self.focused and event.type == pygame.KEYDOWN:
            self.last_blink = time.time()
            self.cursor_visible = True
            
            mods = pygame.key.get_mods()
            shift_pressed = bool(mods & pygame.KMOD_SHIFT)
            ctrl_pressed = bool(mods & pygame.KMOD_CTRL)
            old_pos = self.cursor_pos

            # A. Clipboard / Selection shortcuts
            if ctrl_pressed:
                if event.key == pygame.K_a:
                    self.select_start = 0
                    self.select_end = len(self.text)
                    self.cursor_pos = len(self.text)
                    return True
                elif event.key == pygame.K_c:
                    sel = self.get_selection_range()
                    text_to_copy = self.text[sel[0]:sel[1]] if sel else self.text
                    set_clipboard_text(text_to_copy)
                    return True
                elif event.key == pygame.K_v:
                    self.delete_selection()
                    clip_text = get_clipboard_text()
                    clip_text = "".join(c for c in clip_text if self.char_allowed(c))
                    if len(self.text) + len(clip_text) <= self.max_len:
                        self.text = self.text[:self.cursor_pos] + clip_text + self.text[self.cursor_pos:]
                        self.cursor_pos += len(clip_text)
                    return True

            # B. Backspace / Delete (supports Ctrl deletion)
            if event.key == pygame.K_BACKSPACE:
                if not self.delete_selection():
                    if ctrl_pressed:
                        left_b = find_word_boundary(self.text, self.cursor_pos, -1)
                        self.text = self.text[:left_b] + self.text[self.cursor_pos:]
                        self.cursor_pos = left_b
                    else:
                        if self.cursor_pos > 0:
                            self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                            self.cursor_pos -= 1
                return True
                
            elif event.key == pygame.K_DELETE:
                if not self.delete_selection():
                    if ctrl_pressed:
                        right_b = find_word_boundary(self.text, self.cursor_pos, 1)
                        self.text = self.text[:self.cursor_pos] + self.text[right_b:]
                    else:
                        if self.cursor_pos < len(self.text):
                            self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
                return True

            # C. Cursor Navigation (supports Ctrl selection, Shift selection)
            elif event.key == pygame.K_LEFT:
                if ctrl_pressed:
                    new_pos = find_word_boundary(self.text, self.cursor_pos, -1)
                else:
                    new_pos = max(0, self.cursor_pos - 1)
                    
                if shift_pressed:
                    if self.select_start == -1: self.select_start = old_pos
                    self.cursor_pos = new_pos
                    self.select_end = self.cursor_pos
                else:
                    self.select_start = -1; self.select_end = -1
                    self.cursor_pos = new_pos
                return True
                
            elif event.key == pygame.K_RIGHT:
                if ctrl_pressed:
                    new_pos = find_word_boundary(self.text, self.cursor_pos, 1)
                else:
                    new_pos = min(len(self.text), self.cursor_pos + 1)
                    
                if shift_pressed:
                    if self.select_start == -1: self.select_start = old_pos
                    self.cursor_pos = new_pos
                    self.select_end = self.cursor_pos
                else:
                    self.select_start = -1; self.select_end = -1
                    self.cursor_pos = new_pos
                return True
                
            elif event.key == pygame.K_HOME:
                if shift_pressed:
                    if self.select_start == -1: self.select_start = old_pos
                    self.cursor_pos = 0
                    self.select_end = 0
                else:
                    self.select_start = -1; self.select_end = -1
                    self.cursor_pos = 0
                return True
                
            elif event.key == pygame.K_END:
                if shift_pressed:
                    if self.select_start == -1: self.select_start = old_pos
                    self.cursor_pos = len(self.text)
                    self.select_end = len(self.text)
                else:
                    self.select_start = -1; self.select_end = -1
                    self.cursor_pos = len(self.text)
                return True

        elif self.focused and event.type == pygame.TEXTINPUT:
            self.delete_selection()
            self.last_blink = time.time()
            self.cursor_visible = True
            chars = "".join(c for c in event.text if self.char_allowed(c))
            if len(self.text) + len(chars) <= self.max_len:
                self.text = self.text[:self.cursor_pos] + chars + self.text[self.cursor_pos:]
                self.cursor_pos += len(chars)
            return True

        return False

    def char_allowed(self, c):
        if self.is_number_range:
            return c.isalnum() or c in "[:]-+_"
        else:
            return c.isalnum() or c in "_"

    def estimate_cursor_pos(self, click_x):
        font = theme.fonts["code"]
        best_pos = 0
        best_diff = float('inf')
        for i in range(len(self.text) + 1):
            w, _ = font.size(self.text[:i])
            diff = abs(w - click_x)
            if diff < best_diff:
                best_diff = diff
                best_pos = i
        return best_pos

    def update(self):
        if self.focused:
            if time.time() - self.last_blink > 0.5:
                self.cursor_visible = not self.cursor_visible
                self.last_blink = time.time()

    def draw(self, surface):
        bg_color = theme.colors["input.background"]
        border_color = theme.colors["input.focusBorder"] if self.focused else theme.colors["input.border"]
        
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=6)
        pygame.draw.rect(surface, border_color, self.rect, width=1, border_radius=6)

        prev_clip = surface.get_clip()
        surface.set_clip(self.rect.inflate(-4, -4))

        font = theme.fonts["code"]
        text_color = theme.colors["input.foreground"]
        
        sel = self.get_selection_range()
        if sel:
            sel_min, sel_max = sel
            w_before, _ = font.size(self.text[:sel_min])
            w_sel, _ = font.size(self.text[sel_min:sel_max])
            if w_sel > 0:
                highlight_surf = pygame.Surface((w_sel, self.rect.height - 8), pygame.SRCALPHA)
                highlight_surf.fill((31, 111, 235, 120))
                surface.blit(highlight_surf, (self.rect.x + 8 + w_before, self.rect.y + 4))
        
        if self.text == "" and not self.focused:
            ph_surf = font.render(self.placeholder, True, theme.colors["syntax.comment"])
            surface.blit(ph_surf, (self.rect.x + 8, self.rect.y + (self.rect.height - ph_surf.get_height())//2))
        else:
            txt_surf = font.render(self.text, True, text_color)
            surface.blit(txt_surf, (self.rect.x + 8, self.rect.y + (self.rect.height - txt_surf.get_height())//2))
            
            if self.focused and self.cursor_visible:
                cursor_offset_x, _ = font.size(self.text[:self.cursor_pos])
                cx = self.rect.x + 8 + cursor_offset_x
                cy1 = self.rect.y + 6
                cy2 = self.rect.y + self.rect.height - 6
                pygame.draw.line(surface, text_color, (cx, cy1), (cx, cy2), 1)

        surface.set_clip(prev_clip)

class TextArea(Widget):
    """
    Highly advanced multi-line select-copy-paste-scroll code editor widget.
    Can be loaded in read-only mode for the generated code preview.
    """
    def __init__(self, rect, text="", placeholder="", read_only=False, syntax_highlight=False):
        super().__init__(rect)
        self.text = text
        self.placeholder = placeholder
        self.read_only = read_only
        self.syntax_highlight = syntax_highlight
        self.scroll_y = 0
        self.virtual_height = 0
        self.line_h = 18
        
        self.cursor_pos = len(text)
        self.select_start = -1
        self.select_end = -1
        self.is_dragging_selection = False
        
        self.last_blink = time.time()
        self.cursor_visible = True
        self.last_click_time = 0

    def get_selection_range(self):
        if self.select_start != -1 and self.select_end != -1 and self.select_start != self.select_end:
            return min(self.select_start, self.select_end), max(self.select_start, self.select_end)
        return None
        
    def delete_selection(self):
        if self.read_only:
            return False
        sel = self.get_selection_range()
        if sel:
            self.text = self.text[:sel[0]] + self.text[sel[1]:]
            self.cursor_pos = sel[0]
            self.select_start = -1
            self.select_end = -1
            return True
        return False

    def get_line_col(self, idx):
        lines = self.text.split("\n")
        curr = 0
        for line_idx, line in enumerate(lines):
            if curr <= idx <= curr + len(line):
                return line_idx, idx - curr
            curr += len(line) + 1
        return len(lines) - 1, len(lines[-1])

    def get_idx(self, line_idx, col):
        lines = self.text.split("\n")
        curr = 0
        for i in range(min(line_idx, len(lines))):
            curr += len(lines[i]) + 1
        if line_idx < len(lines):
            return curr + min(col, len(lines[line_idx]))
        return curr

    def handle_event(self, event, offset_mouse_pos=None):
        pos = offset_mouse_pos if offset_mouse_pos else pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(pos)

        # Mouse clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4 and self.hovered:
                self.scroll_y = max(0, self.scroll_y - self.line_h * 2)
                return True
            elif event.button == 5 and self.hovered:
                max_scroll = max(0, self.virtual_height - self.rect.height + 16)
                self.scroll_y = min(max_scroll, self.scroll_y + self.line_h * 2)
                return True
            elif event.button == 1:
                old_focus = self.focused
                self.focused = self.hovered
                if self.focused:
                    pygame.key.start_text_input()
                    curr_time = time.time()
                    if curr_time - self.last_click_time < 0.28:
                        self.select_start = 0
                        self.select_end = len(self.text)
                        self.cursor_pos = len(self.text)
                    else:
                        lines = self.text.split("\n")
                        line_idx = (pos[1] - self.rect.y - 8 + self.scroll_y) // self.line_h
                        line_idx = max(0, min(len(lines) - 1, line_idx))
                        col = self.estimate_cursor_col(lines[line_idx], pos[0] - self.rect.x - 8)
                        self.cursor_pos = self.get_idx(line_idx, col)
                        self.select_start = self.cursor_pos
                        self.select_end = self.cursor_pos
                        self.is_dragging_selection = True
                    self.last_blink = time.time()
                    self.cursor_visible = True
                    self.last_click_time = curr_time
                elif old_focus:
                    pygame.key.stop_text_input()
                return self.focused

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_dragging_selection = False
            if self.select_start == self.select_end:
                self.select_start = -1
                self.select_end = -1

        elif event.type == pygame.MOUSEMOTION:
            if self.focused and self.is_dragging_selection:
                lines = self.text.split("\n")
                line_idx = (pos[1] - self.rect.y - 8 + self.scroll_y) // self.line_h
                line_idx = max(0, min(len(lines) - 1, line_idx))
                col = self.estimate_cursor_col(lines[line_idx], pos[0] - self.rect.x - 8)
                self.select_end = self.get_idx(line_idx, col)
                self.cursor_pos = self.select_end

        # Keyboard actions
        elif self.focused and event.type == pygame.KEYDOWN:
            self.last_blink = time.time()
            self.cursor_visible = True
            
            mods = pygame.key.get_mods()
            shift_pressed = bool(mods & pygame.KMOD_SHIFT)
            ctrl_pressed = bool(mods & pygame.KMOD_CTRL)
            old_pos = self.cursor_pos

            # Ctrl shortcuts
            if ctrl_pressed:
                if event.key == pygame.K_a:
                    self.select_start = 0
                    self.select_end = len(self.text)
                    self.cursor_pos = len(self.text)
                    return True
                elif event.key == pygame.K_c:
                    sel = self.get_selection_range()
                    text_to_copy = self.text[sel[0]:sel[1]] if sel else self.text
                    set_clipboard_text(text_to_copy)
                    return True
                elif event.key == pygame.K_v and not self.read_only:
                    self.delete_selection()
                    clip_text = get_clipboard_text()
                    clip_text = "".join(c for c in clip_text if self.char_allowed(c))
                    self.text = self.text[:self.cursor_pos] + clip_text + self.text[self.cursor_pos:]
                    self.cursor_pos += len(clip_text)
                    self.auto_scroll_to_cursor()
                    return True

            if self.read_only:
                # Restrict modifying keys in read-only mode
                if event.key not in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_HOME, pygame.K_END, pygame.K_c]:
                    return False

            # Modifying keys (Write mode only)
            if not self.read_only:
                if event.key == pygame.K_BACKSPACE:
                    if not self.delete_selection():
                        if ctrl_pressed:
                            left_b = find_word_boundary(self.text, self.cursor_pos, -1)
                            self.text = self.text[:left_b] + self.text[self.cursor_pos:]
                            self.cursor_pos = left_b
                        else:
                            if self.cursor_pos > 0:
                                self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                                self.cursor_pos -= 1
                    self.auto_scroll_to_cursor()
                    return True
                    
                elif event.key == pygame.K_DELETE:
                    if not self.delete_selection():
                        if ctrl_pressed:
                            right_b = find_word_boundary(self.text, self.cursor_pos, 1)
                            self.text = self.text[:self.cursor_pos] + self.text[right_b:]
                        else:
                            if self.cursor_pos < len(self.text):
                                self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
                    self.auto_scroll_to_cursor()
                    return True
                    
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    self.delete_selection()
                    self.text = self.text[:self.cursor_pos] + "\n" + self.text[self.cursor_pos:]
                    self.cursor_pos += 1
                    self.auto_scroll_to_cursor()
                    return True

            # Cursor movements
            lines = self.text.split("\n")
            line_idx, col = self.get_line_col(self.cursor_pos)
            
            if event.key == pygame.K_LEFT:
                if ctrl_pressed:
                    new_pos = find_word_boundary(self.text, self.cursor_pos, -1)
                else:
                    new_pos = max(0, self.cursor_pos - 1)
                    
                if shift_pressed:
                    if self.select_start == -1: self.select_start = old_pos
                    self.cursor_pos = new_pos
                    self.select_end = self.cursor_pos
                else:
                    self.select_start = -1; self.select_end = -1
                    self.cursor_pos = new_pos
                self.auto_scroll_to_cursor()
                return True
                
            elif event.key == pygame.K_RIGHT:
                if ctrl_pressed:
                    new_pos = find_word_boundary(self.text, self.cursor_pos, 1)
                else:
                    new_pos = min(len(self.text), self.cursor_pos + 1)
                    
                if shift_pressed:
                    if self.select_start == -1: self.select_start = old_pos
                    self.cursor_pos = new_pos
                    self.select_end = self.cursor_pos
                else:
                    self.select_start = -1; self.select_end = -1
                    self.cursor_pos = new_pos
                self.auto_scroll_to_cursor()
                return True
                
            elif event.key == pygame.K_UP:
                if line_idx > 0:
                    new_line = line_idx - 1
                    new_col = min(col, len(lines[new_line]))
                    new_pos = self.get_idx(new_line, new_col)
                    if shift_pressed:
                        if self.select_start == -1: self.select_start = old_pos
                        self.cursor_pos = new_pos
                        self.select_end = self.cursor_pos
                    else:
                        self.select_start = -1; self.select_end = -1
                        self.cursor_pos = new_pos
                self.auto_scroll_to_cursor()
                return True
                
            elif event.key == pygame.K_DOWN:
                if line_idx < len(lines) - 1:
                    new_line = line_idx + 1
                    new_col = min(col, len(lines[new_line]))
                    new_pos = self.get_idx(new_line, new_col)
                    if shift_pressed:
                        if self.select_start == -1: self.select_start = old_pos
                        self.cursor_pos = new_pos
                        self.select_end = self.cursor_pos
                    else:
                        self.select_start = -1; self.select_end = -1
                        self.cursor_pos = new_pos
                self.auto_scroll_to_cursor()
                return True
                
            elif event.key == pygame.K_HOME:
                new_pos = self.get_idx(line_idx, 0)
                if shift_pressed:
                    if self.select_start == -1: self.select_start = old_pos
                    self.cursor_pos = new_pos
                    self.select_end = self.cursor_pos
                else:
                    self.select_start = -1; self.select_end = -1
                    self.cursor_pos = new_pos
                self.auto_scroll_to_cursor()
                return True
                
            elif event.key == pygame.K_END:
                new_pos = self.get_idx(line_idx, len(lines[line_idx]))
                if shift_pressed:
                    if self.select_start == -1: self.select_start = old_pos
                    self.cursor_pos = new_pos
                    self.select_end = self.cursor_pos
                else:
                    self.select_start = -1; self.select_end = -1
                    self.cursor_pos = new_pos
                self.auto_scroll_to_cursor()
                return True

        elif self.focused and event.type == pygame.TEXTINPUT and not self.read_only:
            self.delete_selection()
            self.last_blink = time.time()
            self.cursor_visible = True
            chars = "".join(c for c in event.text if self.char_allowed(c))
            self.text = self.text[:self.cursor_pos] + chars + self.text[self.cursor_pos:]
            self.cursor_pos += len(chars)
            self.auto_scroll_to_cursor()
            return True

        return False

    def char_allowed(self, c):
        return c == "\n" or c == "\t" or c.isprintable()

    def estimate_cursor_col(self, line_text, click_x):
        font = theme.fonts["code"]
        best_col = 0
        best_diff = float('inf')
        for i in range(len(line_text) + 1):
            w, _ = font.size(line_text[:i])
            diff = abs(w - click_x)
            if diff < best_diff:
                best_diff = diff
                best_col = i
        return best_col

    def auto_scroll_to_cursor(self):
        line_idx, _ = self.get_line_col(self.cursor_pos)
        ly = line_idx * self.line_h
        if ly < self.scroll_y:
            self.scroll_y = ly
        elif ly + self.line_h > self.scroll_y + self.rect.height - 16:
            self.scroll_y = ly + self.line_h - self.rect.height + 16

    def update(self):
        lines = self.text.split("\n")
        self.virtual_height = len(lines) * self.line_h
        if self.focused:
            if time.time() - self.last_blink > 0.5:
                self.cursor_visible = not self.cursor_visible
                self.last_blink = time.time()

    def draw(self, surface):
        bg_color = theme.colors["input.background"]
        border_color = theme.colors["input.focusBorder"] if self.focused else theme.colors["input.border"]
        
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=12)
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=12)
        
        prev_clip = surface.get_clip()
        surface.set_clip(self.rect.inflate(-4, -4))
        
        font = theme.fonts["code"]
        lines = self.text.split("\n")
        
        sel = self.get_selection_range()
        
        for i, line in enumerate(lines):
            ly = self.rect.y + 8 + i * self.line_h - self.scroll_y
            if ly + self.line_h < self.rect.y or ly > self.rect.bottom:
                continue
                
            if sel:
                sel_min, sel_max = sel
                line_start_idx = self.get_idx(i, 0)
                line_end_idx = line_start_idx + len(line)
                
                if not (line_end_idx < sel_min or line_start_idx > sel_max):
                    start_char = max(0, sel_min - line_start_idx)
                    end_char = min(len(line), sel_max - line_start_idx)
                    
                    w_before, _ = font.size(line[:start_char])
                    w_sel, _ = font.size(line[start_char:end_char])
                    
                    if w_sel > 0:
                        highlight_surf = pygame.Surface((w_sel, self.line_h), pygame.SRCALPHA)
                        highlight_surf.fill((31, 111, 235, 100))
                        surface.blit(highlight_surf, (self.rect.x + 8 + w_before, ly))
            
            if self.syntax_highlight:
                draw_highlighted_line(surface, font, line, self.rect.x + 8, ly)
            else:
                if line:
                    txt_surf = font.render(line, True, theme.colors["input.foreground"])
                    surface.blit(txt_surf, (self.rect.x + 8, ly))
                    
        if not self.text and self.placeholder and not self.focused:
            ph_surf = font.render(self.placeholder, True, theme.colors["syntax.comment"])
            surface.blit(ph_surf, (self.rect.x + 8, self.rect.y + 8))
            
        if self.focused and self.cursor_visible and not self.read_only:
            line_idx, col = self.get_line_col(self.cursor_pos)
            ly = self.rect.y + 8 + line_idx * self.line_h - self.scroll_y
            if self.rect.y <= ly <= self.rect.bottom - self.line_h:
                w_col, _ = font.size(lines[line_idx][:col])
                cx = self.rect.x + 8 + w_col
                pygame.draw.line(surface, theme.colors["input.foreground"], (cx, ly + 2), (cx, ly + self.line_h - 2), 1)
                
        surface.set_clip(prev_clip)

class Checkbox(Widget):
    def __init__(self, rect, label, initial_val=False, callback=None):
        super().__init__(rect)
        self.label = label
        self.checked = initial_val
        self.callback = callback

    def handle_event(self, event, offset_mouse_pos=None):
        pos = offset_mouse_pos if offset_mouse_pos else pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.checked = not self.checked
                if self.callback:
                    self.callback(self.checked)
                return True
        return False

    def draw(self, surface):
        box_size = 18
        box_rect = pygame.Rect(self.rect.x, self.rect.y + (self.rect.height - box_size)//2, box_size, box_size)
        
        bg_color = theme.colors["input.background"]
        border_color = theme.colors["input.focusBorder"] if self.hovered else theme.colors["input.border"]
        
        pygame.draw.rect(surface, bg_color, box_rect, border_radius=4)
        pygame.draw.rect(surface, border_color, box_rect, width=1, border_radius=4)

        if self.checked:
            inner_rect = box_rect.inflate(-8, -8)
            pygame.draw.rect(surface, theme.colors["button.accentBackground"], inner_rect, border_radius=2)

        font = theme.fonts["body"]
        lbl_surf = font.render(tr(self.label), True, theme.colors["editor.foreground"])
        surface.blit(lbl_surf, (box_rect.right + 8, self.rect.y + (self.rect.height - lbl_surf.get_height())//2))

class ScrollArea:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.scroll_y = 0
        self.virtual_height = 0
        self.is_dragging = False
        self.drag_start_y = 0
        self.drag_start_scroll = 0
        self.scrollbar_width = 8
        self.scrollbar_padding = 4

    def handle_event(self, event):
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse_pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4 and hovered:
                self.scroll_y = max(0, self.scroll_y - 30)
                return True
            elif event.button == 5 and hovered:
                max_scroll = max(0, self.virtual_height - self.rect.height)
                self.scroll_y = min(max_scroll, self.scroll_y + 30)
                return True
            elif event.button == 1:
                if self.virtual_height > self.rect.height:
                    sb_rect = self.get_scrollbar_handle_rect()
                    if sb_rect.collidepoint(mouse_pos):
                        self.is_dragging = True
                        self.drag_start_y = mouse_pos[1]
                        self.drag_start_scroll = self.scroll_y
                        return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                delta_y = mouse_pos[1] - self.drag_start_y
                max_scroll = max(0, self.virtual_height - self.rect.height)
                
                track_h = self.rect.height
                handle_h = max(20, int(track_h * (self.rect.height / self.virtual_height)))
                scrollable_track_h = track_h - handle_h
                
                if scrollable_track_h > 0:
                    scroll_delta = (delta_y / scrollable_track_h) * max_scroll
                    self.scroll_y = max(0, min(max_scroll, self.drag_start_scroll + scroll_delta))
                return True
        return False

    def get_scrollbar_handle_rect(self):
        track_h = self.rect.height
        handle_h = max(20, int(track_h * (self.rect.height / self.virtual_height)))
        max_scroll = self.virtual_height - self.rect.height
        
        if max_scroll <= 0:
            return pygame.Rect(0,0,0,0)
            
        scroll_ratio = self.scroll_y / max_scroll
        scrollable_track_h = track_h - handle_h
        handle_y = self.rect.y + int(scroll_ratio * scrollable_track_h)
        
        return pygame.Rect(self.rect.right - self.scrollbar_width - self.scrollbar_padding, 
                           handle_y, 
                           self.scrollbar_width, 
                           handle_h)

    def draw(self, surface, draw_content_func):
        prev_clip = surface.get_clip()
        surface.set_clip(self.rect)
        draw_content_func(surface, self.scroll_y)
        surface.set_clip(prev_clip)

        if self.virtual_height > self.rect.height:
            track_rect = pygame.Rect(self.rect.right - self.scrollbar_width - self.scrollbar_padding, 
                                     self.rect.y, 
                                     self.scrollbar_width, 
                                     self.rect.height)
            pygame.draw.rect(surface, theme.colors["sideBar.background"], track_rect, border_radius=4)
            
            handle_rect = self.get_scrollbar_handle_rect()
            handle_color = theme.colors["button.hoverBackground"] if self.is_dragging else theme.colors["sideBar.border"]
            pygame.draw.rect(surface, handle_color, handle_rect, border_radius=4)

class PortRow:
    def __init__(self, index, port_data, on_delete):
        self.index = index
        self.port_data = port_data
        self.on_delete = on_delete
        
        self.dir_toggle = ToggleButton((0,0,50,26), ["IN", "OUT"], 
                                      initial_index=0 if port_data["dir"] == "IN" else 1,
                                      callback=self.set_dir)
        self.name_input = InputBox((0,0,180,26), text=port_data["name"], placeholder="port_name")
        self.width_input = InputBox((0,0,80,26), text=port_data["width"], placeholder="1", is_number_range=True)
        self.del_btn = Button((0,0,20,26), "", callback=self.delete_self, 
                              no_bg=True, fg_color_key="ports.reset_light", 
                              hover_fg_color_key="ports.reset", icon="X")

    def set_dir(self, val):
        self.port_data["dir"] = val

    def delete_self(self):
        self.on_delete(self.index)

    def update(self):
        self.port_data["name"] = self.name_input.text
        self.port_data["width"] = self.width_input.text
        self.dir_toggle.update()
        self.name_input.update()
        self.width_input.update()
        self.del_btn.update()

    def set_positions(self, x, y, width=366, height=26):
        # Scale positions based on available width and height
        active_w = width - 16
        del_w = height
        width_w = int(70 * (height / 26))
        dir_w = int(50 * (height / 26))
        
        del_x = x + active_w - del_w
        width_x = del_x - 10 - width_w
        
        self.dir_toggle.rect.topleft = (x, y)
        self.dir_toggle.rect.width = dir_w
        self.dir_toggle.rect.height = height
        
        name_w = max(50, width_x - (x + dir_w + 10) - 10)
        self.name_input.rect.topleft = (x + dir_w + 10, y)
        self.name_input.rect.width = name_w
        self.name_input.rect.height = height
        
        self.width_input.rect.topleft = (width_x, y)
        self.width_input.rect.width = width_w
        self.width_input.rect.height = height
        
        self.del_btn.rect.topleft = (del_x, y)
        self.del_btn.rect.width = del_w
        self.del_btn.rect.height = height

    def handle_event(self, event, offset_mouse_pos=None):
        if self.dir_toggle.handle_event(event, offset_mouse_pos): return True
        if self.name_input.handle_event(event, offset_mouse_pos): return True
        if self.width_input.handle_event(event, offset_mouse_pos): return True
        if self.del_btn.handle_event(event, offset_mouse_pos): return True
        return False

    def draw(self, surface):
        self.dir_toggle.draw(surface)
        self.name_input.draw(surface)
        self.width_input.draw(surface)
        self.del_btn.draw(surface)

class BlockDiagram:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.scale = 1.0

    def draw(self, surface, module_name, ports):
        pygame.draw.rect(surface, theme.colors["sideBar.background"], self.rect, border_radius=12)
        pygame.draw.rect(surface, theme.colors["sideBar.border"], self.rect, width=2, border_radius=12)

        if not module_name:
            module_name = "unnamed_module"

        inputs = [p for p in ports if p["dir"] == "IN"]
        outputs = [p for p in ports if p["dir"] == "OUT"]

        # Calculate responsive sizes based on scaling
        block_w = int(260 * self.scale)
        v_spacing = int(36 * self.scale)
        block_h = max(int(180 * self.scale), max(len(inputs), len(outputs)) * v_spacing + int(60 * self.scale))
        
        block_x = self.rect.x + (self.rect.width - block_w) // 2
        block_y = self.rect.y + (self.rect.height - block_h) // 2

        # Create scaled fonts for diagram text
        font_sz = max(8, int(14 * self.scale))
        title_sz = max(10, int(16 * self.scale))
        small_sz = max(6, int(10 * self.scale))
        
        font = pygame.font.SysFont("segoeui", font_sz)
        font_bold = pygame.font.SysFont("segoeui", title_sz, bold=True)
        font_small = pygame.font.SysFont("segoeui", small_sz)

        # Inputs (Left side)
        for i, port in enumerate(inputs):
            name = port["name"] or "unnamed"
            width = port["width"] or "1"
            py = block_y + int(40 * self.scale) + i * v_spacing
            
            line_x1 = self.rect.x + 30
            line_x2 = block_x
            
            color = theme.colors["ports.input"]
            icon_type = None
            if name.lower() in ["clk", "clock", "i_clk"]:
                color = theme.colors["ports.clock"]
                icon_type = "clk"
            elif name.lower() in ["rst", "reset", "rst_n", "i_rst", "rst_b"]:
                color = theme.colors["ports.reset"]
                icon_type = "rst"

            pygame.draw.line(surface, color, (line_x1, py), (line_x2, py), 2)
            pygame.draw.polygon(surface, color, [
                (block_x - 6, py - 4),
                (block_x, py),
                (block_x - 6, py + 4)
            ])

            if icon_type == "clk":
                pygame.draw.lines(surface, color, False, [
                    (line_x1 + 5, py + 4),
                    (line_x1 + 10, py + 4),
                    (line_x1 + 10, py - 4),
                    (line_x1 + 15, py - 4),
                    (line_x1 + 15, py + 4),
                    (line_x1 + 20, py + 4)
                ], 1)
            elif icon_type == "rst":
                pygame.draw.circle(surface, color, (line_x1 + 12, py), 4, 1)
                pygame.draw.line(surface, color, (line_x1 + 12, py - 4), (line_x1 + 12, py), 1)

            lbl = f"{name} [{width}]" if width != "1" else name
            lbl_surf = font.render(lbl, True, theme.colors["editor.foreground"])
            surface.blit(lbl_surf, (line_x1 + 25, py - lbl_surf.get_height() - 2))

        # Outputs (Right side)
        for i, port in enumerate(outputs):
            name = port["name"] or "unnamed"
            width = port["width"] or "1"
            py = block_y + int(40 * self.scale) + i * v_spacing
            
            line_x1 = block_x + block_w
            line_x2 = self.rect.right - 30
            
            color = theme.colors["ports.output"]
            pygame.draw.line(surface, color, (line_x1, py), (line_x2, py), 2)
            pygame.draw.polygon(surface, color, [
                (line_x2 - 6, py - 4),
                (line_x2, py),
                (line_x2 - 6, py + 4)
            ])

            lbl = f"{name} [{width}]" if width != "1" else name
            lbl_surf = font.render(lbl, True, theme.colors["editor.foreground"])
            surface.blit(lbl_surf, (line_x2 - lbl_surf.get_width() - 8, py - lbl_surf.get_height() - 2))

        # Central block
        block_rect = pygame.Rect(block_x, block_y, block_w, block_h)
        bg_surface = pygame.Surface((block_w, block_h), pygame.SRCALPHA)
        # Dynamic block color based on editor.background
        base_color = theme.colors["editor.background"]
        bg_surface.fill((base_color[0], base_color[1], base_color[2], 220))
        surface.blit(bg_surface, block_rect)
        
        pygame.draw.rect(surface, theme.colors["sideBar.border"], block_rect, width=2, border_radius=8)

        mod_lbl = font_bold.render(module_name, True, theme.colors["syntax.name"])
        surface.blit(mod_lbl, (block_x + (block_w - mod_lbl.get_width())//2, block_y + int(12 * self.scale)))
        
        sub_lbl = font_small.render("SYSTEMVERILOG MODULE", True, theme.colors["syntax.comment"])
        surface.blit(sub_lbl, (block_x + (block_w - sub_lbl.get_width())//2, block_y + int(12 * self.scale) + mod_lbl.get_height()))

class ToastManager:
    def __init__(self):
        self.message = ""
        self.color = (0, 255, 0)
        self.show_until = 0

    def show(self, message, duration=2.5, is_error=False):
        self.message = message
        self.color = theme.colors["ports.reset"] if is_error else theme.colors["ports.output"]
        self.show_until = time.time() + duration

    def draw(self, surface, screen_width, screen_height):
        if time.time() < self.show_until:
            font = theme.fonts["body_bold"]
            txt_surf = font.render(self.message, True, (255, 255, 255))
            
            padding_x = 20
            padding_y = 10
            tw = txt_surf.get_width() + padding_x * 2
            th = txt_surf.get_height() + padding_y * 2
            
            rect = pygame.Rect((screen_width - tw)//2, 20, tw, th)
            
            toast_surf = pygame.Surface((tw, th), pygame.SRCALPHA)
            toast_surf.fill((14, 17, 23, 230))
            surface.blit(toast_surf, rect)
            
            pygame.draw.rect(surface, self.color, rect, width=2, border_radius=8)
            surface.blit(txt_surf, (rect.x + padding_x, rect.y + padding_y))
