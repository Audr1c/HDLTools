import pygame
from src.ui.widgets.base import Widget
from src.ui.theme import theme
from src.core.localization import tr

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
