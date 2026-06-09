import time
import pygame
import re
from src.ui.widgets.base import Widget, set_clipboard_text, get_clipboard_text, find_word_boundary
from src.ui.theme import theme
from src.core.localization import tr

def draw_highlighted_line(surface, font, line_text, x, y):
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

class TextArea(Widget):
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

        self.is_dragging_scrollbar = False
        self.drag_start_y = 0
        self.drag_start_scroll = 0
        self.scrollbar_width = 8
        self.scrollbar_padding = 4

    def get_scrollbar_handle_rect(self):
        track_h = self.rect.height - 16
        if self.virtual_height <= track_h or self.virtual_height == 0:
            return pygame.Rect(0, 0, 0, 0)
        handle_h = max(20, int(track_h * (track_h / self.virtual_height)))
        max_scroll = self.virtual_height - track_h
        if max_scroll <= 0:
            return pygame.Rect(0, 0, 0, 0)
        scroll_ratio = self.scroll_y / max_scroll
        scrollable_track_h = track_h - handle_h
        handle_y = self.rect.y + 8 + int(scroll_ratio * scrollable_track_h)
        return pygame.Rect(self.rect.right - self.scrollbar_width - self.scrollbar_padding,
                           handle_y,
                           self.scrollbar_width,
                           handle_h)

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
                    # Check if click on scrollbar
                    if self.virtual_height > self.rect.height - 16:
                        track_rect = pygame.Rect(self.rect.right - self.scrollbar_width - self.scrollbar_padding,
                                                 self.rect.y + 8,
                                                 self.scrollbar_width,
                                                 self.rect.height - 16)
                        if track_rect.collidepoint(pos):
                            sb_rect = self.get_scrollbar_handle_rect()
                            if sb_rect.collidepoint(pos):
                                self.is_dragging_scrollbar = True
                                self.drag_start_y = pos[1]
                                self.drag_start_scroll = self.scroll_y
                            else:
                                track_h = self.rect.height - 16
                                handle_h = sb_rect.height
                                scrollable_track_h = track_h - handle_h
                                if scrollable_track_h > 0:
                                    click_y_rel = pos[1] - (self.rect.y + 8) - (handle_h / 2)
                                    click_ratio = click_y_rel / scrollable_track_h
                                    max_scroll = max(0, self.virtual_height - track_h)
                                    self.scroll_y = max(0, min(max_scroll, int(click_ratio * max_scroll)))
                                    self.is_dragging_scrollbar = True
                                    self.drag_start_y = pos[1]
                                    self.drag_start_scroll = self.scroll_y
                            return True
                            
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
            self.is_dragging_scrollbar = False
            self.is_dragging_selection = False
            if self.select_start == self.select_end:
                self.select_start = -1
                self.select_end = -1

        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging_scrollbar:
                delta_y = pos[1] - self.drag_start_y
                track_h = self.rect.height - 16
                max_scroll = max(0, self.virtual_height - track_h)
                handle_h = max(20, int(track_h * (track_h / self.virtual_height)))
                scrollable_track_h = track_h - handle_h
                if scrollable_track_h > 0:
                    scroll_delta = (delta_y / scrollable_track_h) * max_scroll
                    self.scroll_y = max(0, min(max_scroll, self.drag_start_scroll + scroll_delta))
                return True
            elif self.focused and self.is_dragging_selection:
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
                
            elif event.key == pygame.K_RETURN:
                self.delete_selection()
                self.text = self.text[:self.cursor_pos] + "\n" + self.text[self.cursor_pos:]
                self.cursor_pos += 1
                self.auto_scroll_to_cursor()
                return True

            # Navigation
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
                lines = self.text.split("\n")
                line_idx, col = self.get_line_col(self.cursor_pos)
                if line_idx > 0:
                    new_pos = self.get_idx(line_idx - 1, col)
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
                lines = self.text.split("\n")
                line_idx, col = self.get_line_col(self.cursor_pos)
                if line_idx < len(lines) - 1:
                    new_pos = self.get_idx(line_idx + 1, col)
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
                lines = self.text.split("\n")
                line_idx, _ = self.get_line_col(self.cursor_pos)
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
                lines = self.text.split("\n")
                line_idx, _ = self.get_line_col(self.cursor_pos)
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
        # Allow printable and whitespace characters in text areas
        return c.isprintable() or c in "\n\t\r"

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
        
        # Adjust clip if scrollbar is visible
        clip_w = self.rect.width - 8
        if self.virtual_height > self.rect.height - 16:
            clip_w -= 16
        surface.set_clip(pygame.Rect(self.rect.x + 4, self.rect.y + 4, clip_w, self.rect.height - 8))
        
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

        # Draw scrollbar if content exceeds height
        if self.virtual_height > self.rect.height - 16:
            track_rect = pygame.Rect(self.rect.right - self.scrollbar_width - self.scrollbar_padding,
                                     self.rect.y + 8,
                                     self.scrollbar_width,
                                     self.rect.height - 16)
            pygame.draw.rect(surface, theme.colors["sideBar.background"], track_rect, border_radius=4)
            
            handle_rect = self.get_scrollbar_handle_rect()
            handle_color = theme.colors["button.hoverBackground"] if self.is_dragging_scrollbar else theme.colors["sideBar.border"]
            pygame.draw.rect(surface, handle_color, handle_rect, border_radius=4)
