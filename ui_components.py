import pygame
import json
import os
import time
import tkinter as tk

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
            "ports.input": (59, 130, 246),
            "ports.output": (16, 185, 129),
            "ports.inout": (245, 158, 11)
        }
        
        self.fonts = {}
        self.load_theme(theme_path)

    def load_theme(self, theme_path):
        # Start with fallback
        for k, v in self.fallback_colors.items():
            self.colors[k] = v

        if theme_path and os.path.exists(theme_path):
            try:
                with open(theme_path, 'r') as f:
                    data = json.load(f)
                for key, val in data.items():
                    if isinstance(val, str) and val.startswith("#"):
                        # Parse hex to rgb
                        h = val.lstrip("#")
                        if len(h) == 6:
                            self.colors[key] = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
                        elif len(h) == 8:
                            self.colors[key] = tuple(int(h[i:i+2], 16) for i in (0, 2, 4, 6))
            except Exception as e:
                print(f"Warning: Failed to load theme file: {e}. Using defaults.")

    def init_fonts(self):
        pygame.font.init()
        # Find available system fonts or fallback to default
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

        self.fonts["header"] = pygame.font.SysFont(sans_name, 20, bold=True)
        self.fonts["body"] = pygame.font.SysFont(sans_name, 14)
        self.fonts["body_bold"] = pygame.font.SysFont(sans_name, 14, bold=True)
        self.fonts["small"] = pygame.font.SysFont(sans_name, 11)
        self.fonts["code"] = pygame.font.SysFont(mono_name, 14)
        self.fonts["code_large"] = pygame.font.SysFont(mono_name, 16)

# Globals for access
theme = Theme("theme.json")

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
    def __init__(self, rect, text, callback=None, is_accent=False, bg_color_key=None, icon=None):
        super().__init__(rect)
        self.text = text
        self.callback = callback
        self.is_accent = is_accent
        self.bg_color_key = bg_color_key
        self.icon = icon # e.g. "+", "X"
        self.alpha_hover = 0 # for smooth transition
        
    def handle_event(self, event, offset_mouse_pos=None):
        pos = offset_mouse_pos if offset_mouse_pos else pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and self.callback:
                pygame.key.start_text_input() # ensure text input is active if we clicked a text button, or just run callback
                self.callback()
                return True
        return False

    def update(self):
        target = 255 if self.hovered else 0
        if self.alpha_hover != target:
            # Smooth transition
            diff = target - self.alpha_hover
            step = 30 if diff > 0 else -30
            if abs(diff) <= abs(step):
                self.alpha_hover = target
            else:
                self.alpha_hover += step

    def draw(self, surface):
        # Determine colors
        if self.bg_color_key:
            bg_base = theme.colors[self.bg_color_key]
        elif self.is_accent:
            bg_base = theme.colors["button.accentBackground"]
        else:
            bg_base = theme.colors["button.background"]

        fg_color = theme.colors["button.accentForeground"] if (self.is_accent or self.bg_color_key) else theme.colors["button.foreground"]
        
        # Calculate hover background color
        if self.is_accent:
            # Lighter accent for hover
            bg_hover = tuple(min(255, int(c * 1.2)) for c in bg_base)
        elif self.bg_color_key:
            bg_hover = tuple(min(255, int(c * 1.2)) for c in bg_base)
        else:
            bg_hover = theme.colors["button.hoverBackground"]

        # Mix colors for smooth animation
        factor = self.alpha_hover / 255.0
        bg_curr = tuple(int(bg_base[i] * (1 - factor) + bg_hover[i] * factor) for i in range(3))

        # Draw rounded rect
        pygame.draw.rect(surface, bg_curr, self.rect, border_radius=6)
        
        # Draw border
        border_color = theme.colors["sideBar.border"]
        pygame.draw.rect(surface, border_color, self.rect, width=1, border_radius=6)

        # Draw content
        font = theme.fonts["body_bold"] if self.is_accent else theme.fonts["body"]
        
        if self.icon:
            # Draw icon (e.g. "+" or "X")
            txt_surf = font.render(self.icon, True, fg_color)
            txt_rect = txt_surf.get_rect(center=self.rect.center)
            surface.blit(txt_surf, txt_rect)
        else:
            txt_surf = font.render(self.text, True, fg_color)
            txt_rect = txt_surf.get_rect(center=self.rect.center)
            surface.blit(txt_surf, txt_rect)

