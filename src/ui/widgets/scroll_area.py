import pygame
from src.ui.theme import theme

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
                    track_rect = pygame.Rect(self.rect.right - self.scrollbar_width - self.scrollbar_padding,
                                             self.rect.y,
                                             self.scrollbar_width,
                                             self.rect.height)
                    if track_rect.collidepoint(mouse_pos):
                        sb_rect = self.get_scrollbar_handle_rect()
                        if sb_rect.collidepoint(mouse_pos):
                            self.is_dragging = True
                            self.drag_start_y = mouse_pos[1]
                            self.drag_start_scroll = self.scroll_y
                        else:
                            track_h = self.rect.height
                            handle_h = sb_rect.height
                            scrollable_track_h = track_h - handle_h
                            if scrollable_track_h > 0:
                                click_y_rel = mouse_pos[1] - self.rect.y - (handle_h / 2)
                                click_ratio = click_y_rel / scrollable_track_h
                                max_scroll = max(0, self.virtual_height - track_h)
                                self.scroll_y = max(0, min(max_scroll, int(click_ratio * max_scroll)))
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
