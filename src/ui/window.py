import os
import pygame
from src.ui.widgets import (
    Button, ToggleButton, Checkbox, InputBox, TextArea, ScrollArea, BlockDiagram, ToastManager, PortRow, set_clipboard_text
)
from src.ui.theme import theme
from src.core.localization import tr
import src.core.localization as loc
from src.core.config import select_open_file, select_save_file, resource_path
from src.core.parser import parse_sv_file, parse_vhdl_file, detect_clk_rst, detect_hdl_language
from src.core.generator import generate_module_code, generate_testbench_code, generate_master_tb_code

class MainWindow:
    def __init__(self, state):
        self.state = state
        self.toast = ToastManager()
        
        # --- Sidebar Controls ---
        self.btn_prefs = Button((0, 0, 100, 26), "Preferences", callback=self.open_pref)
        self.module_name_input = InputBox((0, 0, 100, 26), text=self.state.module_name, placeholder="module_name")
        self.active_low_cb = Checkbox((0, 0, 100, 26), "active_low", initial_val=self.state.is_active_low_reset)
        self.sync_reset_cb = Checkbox((0, 0, 100, 26), "sync_reset", initial_val=self.state.is_sync_reset)
        
        self.btn_add_clk = Button((0, 0, 100, 26), "Add Clock", callback=self.add_clock_preset)
        self.btn_add_rst = Button((0, 0, 100, 26), "Add Reset", callback=self.add_reset_preset)
        self.tb_mode_toggle = ToggleButton((0, 0, 100, 26), ["Standalone", "With Master"], initial_index=0 if self.state.tb_mode == "standalone" else 1)
        
        self.btn_add_input = Button((0, 0, 100, 26), "+ Input", callback=self.add_input_port, bg_color_key="ports.input")
        self.btn_add_output = Button((0, 0, 100, 26), "+ Output", callback=self.add_output_port, bg_color_key="ports.output")
        
        self.ports_scroll = ScrollArea((0, 0, 100, 100))
        self.port_rows = []
        self.rebuild_port_rows()
        
        # --- Right Panel Tabs ---
        self.btn_tab_diagram = Button((0, 0, 150, 30), "Block Diagram", callback=lambda: self.set_right_tab("diagram"))
        self.btn_tab_code = Button((0, 0, 150, 30), "Code Preview", callback=lambda: self.set_right_tab("code"))
        self.btn_tab_paste = Button((0, 0, 150, 30), "Paste or Import", callback=lambda: self.set_right_tab("paste"))
        self.btn_save = Button((0, 0, 40, 30), "", callback=self.handle_save_active, icon="save")
        
        # --- Tab 1: Diagram Widgets ---
        self.diagram_visualizer = BlockDiagram((0, 0, 100, 100))
        self.btn_diag_zoom_in = Button((0, 0, 30, 30), "+", callback=self.diag_zoom_in)
        self.btn_diag_zoom_out = Button((0, 0, 30, 30), "-", callback=self.diag_zoom_out)
        
        # --- Tab 2: Code Preview Widgets ---
        self.btn_subtab_mod = Button((0, 0, 120, 26), "Module Code", callback=lambda: self.set_subtab("module"))
        self.btn_subtab_tb = Button((0, 0, 120, 26), "Testbench Code", callback=lambda: self.set_subtab("testbench"))
        self.btn_subtab_master = Button((0, 0, 120, 26), "Master TB Code", callback=lambda: self.set_subtab("master"))
        self.btn_copy = Button((0, 0, 120, 26), "Copy Code", callback=self.handle_copy_code, is_accent=True)
        self.btn_code_zoom_in = Button((0, 0, 30, 26), "+", callback=self.code_zoom_in)
        self.btn_code_zoom_out = Button((0, 0, 30, 26), "-", callback=self.code_zoom_out)
        self.code_preview_area = TextArea((0, 0, 100, 100), read_only=True, syntax_highlight=True)
        
        # --- Tab 3: Paste SV Code Widgets ---
        self.paste_area = TextArea((0, 0, 100, 100), placeholder="Paste your SystemVerilog module code here...")
        self.btn_parse_pasted = Button((0, 0, 200, 30), "Parse Pasted Code", callback=self.handle_parse_pasted, is_accent=True)
        self.btn_import_file = Button((0, 0, 200, 30), "Import SV File", callback=self.handle_parse_file, bg_color_key="list.activeSelectionBackground")
        
        # --- Preferences Modal Controls ---
        self.pref_lang_toggle = ToggleButton((0, 0, 180, 26), ["English", "Français"], initial_index=0 if loc.current_language == "en" else 1)
        theme_names = ["Dark (Default)", "Light", "Solarized"]
        self.pref_theme_toggle = ToggleButton((0, 0, 180, 26), theme_names, initial_index=theme_names.index(self.state.current_theme_name))
        hdl_names = ["SystemVerilog", "Verilog", "VHDL"]
        self.pref_hdl_toggle = ToggleButton((0, 0, 180, 26), hdl_names, initial_index=hdl_names.index(self.state.hdl_lang))
        self.btn_pref_ui_dec = Button((0, 0, 30, 26), "-", callback=self.ui_scale_dec)
        self.btn_pref_ui_inc = Button((0, 0, 30, 26), "+", callback=self.ui_scale_inc)
        self.btn_pref_ed_dec = Button((0, 0, 30, 26), "-", callback=self.ed_dec)
        self.btn_pref_ed_inc = Button((0, 0, 30, 26), "+", callback=self.ed_inc)
        self.btn_pref_close = Button((0, 0, 150, 30), "Close", callback=self.close_pref, is_accent=True)
        
        # Initial updates
        self.code_preview_area.line_h = self.state.code_font_size + 4
        self.paste_area.line_h = self.state.code_font_size + 4
        self.update_code_cache()
        self.update_tab_highlights()

    # --- Callbacks ---
    def set_right_tab(self, tab):
        self.state.right_tab = tab
        self.code_preview_area.scroll_y = 0
        self.paste_area.scroll_y = 0
        self.update_code_cache()
        self.update_tab_highlights()

    def set_subtab(self, sub):
        self.state.code_subtab = sub
        self.code_preview_area.scroll_y = 0
        self.update_code_cache()
        self.update_tab_highlights()

    def open_pref(self):
        self.state.show_preferences_modal = True
        self.pref_lang_toggle.index = 0 if loc.current_language == "en" else 1

    def close_pref(self):
        self.state.show_preferences_modal = False

    def ui_scale_dec(self):
        self.state.ui_font_scale = max(0.6, self.state.ui_font_scale - 0.1)
        theme.init_fonts(self.state.ui_font_scale)
        self.toast.show(f"UI Size: {int(self.state.ui_font_scale * 100)}%")

    def ui_scale_inc(self):
        self.state.ui_font_scale = min(1.8, self.state.ui_font_scale + 0.1)
        theme.init_fonts(self.state.ui_font_scale)
        self.toast.show(f"UI Size: {int(self.state.ui_font_scale * 100)}%")

    def ed_dec(self):
        self.state.code_font_size = max(10, self.state.code_font_size - 2)
        theme.fonts["code"] = pygame.font.SysFont(theme.mono_name, self.state.code_font_size)
        theme.fonts["code_large"] = pygame.font.SysFont(theme.mono_name, self.state.code_font_size + 2)
        self.code_preview_area.line_h = self.state.code_font_size + 4
        self.paste_area.line_h = self.state.code_font_size + 4
        self.update_code_cache()
        self.toast.show(f"Editor Font Size: {self.state.code_font_size}px")

    def ed_inc(self):
        self.state.code_font_size = min(32, self.state.code_font_size + 2)
        theme.fonts["code"] = pygame.font.SysFont(theme.mono_name, self.state.code_font_size)
        theme.fonts["code_large"] = pygame.font.SysFont(theme.mono_name, self.state.code_font_size + 2)
        self.code_preview_area.line_h = self.state.code_font_size + 4
        self.paste_area.line_h = self.state.code_font_size + 4
        self.update_code_cache()
        self.toast.show(f"Editor Font Size: {self.state.code_font_size}px")

    def code_zoom_in(self):
        self.ed_inc()

    def code_zoom_out(self):
        self.ed_dec()

    def diag_zoom_in(self):
        self.diagram_visualizer.scale = min(2.0, self.diagram_visualizer.scale + 0.1)
        self.toast.show(f"Diagram Scale: {int(self.diagram_visualizer.scale * 100)}%")

    def diag_zoom_out(self):
        self.diagram_visualizer.scale = max(0.5, self.diagram_visualizer.scale - 0.1)
        self.toast.show(f"Diagram Scale: {int(self.diagram_visualizer.scale * 100)}%")

    def delete_port(self, idx):
        if 0 <= idx < len(self.state.ports):
            deleted_name = self.state.ports[idx]["name"]
            self.state.ports.pop(idx)
            self.rebuild_port_rows()
            self.toast.show(f"Deleted port '{deleted_name}'")

    def rebuild_port_rows(self):
        self.port_rows = []
        for idx, p in enumerate(self.state.ports):
            row = PortRow(idx, p, self.delete_port)
            self.port_rows.append(row)

    def add_clock_preset(self):
        if any(p["name"] == "clk" for p in self.state.ports):
            self.toast.show("Clock port 'clk' already exists", is_error=True)
            return
        self.state.ports.insert(0, {"name": "clk", "dir": "IN", "width": "1"})
        self.rebuild_port_rows()
        self.toast.show("Added clock 'clk'")

    def add_reset_preset(self):
        rst_name = "rst_n" if self.state.is_active_low_reset else "rst"
        if any(p["name"] == rst_name for p in self.state.ports):
            self.toast.show(f"Reset port '{rst_name}' already exists", is_error=True)
            return
        idx = 1 if (self.state.ports and self.state.ports[0]["name"] == "clk") else 0
        self.state.ports.insert(idx, {"name": rst_name, "dir": "IN", "width": "1"})
        self.rebuild_port_rows()
        self.toast.show(f"Added reset '{rst_name}'")

    def add_input_port(self):
        name = f"in_port_{len(self.state.ports)}"
        self.state.ports.append({"name": name, "dir": "IN", "width": "1"})
        self.rebuild_port_rows()
        self.ports_scroll.scroll_y = max(0, len(self.state.ports) * int(36 * self.state.ui_font_scale) - self.ports_scroll.rect.height)
        self.toast.show(f"Added input '{name}'")

    def add_output_port(self):
        name = f"out_port_{len(self.state.ports)}"
        self.state.ports.append({"name": name, "dir": "OUT", "width": "1"})
        self.rebuild_port_rows()
        self.ports_scroll.scroll_y = max(0, len(self.state.ports) * int(36 * self.state.ui_font_scale) - self.ports_scroll.rect.height)
        self.toast.show(f"Added output '{name}'")

    def handle_copy_code(self):
        code_str = self.code_preview_area.text
        set_clipboard_text(code_str)
        self.toast.show("Code copied to clipboard!")

    def handle_save_active(self):
        ext_map = {
            "SystemVerilog": ".sv",
            "Verilog": ".v",
            "VHDL": ".vhd"
        }
        ext = ext_map.get(self.state.hdl_lang, ".sv")
        
        default_name = ""
        if self.state.code_subtab == "module":
            default_name = f"{self.state.module_name}{ext}"
        elif self.state.code_subtab == "testbench":
            default_name = f"tb_{self.state.module_name}{ext}"
        else:
            default_name = "master_tb.sv"
            
        file_path = select_save_file(default_name, is_tb=(self.state.code_subtab != "module"))
        if file_path:
            try:
                code_str = self.code_preview_area.text
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(code_str)
                self.toast.show(f"Saved successfully to '{os.path.basename(file_path)}'")
            except Exception as e:
                self.toast.show(f"Save failed: {e}", is_error=True)

    def handle_parse_file(self):
        path = select_open_file()
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.paste_area.text = content
                self.paste_area.cursor_pos = len(content)
                self.perform_parse(content)
            except Exception as e:
                self.toast.show(f"{tr('toast_parse_error')}{e}", is_error=True)

    def handle_parse_pasted(self):
        content = self.paste_area.text
        if content.strip():
            self.perform_parse(content)
        else:
            self.toast.show("Paste area is empty!", is_error=True)

    def perform_parse(self, content):
        try:
            detected_lang = detect_hdl_language(content)
            if detected_lang != "Unknown" and detected_lang != self.state.hdl_lang:
                msg = f"Incohérence : Le code collé est {detected_lang}, attendu {self.state.hdl_lang}" if loc.current_language == "fr" else f"Language mismatch: Paste is {detected_lang}, expected {self.state.hdl_lang}"
                self.toast.show(msg, is_error=True)
                
            if detected_lang == "VHDL" or self.state.hdl_lang == "VHDL":
                parsed_name, parsed_ports = parse_vhdl_file(content)
            else:
                parsed_name, parsed_ports = parse_sv_file(content)
                
            if parsed_name:
                self.state.module_name = parsed_name
                self.module_name_input.text = parsed_name
                self.module_name_input.cursor_pos = len(parsed_name)
                self.state.ports = parsed_ports
                
                clk_p, rst_p = detect_clk_rst(self.state.ports)
                if rst_p:
                    self.state.is_active_low_reset = rst_p["name"].lower().endswith("n") or rst_p["name"].lower().endswith("b")
                    self.active_low_cb.checked = self.state.is_active_low_reset
                    
                self.rebuild_port_rows()
                self.ports_scroll.scroll_y = 0
                self.update_code_cache()
                self.toast.show(f"Parsed module '{parsed_name}' ({len(self.state.ports)} ports)")
                self.set_right_tab("diagram")
            else:
                self.toast.show("No valid module declaration found", is_error=True)
        except Exception as e:
            self.toast.show(f"Error parsing code: {e}", is_error=True)

    def get_master_tb_code(self):
        if self.state.module_name.lower() in ["alu", "regfile", "reg_file"]:
            sub_tbs = [
                {"module_name": "alu"},
                {"module_name": "regfile"}
            ]
        else:
            sub_tbs = [
                {"module_name": self.state.module_name},
                {"module_name": "other_module"}
            ]
        return generate_master_tb_code(sub_tbs)

    def update_code_cache(self):
        if self.state.code_subtab == "module":
            code_str = generate_module_code(self.state.module_name, self.state.ports, hdl_lang=self.state.hdl_lang)
        elif self.state.code_subtab == "testbench":
            code_str = generate_testbench_code(
                self.state.module_name, self.state.ports, self.state.is_sync_reset, self.state.is_active_low_reset, self.state.tb_mode, hdl_lang=self.state.hdl_lang
            )
        else:
            code_str = self.get_master_tb_code()
            
        self.code_preview_area.text = code_str

    def update_tab_highlights(self):
        self.btn_tab_diagram.is_accent = (self.state.right_tab == "diagram")
        self.btn_tab_code.is_accent = (self.state.right_tab == "code")
        self.btn_tab_paste.is_accent = (self.state.right_tab == "paste")
        self.btn_subtab_mod.is_accent = (self.state.code_subtab == "module")
        self.btn_subtab_tb.is_accent = (self.state.code_subtab == "testbench")
        self.btn_subtab_master.is_accent = (self.state.code_subtab == "master")

    # --- UI Layout Calculations ---
    def recalculate_all_layouts(self, w_width, w_height):
        scale = self.state.ui_font_scale
        sidebar_width = self.state.sidebar_width
        pad = int(20 * scale)
        h_widget = int(26 * scale)
        
        # Title & Prefs
        title_y = int(20 * scale)
        lbl_title_h = theme.fonts["header"].get_linesize()
        
        self.btn_prefs.rect.width = int(100 * scale)
        self.btn_prefs.rect.height = h_widget
        self.btn_prefs.rect.x = sidebar_width - self.btn_prefs.rect.width - pad
        self.btn_prefs.rect.y = title_y
        
        # Module Name Row
        mod_name_y = title_y + lbl_title_h + int(15 * scale)
        lbl_mod_w = theme.fonts["body"].size(tr("module_name"))[0]
        self.module_name_input.rect.x = pad + lbl_mod_w + int(10 * scale)
        self.module_name_input.rect.y = mod_name_y + (theme.fonts["body"].get_height() - h_widget) // 2
        self.module_name_input.rect.width = sidebar_width - self.module_name_input.rect.x - pad
        self.module_name_input.rect.height = h_widget
        
        # Checkboxes Row
        cb_y = max(self.module_name_input.rect.bottom, mod_name_y + theme.fonts["body"].get_height()) + int(12 * scale)
        cb_w = (sidebar_width - pad * 2 - int(10 * scale)) // 2
        self.active_low_cb.rect = pygame.Rect(pad, cb_y, cb_w, h_widget)
        self.sync_reset_cb.rect = pygame.Rect(pad + cb_w + int(10 * scale), cb_y, cb_w, h_widget)
        
        # Add Clock / Add Reset
        btn_y = cb_y + h_widget + int(12 * scale)
        btn_w = (sidebar_width - pad * 2 - int(10 * scale)) // 2
        self.btn_add_clk.rect = pygame.Rect(pad, btn_y, btn_w, h_widget)
        self.btn_add_rst.rect = pygame.Rect(pad + btn_w + int(10 * scale), btn_y, btn_w, h_widget)
        
        # Testbench settings
        self.line1_y = btn_y + h_widget + int(15 * scale)
        self.lbl_tb_title_y = self.line1_y + int(8 * scale)
        lbl_tb_title_h = theme.fonts["body_bold"].get_height()
        
        toggle_y = self.lbl_tb_title_y + lbl_tb_title_h + int(10 * scale)
        self.tb_mode_toggle.rect = pygame.Rect(pad, toggle_y, sidebar_width - pad * 2, h_widget)
        
        # Module Ports Header
        self.line2_y = toggle_y + h_widget + int(15 * scale)
        self.lbl_ports_y = self.line2_y + int(8 * scale)
        lbl_ports_h = theme.fonts["body_bold"].get_height()
        
        # Add Input / Add Output
        btn_pw = int(110 * scale)
        self.btn_add_output.rect.width = btn_pw
        self.btn_add_output.rect.height = h_widget
        self.btn_add_output.rect.x = sidebar_width - pad - btn_pw
        self.btn_add_output.rect.y = self.lbl_ports_y + (lbl_ports_h - h_widget) // 2
        
        self.btn_add_input.rect.width = btn_pw
        self.btn_add_input.rect.height = h_widget
        self.btn_add_input.rect.x = self.btn_add_output.rect.x - int(10 * scale) - btn_pw
        self.btn_add_input.rect.y = self.btn_add_output.rect.y
        
        # Scroll Area
        scroll_y_start = max(self.lbl_ports_y + lbl_ports_h, self.btn_add_input.rect.bottom) + int(10 * scale)
        self.ports_scroll.rect.x = pad
        self.ports_scroll.rect.y = scroll_y_start
        self.ports_scroll.rect.width = sidebar_width - pad * 2
        self.ports_scroll.rect.height = w_height - scroll_y_start - int(20 * scale)
        
        # Right Panel layouts
        right_margin = int(20 * scale)
        gap = int(10 * scale)
        tab_w = int(150 * scale)
        tab_h = int(30 * scale)
        
        self.btn_tab_diagram.rect.width = tab_w
        self.btn_tab_diagram.rect.height = tab_h
        self.btn_tab_diagram.rect.x = sidebar_width + int(20 * scale)
        self.btn_tab_diagram.rect.y = int(20 * scale)
        
        self.btn_tab_code.rect.width = tab_w
        self.btn_tab_code.rect.height = tab_h
        self.btn_tab_code.rect.x = self.btn_tab_diagram.rect.right + gap
        self.btn_tab_code.rect.y = self.btn_tab_diagram.rect.y
        
        self.btn_tab_paste.rect.width = tab_w
        self.btn_tab_paste.rect.height = tab_h
        self.btn_tab_paste.rect.x = self.btn_tab_code.rect.right + gap
        self.btn_tab_paste.rect.y = self.btn_tab_diagram.rect.y
        
        save_w = int(40 * scale)
        save_h = int(30 * scale)
        self.btn_save.rect.width = save_w
        self.btn_save.rect.height = save_h
        self.btn_save.rect.x = w_width - save_w - right_margin
        self.btn_save.rect.y = self.btn_tab_diagram.rect.y
        
        # Subtabs zoom Zoom Zoom
        sub_w = int(120 * scale)
        sub_h = int(26 * scale)
        subtab_y = self.btn_tab_diagram.rect.bottom + int(15 * scale)
        
        self.btn_subtab_mod.rect.width = sub_w
        self.btn_subtab_mod.rect.height = sub_h
        self.btn_subtab_mod.rect.x = sidebar_width + int(20 * scale)
        self.btn_subtab_mod.rect.y = subtab_y
        
        self.btn_subtab_tb.rect.width = sub_w
        self.btn_subtab_tb.rect.height = sub_h
        self.btn_subtab_tb.rect.x = self.btn_subtab_mod.rect.right + gap
        self.btn_subtab_tb.rect.y = subtab_y
        
        self.btn_subtab_master.rect.width = sub_w
        self.btn_subtab_master.rect.height = sub_h
        self.btn_subtab_master.rect.x = self.btn_subtab_tb.rect.right + gap
        self.btn_subtab_master.rect.y = subtab_y
        
        w_zoom = int(30 * scale)
        self.btn_copy.rect.width = int(120 * scale)
        self.btn_copy.rect.height = sub_h
        self.btn_copy.rect.x = w_width - right_margin - self.btn_copy.rect.width
        self.btn_copy.rect.y = subtab_y
        
        self.btn_code_zoom_out.rect.width = w_zoom
        self.btn_code_zoom_out.rect.height = sub_h
        self.btn_code_zoom_out.rect.x = self.btn_copy.rect.x - gap - w_zoom
        self.btn_code_zoom_out.rect.y = subtab_y
        
        self.btn_code_zoom_in.rect.width = w_zoom
        self.btn_code_zoom_in.rect.height = sub_h
        self.btn_code_zoom_in.rect.x = self.btn_code_zoom_out.rect.x - gap - w_zoom
        self.btn_code_zoom_in.rect.y = subtab_y
        
        # Diagram
        self.diagram_visualizer.rect.x = sidebar_width + int(20 * scale)
        self.diagram_visualizer.rect.y = self.btn_tab_diagram.rect.bottom + int(15 * scale)
        self.diagram_visualizer.rect.width = w_width - self.diagram_visualizer.rect.x - right_margin
        self.diagram_visualizer.rect.height = w_height - self.diagram_visualizer.rect.y - right_margin
        
        w_diag_zoom = int(30 * scale)
        h_diag_zoom = int(30 * scale)
        self.btn_diag_zoom_out.rect.width = w_diag_zoom
        self.btn_diag_zoom_out.rect.height = h_diag_zoom
        self.btn_diag_zoom_out.rect.x = w_width - right_margin - w_diag_zoom - int(10 * scale)
        self.btn_diag_zoom_out.rect.y = self.diagram_visualizer.rect.y + int(15 * scale)
        
        self.btn_diag_zoom_in.rect.width = w_diag_zoom
        self.btn_diag_zoom_in.rect.height = h_diag_zoom
        self.btn_diag_zoom_in.rect.x = self.btn_diag_zoom_out.rect.x - w_diag_zoom - int(8 * scale)
        self.btn_diag_zoom_in.rect.y = self.btn_diag_zoom_out.rect.y
        
        # Areas
        self.code_preview_area.rect.x = sidebar_width + int(20 * scale)
        self.code_preview_area.rect.y = subtab_y + sub_h + int(10 * scale)
        self.code_preview_area.rect.width = w_width - self.code_preview_area.rect.x - right_margin
        self.code_preview_area.rect.height = w_height - self.code_preview_area.rect.y - right_margin
        
        btn_w = int(200 * scale)
        btn_h = int(30 * scale)
        self.btn_parse_pasted.rect.width = btn_w
        self.btn_parse_pasted.rect.height = btn_h
        self.btn_parse_pasted.rect.x = w_width - right_margin - btn_w
        self.btn_parse_pasted.rect.y = w_height - btn_h - int(20 * scale)
        
        self.btn_import_file.rect.width = btn_w
        self.btn_import_file.rect.height = btn_h
        self.btn_import_file.rect.x = self.btn_parse_pasted.rect.x - btn_w - int(15 * scale)
        self.btn_import_file.rect.y = self.btn_parse_pasted.rect.y
        
        self.paste_area.rect.x = sidebar_width + int(20 * scale)
        self.paste_area.rect.y = self.btn_tab_diagram.rect.bottom + int(15 * scale)
        self.paste_area.rect.width = w_width - self.paste_area.rect.x - right_margin
        self.paste_area.rect.height = self.btn_parse_pasted.rect.y - self.paste_area.rect.y - int(15 * scale)
        
        # Modal Card Layout
        self.pref_card_w = int(450 * scale)
        self.pref_card_h = int(400 * scale)
        card_x = (w_width - self.pref_card_w) // 2
        card_y = (w_height - self.pref_card_h) // 2
        
        self.pref_lang_toggle.rect.topleft = (card_x + int(220 * scale), card_y + int(75 * scale))
        self.pref_lang_toggle.rect.width = int(180 * scale)
        self.pref_lang_toggle.rect.height = h_widget
        
        self.btn_pref_ui_dec.rect.topleft = (card_x + int(220 * scale), card_y + int(125 * scale))
        self.btn_pref_ui_dec.rect.width = int(30 * scale)
        self.btn_pref_ui_dec.rect.height = h_widget
        
        self.btn_pref_ui_inc.rect.topleft = (card_x + int(350 * scale), card_y + int(125 * scale))
        self.btn_pref_ui_inc.rect.width = int(30 * scale)
        self.btn_pref_ui_inc.rect.height = h_widget
        
        self.btn_pref_ed_dec.rect.topleft = (card_x + int(220 * scale), card_y + int(175 * scale))
        self.btn_pref_ed_dec.rect.width = int(30 * scale)
        self.btn_pref_ed_dec.rect.height = h_widget
        
        self.btn_pref_ed_inc.rect.topleft = (card_x + int(350 * scale), card_y + int(175 * scale))
        self.btn_pref_ed_inc.rect.width = int(30 * scale)
        self.btn_pref_ed_inc.rect.height = h_widget
        
        self.pref_theme_toggle.rect.topleft = (card_x + int(220 * scale), card_y + int(225 * scale))
        self.pref_theme_toggle.rect.width = int(180 * scale)
        self.pref_theme_toggle.rect.height = h_widget
        
        self.pref_hdl_toggle.rect.topleft = (card_x + int(220 * scale), card_y + int(275 * scale))
        self.pref_hdl_toggle.rect.width = int(180 * scale)
        self.pref_hdl_toggle.rect.height = h_widget
        
        self.btn_pref_close.rect.width = int(150 * scale)
        self.btn_pref_close.rect.height = int(30 * scale)
        self.btn_pref_close.rect.topleft = (card_x + (self.pref_card_w - self.btn_pref_close.rect.width) // 2, card_y + int(340 * scale))

    # --- Draw Panels & Controls ---
    def draw(self, screen, w_width, w_height):
        # Background
        screen.fill(theme.colors["editor.background"])
        
        # 1. DRAW SIDEBAR
        sidebar_width = self.state.sidebar_width
        sidebar_rect = pygame.Rect(0, 0, sidebar_width, w_height)
        pygame.draw.rect(screen, theme.colors["sideBar.background"], sidebar_rect)
        pygame.draw.line(screen, theme.colors["sideBar.border"], (sidebar_width, 0), (sidebar_width, w_height), 2)
        
        scale = self.state.ui_font_scale
        pad = int(20 * scale)
        
        # App Title
        lbl_title = theme.fonts["header"].render(tr("title"), True, theme.colors["editor.foreground"])
        screen.blit(lbl_title, (pad, int(20 * scale)))
        self.btn_prefs.draw(screen)
        
        # Module Name Text label
        lbl_mod = theme.fonts["body"].render(tr("module_name"), True, theme.colors["editor.foreground"])
        lbl_mod_y = self.module_name_input.rect.y + (self.module_name_input.rect.height - lbl_mod.get_height()) // 2
        screen.blit(lbl_mod, (pad, lbl_mod_y))
        
        # Inputs & checkbox
        self.module_name_input.draw(screen)
        self.active_low_cb.draw(screen)
        self.sync_reset_cb.draw(screen)
        self.btn_add_clk.draw(screen)
        self.btn_add_rst.draw(screen)
        
        # Testbench Setting segment header
        pygame.draw.line(screen, theme.colors["sideBar.border"], (pad, self.line1_y), (sidebar_width - pad, self.line1_y), 1)
        lbl_tb_title = theme.fonts["body_bold"].render(tr("tb_settings"), True, theme.colors["editor.foreground"])
        screen.blit(lbl_tb_title, (pad, self.lbl_tb_title_y))
        self.tb_mode_toggle.draw(screen)
        
        # Ports segment header
        pygame.draw.line(screen, theme.colors["sideBar.border"], (pad, self.line2_y), (sidebar_width - pad, self.line2_y), 1)
        lbl_ports = theme.fonts["body_bold"].render(tr("module_ports"), True, theme.colors["editor.foreground"])
        screen.blit(lbl_ports, (pad, self.lbl_ports_y))
        self.btn_add_input.draw(screen)
        self.btn_add_output.draw(screen)
        
        # Ports List scroll content drawer
        def draw_ports_list(surface, scroll_y):
            row_start_y = self.ports_scroll.rect.y
            row_total_h = int(36 * scale)
            pad_ports = int(20 * scale)
            h_widget = int(26 * scale)
            for idx, r in enumerate(self.port_rows):
                ry = row_start_y + idx * row_total_h
                r.set_positions(pad_ports, ry, sidebar_width - pad_ports * 2, h_widget)
                
                original_pos = (r.dir_toggle.rect.y, r.name_input.rect.y, r.width_input.rect.y, r.del_btn.rect.y)
                r.dir_toggle.rect.y -= scroll_y
                r.name_input.rect.y -= scroll_y
                r.width_input.rect.y -= scroll_y
                r.del_btn.rect.y -= scroll_y
                
                r.draw(surface)
                
                r.dir_toggle.rect.y = original_pos[0]
                r.name_input.rect.y = original_pos[1]
                r.width_input.rect.y = original_pos[2]
                r.del_btn.rect.y = original_pos[3]
                
        self.ports_scroll.draw(screen, draw_ports_list)
        
        # 2. DRAW RIGHT PANEL
        self.btn_tab_diagram.draw(screen)
        self.btn_tab_code.draw(screen)
        self.btn_tab_paste.draw(screen)
        self.btn_save.draw(screen)
        
        if self.state.right_tab == "diagram":
            self.diagram_visualizer.draw(screen, self.state.module_name, self.state.ports)
            self.btn_diag_zoom_in.draw(screen)
            self.btn_diag_zoom_out.draw(screen)
            
        elif self.state.right_tab == "code":
            bg_y = self.btn_tab_diagram.rect.bottom + int(10 * scale)
            bg_h = w_height - bg_y - int(20 * scale)
            code_bg_rect = pygame.Rect(sidebar_width + pad, bg_y, w_width - sidebar_width - pad * 2, bg_h)
            pygame.draw.rect(screen, theme.colors["sideBar.background"], code_bg_rect, border_radius=12)
            pygame.draw.rect(screen, theme.colors["sideBar.border"], code_bg_rect, width=2, border_radius=12)
            
            self.btn_subtab_mod.draw(screen)
            self.btn_subtab_tb.draw(screen)
            if self.state.tb_mode == "chained":
                self.btn_subtab_master.draw(screen)
            self.btn_copy.draw(screen)
            self.btn_code_zoom_in.draw(screen)
            self.btn_code_zoom_out.draw(screen)
            
            subtab_bottom = self.btn_subtab_mod.rect.bottom + int(5 * scale)
            pygame.draw.line(screen, theme.colors["sideBar.border"], (sidebar_width + pad, subtab_bottom), (w_width - pad, subtab_bottom), 1)
            self.code_preview_area.draw(screen)
            
        elif self.state.right_tab == "paste":
            self.paste_area.draw(screen)
            self.btn_parse_pasted.draw(screen)
            self.btn_import_file.draw(screen)
            
        # 3. DRAW PREFERENCES DIALOG MODAL
        if self.state.show_preferences_modal:
            overlay = pygame.Surface((w_width, w_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            card_x = (w_width - self.pref_card_w) // 2
            card_y = (w_height - self.pref_card_h) // 2
            
            card_rect = pygame.Rect(card_x, card_y, self.pref_card_w, self.pref_card_h)
            pygame.draw.rect(screen, theme.colors["sideBar.background"], card_rect, border_radius=12)
            pygame.draw.rect(screen, theme.colors["sideBar.border"], card_rect, width=2, border_radius=12)
            
            lbl_pref_title = theme.fonts["header"].render(tr("pref_title"), True, theme.colors["editor.foreground"])
            screen.blit(lbl_pref_title, (card_x + (self.pref_card_w - lbl_pref_title.get_width()) // 2, card_y + int(20 * scale)))
            
            # Row 1: Language
            lbl_lang = theme.fonts["body_bold"].render(tr("pref_lang"), True, theme.colors["editor.foreground"])
            screen.blit(lbl_lang, (card_x + int(30 * scale), card_y + int(80 * scale)))
            self.pref_lang_toggle.draw(screen)
            
            # Row 2: UI Scale
            lbl_ui = theme.fonts["body_bold"].render(tr("pref_ui_scale"), True, theme.colors["editor.foreground"])
            screen.blit(lbl_ui, (card_x + int(30 * scale), card_y + int(130 * scale)))
            self.btn_pref_ui_dec.draw(screen)
            self.btn_pref_ui_inc.draw(screen)
            
            lbl_ui_val = theme.fonts["body"].render(f"{int(self.state.ui_font_scale * 100)}%", True, theme.colors["editor.foreground"])
            lbl_ui_val_x = self.btn_pref_ui_dec.rect.right + (self.btn_pref_ui_inc.rect.left - self.btn_pref_ui_dec.rect.right - lbl_ui_val.get_width()) // 2
            lbl_ui_val_y = self.btn_pref_ui_dec.rect.y + (self.btn_pref_ui_dec.rect.height - lbl_ui_val.get_height()) // 2
            screen.blit(lbl_ui_val, (lbl_ui_val_x, lbl_ui_val_y))
            
            # Row 3: Editor Size
            lbl_ed = theme.fonts["body_bold"].render(tr("pref_editor_size"), True, theme.colors["editor.foreground"])
            screen.blit(lbl_ed, (card_x + int(30 * scale), card_y + int(180 * scale)))
            self.btn_pref_ed_dec.draw(screen)
            self.btn_pref_ed_inc.draw(screen)
            
            lbl_ed_val = theme.fonts["body"].render(f"{self.state.code_font_size}px", True, theme.colors["editor.foreground"])
            lbl_ed_val_x = self.btn_pref_ed_dec.rect.right + (self.btn_pref_ed_inc.rect.left - self.btn_pref_ed_dec.rect.right - lbl_ed_val.get_width()) // 2
            lbl_ed_val_y = self.btn_pref_ed_dec.rect.y + (self.btn_pref_ed_dec.rect.height - lbl_ed_val.get_height()) // 2
            screen.blit(lbl_ed_val, (lbl_ed_val_x, lbl_ed_val_y))
            
            # Row 4: Theme
            lbl_th = theme.fonts["body_bold"].render(tr("pref_theme"), True, theme.colors["editor.foreground"])
            screen.blit(lbl_th, (card_x + int(30 * scale), card_y + int(230 * scale)))
            self.pref_theme_toggle.draw(screen)
            
            # Row 5: HDL Language
            lbl_hdl = theme.fonts["body_bold"].render(tr("pref_hdl"), True, theme.colors["editor.foreground"])
            screen.blit(lbl_hdl, (card_x + int(30 * scale), card_y + int(280 * scale)))
            self.pref_hdl_toggle.draw(screen)
            
            self.btn_pref_close.draw(screen)
            
        # 4. DRAW TOASTS
        self.toast.draw(screen, w_width, w_height)

    # --- Event Handling ---
    def handle_event(self, event, mouse_pos, w_width, w_height):
        # Divider separation drag area calculations
        sidebar_width = self.state.sidebar_width
        on_separator = abs(mouse_pos[0] - sidebar_width) < 5
        
        # Modal locks events in background
        if self.state.show_preferences_modal:
            self.pref_lang_toggle.handle_event(event)
            self.pref_theme_toggle.handle_event(event)
            self.pref_hdl_toggle.handle_event(event)
            self.btn_pref_ui_dec.handle_event(event)
            self.btn_pref_ui_inc.handle_event(event)
            self.btn_pref_ed_dec.handle_event(event)
            self.btn_pref_ed_inc.handle_event(event)
            self.btn_pref_close.handle_event(event)
            return True

        # Global Tab Key Navigation
        if event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
            focusable = [self.module_name_input]
            for r in self.port_rows:
                focusable.append(r.name_input)
                focusable.append(r.width_input)
                
            curr_idx = -1
            for idx, w in enumerate(focusable):
                if w.focused:
                    w.focused = False
                    w.cursor_pos = len(w.text)
                    curr_idx = idx
                    break
            
            if curr_idx != -1:
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    next_idx = (curr_idx - 1) % len(focusable)
                else:
                    next_idx = (curr_idx + 1) % len(focusable)
                focusable[next_idx].focused = True
                
                # Auto scroll to view ports list focus
                start_ports_idx = 1
                if next_idx >= start_ports_idx:
                    row_idx = (next_idx - start_ports_idx) // 2
                    row_total_h = int(36 * self.state.ui_font_scale)
                    target_vy = row_idx * row_total_h
                    viewport_h = self.ports_scroll.rect.height
                    if target_vy < self.ports_scroll.scroll_y:
                        self.ports_scroll.scroll_y = target_vy
                    elif target_vy + row_total_h > self.ports_scroll.scroll_y + viewport_h:
                        self.ports_scroll.scroll_y = target_vy + row_total_h - viewport_h
            return True

        # Left panel controls
        self.module_name_input.handle_event(event)
        self.active_low_cb.handle_event(event)
        self.sync_reset_cb.handle_event(event)
        self.btn_add_clk.handle_event(event)
        self.btn_add_rst.handle_event(event)
        self.tb_mode_toggle.handle_event(event)
        self.btn_add_input.handle_event(event)
        self.btn_add_output.handle_event(event)
        self.btn_prefs.handle_event(event)
        
        # Right panel main tabs
        self.btn_tab_diagram.handle_event(event)
        self.btn_tab_code.handle_event(event)
        self.btn_tab_paste.handle_event(event)
        self.btn_save.handle_event(event)
        
        # Sub panel conditions
        if self.state.right_tab == "diagram":
            self.btn_diag_zoom_in.handle_event(event)
            self.btn_diag_zoom_out.handle_event(event)
        elif self.state.right_tab == "code":
            self.btn_subtab_mod.handle_event(event)
            self.btn_subtab_tb.handle_event(event)
            if self.state.tb_mode == "chained":
                self.btn_subtab_master.handle_event(event)
            self.btn_copy.handle_event(event)
            self.btn_code_zoom_in.handle_event(event)
            self.btn_code_zoom_out.handle_event(event)
            self.code_preview_area.handle_event(event)
        elif self.state.right_tab == "paste":
            self.paste_area.handle_event(event)
            self.btn_parse_pasted.handle_event(event)
            self.btn_import_file.handle_event(event)
            
        # Sidebar scroll
        self.ports_scroll.handle_event(event)
        
        # Port rows event handling
        in_scroll_viewport = self.ports_scroll.rect.collidepoint(mouse_pos)
        offset_pos = (mouse_pos[0], mouse_pos[1] + self.ports_scroll.scroll_y) if in_scroll_viewport else (-1, -1)
        for r in self.port_rows:
            r.handle_event(event, offset_pos)
            
        return False
