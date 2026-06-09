import time
import pygame
from src.ui.widgets.base import Widget, set_clipboard_text, get_clipboard_text, find_word_boundary
from src.ui.theme import theme

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
            return c.isalnum() or c in "[:]-+_ "
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