class ToggleButton(Widget):
    def __init__(self, rect, options, initial_index=0, callback=None):
        super().__init__(rect)
        self.options = options # list of strings (e.g., ["IN", "OUT"])
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
        
        # Color coding for IN/OUT
        if val_str == "IN":
            fg_color = theme.colors["ports.input"]
        elif val_str == "OUT":
            fg_color = theme.colors["ports.output"]
        else:
            fg_color = theme.colors["button.foreground"]

        font = theme.fonts["body_bold"]
        txt_surf = font.render(val_str, True, fg_color)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

class InputBox(Widget):
    def __init__(self, rect, text="", placeholder="", is_number_range=False, max_len=60):
        super().__init__(rect)
        self.text = text
        self.placeholder = placeholder
        self.is_number_range = is_number_range # allows digits, :, [ ] for bus dimensions
        self.max_len = max_len
        self.cursor_pos = len(text)
        self.cursor_visible = True
        self.last_blink = time.time()
        
    def handle_event(self, event, offset_mouse_pos=None):
        pos = offset_mouse_pos if offset_mouse_pos else pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            old_focus = self.focused
            self.focused = self.hovered
            if self.focused:
                pygame.key.start_text_input()
                # Estimate cursor pos based on click X relative to text start
                self.cursor_pos = self.estimate_cursor_pos(pos[0] - self.rect.x - 8)
                self.last_blink = time.time()
                self.cursor_visible = True
            elif old_focus:
                pygame.key.stop_text_input()
            return self.focused

        if self.focused and event.type == pygame.KEYDOWN:
            self.last_blink = time.time()
            self.cursor_visible = True

            # Handle backspace
            if event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
                return True
            
            # Handle delete
            elif event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
                return True

            # Handle navigation
            elif event.key == pygame.K_LEFT:
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
                return True
            elif event.key == pygame.K_RIGHT:
                if self.cursor_pos < len(self.text):
                    self.cursor_pos += 1
                return True
            elif event.key == pygame.K_HOME:
                self.cursor_pos = 0
                return True
            elif event.key == pygame.K_END:
                self.cursor_pos = len(self.text)
                return True

            # Handle copy-paste shortcuts
            mods = pygame.key.get_mods()
            if (mods & pygame.KMOD_CTRL):
                if event.key == pygame.K_v:
                    clip_text = get_clipboard_text()
                    # Filter input
                    clip_text = "".join(c for c in clip_text if self.char_allowed(c))
                    # Insert
                    if len(self.text) + len(clip_text) <= self.max_len:
                        self.text = self.text[:self.cursor_pos] + clip_text + self.text[self.cursor_pos:]
                        self.cursor_pos += len(clip_text)
                    return True
                elif event.key == pygame.K_c:
                    set_clipboard_text(self.text)
                    return True

        elif self.focused and event.type == pygame.TEXTINPUT:
            # event.text is the typed character(s)
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
            # Allow digits, brackets, colons, - and variables
            return c.isalnum() or c in "[:]-+_"
        else:
            # Allow variable name chars (alphanumeric and underscore)
            return c.isalnum() or c in "_"

    def estimate_cursor_pos(self, click_x):
        # Simple estimation by stepping through characters
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
        
        # Draw input box background & border
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=6)
        pygame.draw.rect(surface, border_color, self.rect, width=1, border_radius=6)

        # Draw text
        font = theme.fonts["code"]
        text_color = theme.colors["input.foreground"]
        
        if self.text == "" and not self.focused:
            # Draw placeholder
            ph_surf = font.render(self.placeholder, True, theme.colors["syntax.comment"])
            surface.blit(ph_surf, (self.rect.x + 8, self.rect.y + (self.rect.height - ph_surf.get_height())//2))
        else:
            # Render visible text
            txt_surf = font.render(self.text, True, text_color)
            surface.blit(txt_surf, (self.rect.x + 8, self.rect.y + (self.rect.height - txt_surf.get_height())//2))
            
            # Render cursor
            if self.focused and self.cursor_visible:
                cursor_offset_x, _ = font.size(self.text[:self.cursor_pos])
                cx = self.rect.x + 8 + cursor_offset_x
                cy1 = self.rect.y + 6
                cy2 = self.rect.y + self.rect.height - 6
                pygame.draw.line(surface, text_color, (cx, cy1), (cx, cy2), 1)

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
        # Draw check box
        box_size = 18
        box_rect = pygame.Rect(self.rect.x, self.rect.y + (self.rect.height - box_size)//2, box_size, box_size)
        
        bg_color = theme.colors["input.background"]
        border_color = theme.colors["input.focusBorder"] if self.hovered else theme.colors["input.border"]
        
        pygame.draw.rect(surface, bg_color, box_rect, border_radius=4)
        pygame.draw.rect(surface, border_color, box_rect, width=1, border_radius=4)

        if self.checked:
            # Draw a check mark (accent colored square or simple line art)
            inner_rect = box_rect.inflate(-8, -8)
            pygame.draw.rect(surface, theme.colors["button.accentBackground"], inner_rect, border_radius=2)

        # Draw label
        font = theme.fonts["body"]
        lbl_surf = font.render(self.label, True, theme.colors["editor.foreground"])
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
            if event.button == 4 and hovered: # Wheel Up
                self.scroll_y = max(0, self.scroll_y - 30)
                return True
            elif event.button == 5 and hovered: # Wheel Down
                max_scroll = max(0, self.virtual_height - self.rect.height)
                self.scroll_y = min(max_scroll, self.scroll_y + 30)
                return True
            elif event.button == 1:
                # Check scrollbar hit
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
                
                # Calculate scroll ratio
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
        # Set clipping rect to scroll area viewport
        prev_clip = surface.get_clip()
        surface.set_clip(self.rect)

        # Draw content inside viewport (offset by scroll_y)
        draw_content_func(surface, self.scroll_y)

        # Restore original clip
        surface.set_clip(prev_clip)

        # Draw scrollbar if needed
        if self.virtual_height > self.rect.height:
            # Draw track
            track_rect = pygame.Rect(self.rect.right - self.scrollbar_width - self.scrollbar_padding, 
                                     self.rect.y, 
                                     self.scrollbar_width, 
                                     self.rect.height)
            pygame.draw.rect(surface, theme.colors["sideBar.background"], track_rect, border_radius=4)
            
            # Draw handle
            handle_rect = self.get_scrollbar_handle_rect()
            handle_color = theme.colors["button.hoverBackground"] if self.is_dragging else theme.colors["sideBar.border"]
            pygame.draw.rect(surface, handle_color, handle_rect, border_radius=4)

class PortRow:
    def __init__(self, index, port_data, on_delete):
        # port_data is a dict: {"name": str, "dir": "IN"|"OUT", "width": str}
        self.index = index
        self.port_data = port_data
        self.on_delete = on_delete
        
        # Sub-widgets (positions will be set dynamically during draw/event)
        self.dir_toggle = ToggleButton((0,0,50,26), ["IN", "OUT"], 
                                      initial_index=0 if port_data["dir"] == "IN" else 1,
                                      callback=self.set_dir)
        self.name_input = InputBox((0,0,180,26), text=port_data["name"], placeholder="port_name")
        self.width_input = InputBox((0,0,80,26), text=port_data["width"], placeholder="1", is_number_range=True)
        self.del_btn = Button((0,0,26,26), "", callback=self.delete_self, bg_color_key="ports.reset", icon="X")

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

    def set_positions(self, x, y):
        # Lay out sub-widgets relative to the row's top-left
        self.dir_toggle.rect.topleft = (x, y)
        self.name_input.rect.topleft = (x + 60, y)
        self.width_input.rect.topleft = (x + 250, y)
        self.del_btn.rect.topleft = (x + 340, y)

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

    def draw(self, surface, module_name, ports):
        # Draw background panel
        pygame.draw.rect(surface, theme.colors["sideBar.background"], self.rect, border_radius=12)
        pygame.draw.rect(surface, theme.colors["sideBar.border"], self.rect, width=2, border_radius=12)

        if not module_name:
            module_name = "unnamed_module"

        # Separate inputs and outputs
        inputs = [p for p in ports if p["dir"] == "IN"]
        outputs = [p for p in ports if p["dir"] == "OUT"]

        # Calculate coordinates for the central block
        block_w = 260
        block_h = max(180, max(len(inputs), len(outputs)) * 36 + 60)
        
        # Center the block in our viewport
        block_x = self.rect.x + (self.rect.width - block_w) // 2
        block_y = self.rect.y + (self.rect.height - block_h) // 2

        # Draw connection lines & labels
        font = theme.fonts["body"]
        font_bold = theme.fonts["body_bold"]
        font_small = theme.fonts["small"]

        # Draw Inputs (Left side)
        for i, port in enumerate(inputs):
            name = port["name"] or "unnamed"
            width = port["width"] or "1"
            
            # Determine spacing
            py = block_y + 40 + i * 36
            
            # Draw line to block
            line_x1 = self.rect.x + 30
            line_x2 = block_x
            
            # Color code
            color = theme.colors["ports.input"]
            icon_type = None
            if name.lower() in ["clk", "clock", "i_clk"]:
                color = theme.colors["ports.clock"]
                icon_type = "clk"
            elif name.lower() in ["rst", "reset", "rst_n", "i_rst", "rst_b"]:
                color = theme.colors["ports.reset"]
                icon_type = "rst"

            pygame.draw.line(surface, color, (line_x1, py), (line_x2, py), 2)
            
            # Draw input triangle arrow at the block entrance
            pygame.draw.polygon(surface, color, [
                (block_x - 6, py - 4),
                (block_x, py),
                (block_x - 6, py + 4)
            ])

            # Draw port symbol/icon
            if icon_type == "clk":
                # Clock wave icon
                pygame.draw.lines(surface, color, False, [
                    (line_x1 + 5, py + 4),
                    (line_x1 + 10, py + 4),
                    (line_x1 + 10, py - 4),
                    (line_x1 + 15, py - 4),
                    (line_x1 + 15, py + 4),
                    (line_x1 + 20, py + 4)
                ], 1)
            elif icon_type == "rst":
                # Power/reset symbol (small circle with line)
                pygame.draw.circle(surface, color, (line_x1 + 12, py), 4, 1)
                pygame.draw.line(surface, color, (line_x1 + 12, py - 4), (line_x1 + 12, py), 1)

            # Draw text label
            lbl = f"{name} [{width}]" if width != "1" else name
            lbl_surf = font.render(lbl, True, theme.colors["editor.foreground"])
            surface.blit(lbl_surf, (line_x1 + 25, py - lbl_surf.get_height() - 2))

        # Draw Outputs (Right side)
        for i, port in enumerate(outputs):
            name = port["name"] or "unnamed"
            width = port["width"] or "1"
            
            py = block_y + 40 + i * 36
            
            # Draw line out of block
            line_x1 = block_x + block_w
            line_x2 = self.rect.right - 30
            
            color = theme.colors["ports.output"]
            pygame.draw.line(surface, color, (line_x1, py), (line_x2, py), 2)
            
            # Draw output arrow pointing outwards
            pygame.draw.polygon(surface, color, [
                (line_x2 - 6, py - 4),
                (line_x2, py),
                (line_x2 - 6, py + 4)
            ])

            # Draw text label
            lbl = f"{name} [{width}]" if width != "1" else name
            lbl_surf = font.render(lbl, True, theme.colors["editor.foreground"])
            surface.blit(lbl_surf, (line_x2 - lbl_surf.get_width() - 8, py - lbl_surf.get_height() - 2))

        # Draw central block (SystemVerilog Module)
        block_rect = pygame.Rect(block_x, block_y, block_w, block_h)
        # semi-transparent filling
        bg_surface = pygame.Surface((block_w, block_h), pygame.SRCALPHA)
        # dark modern block color
        bg_surface.fill((20, 24, 33, 220))
        surface.blit(bg_surface, block_rect)
        
        # Border
        pygame.draw.rect(surface, theme.colors["sideBar.border"], block_rect, width=2, border_radius=8)

        # Render module header text
        mod_lbl = font_bold.render(module_name, True, theme.colors["syntax.name"])
        surface.blit(mod_lbl, (block_x + (block_w - mod_lbl.get_width())//2, block_y + 12))
        
        # Render a small sublabel: "SystemVerilog Module"
        sub_lbl = font_small.render("SYSTEMVERILOG MODULE", True, theme.colors["syntax.comment"])
        surface.blit(sub_lbl, (block_x + (block_w - sub_lbl.get_width())//2, block_y + 12 + mod_lbl.get_height()))

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
            
            # Position at top center
            rect = pygame.Rect((screen_width - tw)//2, 20, tw, th)
            
            # Draw semi-transparent card
            toast_surf = pygame.Surface((tw, th), pygame.SRCALPHA)
            toast_surf.fill((14, 17, 23, 230))
            surface.blit(toast_surf, rect)
            
            # Border
            pygame.draw.rect(surface, self.color, rect, width=2, border_radius=8)
            
            # Text
            surface.blit(txt_surf, (rect.x + padding_x, rect.y + padding_y))
