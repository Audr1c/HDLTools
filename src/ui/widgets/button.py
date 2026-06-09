import os
import pygame
from src.ui.widgets.base import Widget
from src.ui.theme import theme, image_cache
from src.core.localization import tr
from src.core.config import resource_path

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
                path = resource_path(os.path.join("assets", "images", "diskette.png"))
                if path not in image_cache:
                    if os.path.exists(path):
                        try:
                            image_cache[path] = pygame.image.load(path).convert_alpha()
                        except Exception:
                            image_cache[path] = None
                    else:
                        try:
                            os.makedirs(os.path.dirname(path), exist_ok=True)
                            temp_s = pygame.Surface((32, 32), pygame.SRCALPHA)
                            pygame.draw.rect(temp_s, (201, 209, 217), (4, 4, 24, 24), border_radius=2)
                            pygame.draw.rect(temp_s, (20, 24, 33), (8, 6, 16, 6))
                            pygame.draw.rect(temp_s, (20, 24, 33), (10, 18, 12, 10))
                            pygame.image.save(temp_s, path)
                            image_cache[path] = temp_s
                        except Exception:
                            image_cache[path] = None
                
                img = image_cache[path]
                if img:
                    sz_w = self.rect.width - 8
                    sz_h = self.rect.height - 8
                    scaled = pygame.transform.smoothscale(img, (sz_w, sz_h))
                    r_img = scaled.get_rect(center=self.rect.center)
                    surface.blit(scaled, r_img)
                else:
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
