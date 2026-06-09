import time
import pygame
from src.ui.theme import theme

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
