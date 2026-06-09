import os
import sys
import pygame
from src.core.config import setup_dpi_and_app_id, ensure_assets_exist, resource_path, chemin_icone, FPS
from src.core.preferences import load_preferences, save_preferences
from src.core.state import AppState
from src.ui.theme import theme
from src.ui.window import MainWindow
import src.core.localization as loc

class Application:
    def __init__(self):
        # 1. Initialize DPI awareness for clean text in Windows
        setup_dpi_and_app_id()
        
        # 2. Build default image assets dynamically if they are missing
        ensure_assets_exist()
        
        # 3. Load user configurations
        self.prefs = load_preferences()
        self.state = AppState(self.prefs)
        
        # 4. Apply localization
        loc.current_language = self.state.current_language
        
        # 5. Initialize Pygame & display
        pygame.init()
        self.width = self.prefs.get("window_width", 1280)
        self.height = self.prefs.get("window_height", 720)
        
        flags = pygame.RESIZABLE
        if self.prefs.get("window_maximized", False):
            flags |= pygame.WINDOWMAXIMIZED
            
        self.screen = pygame.display.set_mode((self.width, self.height), flags)
        pygame.display.set_caption("Tools HDL")
        
        # Set window icon
        if os.path.exists(chemin_icone):
            try:
                icon_surf = pygame.image.load(chemin_icone)
                pygame.display.set_icon(icon_surf)
            except Exception as e:
                print("Failed to set window icon:", e)
                
        # 6. Apply initial theme and load fonts
        theme.apply_preset(self.state.current_theme_name)
        theme.init_fonts(self.state.ui_font_scale)
        
        # 7. Create UI Main Window
        self.window = MainWindow(self.state)
        self.clock = pygame.time.Clock()
        
    def run(self):
        self.window.recalculate_all_layouts(self.width, self.height)
        
        # Dragging states
        is_dragging_separator = False
        
        while self.state.running:
            mouse_pos = pygame.mouse.get_pos()
            
            # 1. Update states from widgets input elements
            if not self.state.show_preferences_modal:
                # Sync module name changes
                if self.state.module_name != self.window.module_name_input.text:
                    self.state.module_name = self.window.module_name_input.text
                    self.window.update_code_cache()
                # Sync reset checkboxes
                if self.state.is_sync_reset != self.window.sync_reset_cb.checked:
                    self.state.is_sync_reset = self.window.sync_reset_cb.checked
                    self.window.update_code_cache()
                if self.state.is_active_low_reset != self.window.active_low_cb.checked:
                    self.state.is_active_low_reset = self.window.active_low_cb.checked
                    self.window.update_code_cache()
                # Sync testbench Mode toggles
                curr_tb_mode = "standalone" if self.window.tb_mode_toggle.index == 0 else "chained"
                if self.state.tb_mode != curr_tb_mode:
                    self.state.tb_mode = curr_tb_mode
                    # Reset subtab if master is selected but stand-alone is active
                    if self.state.tb_mode == "standalone" and self.state.code_subtab == "master":
                        self.state.code_subtab = "testbench"
                        self.window.update_tab_highlights()
                    self.window.update_code_cache()
            
            # 2. Update widget hover alphas
            self.window.btn_prefs.update()
            if self.state.show_preferences_modal:
                self.window.pref_lang_toggle.update()
                self.window.pref_theme_toggle.update()
                self.window.pref_hdl_toggle.update()
                self.window.btn_pref_ui_dec.update()
                self.window.btn_pref_ui_inc.update()
                self.window.btn_pref_ed_dec.update()
                self.window.btn_pref_ed_inc.update()
                self.window.btn_pref_close.update()
            else:
                self.window.module_name_input.update()
                self.window.active_low_cb.update()
                self.window.sync_reset_cb.update()
                self.window.btn_add_clk.update()
                self.window.btn_add_rst.update()
                self.window.tb_mode_toggle.update()
                self.window.btn_add_input.update()
                self.window.btn_add_output.update()
                self.window.btn_tab_diagram.update()
                self.window.btn_tab_code.update()
                self.window.btn_tab_paste.update()
                self.window.btn_save.update()
                
                if self.state.right_tab == "diagram":
                    self.window.btn_diag_zoom_in.update()
                    self.window.btn_diag_zoom_out.update()
                elif self.state.right_tab == "code":
                    self.window.btn_subtab_mod.update()
                    self.window.btn_subtab_tb.update()
                    if self.state.tb_mode == "chained":
                        self.window.btn_subtab_master.update()
                    self.window.btn_copy.update()
                    self.window.btn_code_zoom_in.update()
                    self.window.btn_code_zoom_out.update()
                    self.window.code_preview_area.update()
                elif self.state.right_tab == "paste":
                    self.window.paste_area.update()
                    self.window.btn_parse_pasted.update()
                    self.window.btn_import_file.update()
                    
                for r in self.window.port_rows:
                    r.update()
                    
            self.window.ports_scroll.virtual_height = len(self.state.ports) * int(36 * self.state.ui_font_scale)
            
            # Auto-update code cache on Preview to avoid desync
            if self.state.right_tab == "code" and not self.state.show_preferences_modal:
                self.window.update_code_cache()
                
            # Set WE cursor if hovering over divider
            on_separator = abs(mouse_pos[0] - self.state.sidebar_width) < 5
            if is_dragging_separator or (on_separator and not self.state.show_preferences_modal):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEWE)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                
            # 3. Process Events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.quit_app()
                    return
                    
                if event.type == pygame.VIDEORESIZE:
                    is_max = bool(pygame.display.get_surface().get_flags() & pygame.WINDOWMAXIMIZED)
                    if not is_max:
                        self.width = event.w
                        self.height = event.h
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.window.recalculate_all_layouts(event.w, event.h)
                    
                # Divider dragging events
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if on_separator and not self.state.show_preferences_modal:
                        is_dragging_separator = True
                        self.window.module_name_input.focused = False
                        for r in self.window.port_rows:
                            r.name_input.focused = False
                            r.width_input.focused = False
                        continue
                        
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    is_dragging_separator = False
                    
                elif event.type == pygame.MOUSEMOTION:
                    if is_dragging_separator:
                        self.state.sidebar_width = max(350, min(self.width - 400, event.pos[0]))
                        self.window.recalculate_all_layouts(self.width, self.height)
                        continue
                        
                # Delegate events to widgets
                self.window.handle_event(event, mouse_pos, self.width, self.height)
                
            # 4. Sync Settings from Preference Modal Toggles
            sel_lang = "en" if self.window.pref_lang_toggle.index == 0 else "fr"
            if loc.current_language != sel_lang:
                loc.current_language = sel_lang
                self.state.current_language = sel_lang
                
            theme_names = ["Dark (Default)", "Light", "Solarized"]
            sel_theme = theme_names[self.window.pref_theme_toggle.index]
            if self.state.current_theme_name != sel_theme:
                self.state.current_theme_name = sel_theme
                theme.apply_preset(sel_theme)
                theme.init_fonts(self.state.ui_font_scale)
                
            hdl_names = ["SystemVerilog", "Verilog", "VHDL"]
            sel_hdl = hdl_names[self.window.pref_hdl_toggle.index]
            if self.state.hdl_lang != sel_hdl:
                self.state.hdl_lang = sel_hdl
                self.window.code_preview_area.scroll_y = 0
                self.window.update_code_cache()
                
            # Always keep layouts relative
            self.window.recalculate_all_layouts(self.width, self.height)
            
            # 5. Drawing phase
            self.window.draw(self.screen, self.width, self.height)
            pygame.display.flip()
            self.clock.tick(FPS)

    def quit_app(self):
        is_max = bool(pygame.display.get_surface().get_flags() & pygame.WINDOWMAXIMIZED)
        save_prefs = {
            "window_width": self.width,
            "window_height": self.height,
            "window_maximized": is_max,
            "ui_scale": self.state.ui_font_scale,
            "editor_font_size": self.state.code_font_size,
            "theme": self.state.current_theme_name,
            "language": self.state.current_language,
            "hdl_lang": self.state.hdl_lang,
            "sidebar_width": self.state.sidebar_width
        }
        save_preferences(save_prefs)
        pygame.quit()
        sys.exit()

def main():
    app = Application()
    app.run()

if __name__ == "__main__":
    main()
