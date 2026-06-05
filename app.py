import ctypes
import os
import sys

# Set DPI awareness and AppUserModelID for Windows to prevent blurry fonts and generic taskbar icon
if sys.platform.startswith("win"):
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass
    try:
        # Give the process a unique App ID before creating any window/UI, so Windows displays the custom taskbar icon
        myappid = "Tools.hdl.1.0"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

import pygame
import tkinter as tk
from tkinter import filedialog

def resource_path(relative_path):
    """Obtient le chemin absolu vers la ressource, fonctionne pour dev et pour PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# Asset Paths Setup
DOSSIER_COURANT = resource_path(".")
DOSSIER_IMAGES = os.path.join(DOSSIER_COURANT, "assets", "images")

# Ensure assets directory and default icon exist before loading
try:
    os.makedirs(DOSSIER_IMAGES, exist_ok=True)
except Exception:
    pass

chemin_icone = os.path.join(DOSSIER_IMAGES, "icone.png")
if not os.path.exists(chemin_icone):
    try:
        pygame.init()
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(surf, (0, 229, 255), (6, 6, 20, 20), border_radius=4)
        for i in range(4):
            py = 9 + i * 5
            pygame.draw.line(surf, (0, 229, 255), (2, py), (5, py), 1)
            pygame.draw.line(surf, (0, 229, 255), (26, py), (29, py), 1)
        pygame.image.save(surf, chemin_icone)
    except Exception:
        pass

# Ensure diskette.png exists
chemin_disquette = os.path.join(DOSSIER_IMAGES, "diskette.png")
if not os.path.exists(chemin_disquette):
    try:
        pygame.init()
        temp_d = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(temp_d, (201, 209, 217), (4, 4, 24, 24), border_radius=2)
        pygame.draw.rect(temp_d, (20, 24, 33), (8, 6, 16, 6))
        pygame.draw.rect(temp_d, (20, 24, 33), (10, 18, 12, 10))
        pygame.image.save(temp_d, chemin_disquette)
    except Exception:
        pass

# Import our custom components
from ui_components import (
    theme, Button, ToggleButton, Checkbox, 
    ScrollArea, PortRow, BlockDiagram, ToastManager,
    TextArea, set_clipboard_text, tr
)
import ui_components
from sv_parser import parse_sv_file, detect_clk_rst
from sv_generator import generate_module_code, generate_testbench_code, generate_master_tb_code

# Global settings for window
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

def select_open_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Open SystemVerilog/Verilog Module",
        filetypes=[("SystemVerilog Files", "*.sv"), ("Verilog Files", "*.v"), ("All Files", "*.*")]
    )
    root.destroy()
    return file_path

def select_save_file(default_name, is_tb=False):
    root = tk.Tk()
    root.withdraw()
    ext = ".sv"
    title = "Save Testbench File" if is_tb else "Save Module File"
    file_path = filedialog.asksaveasfilename(
        title=title,
        initialfile=default_name,
        defaultextension=ext,
        filetypes=[("SystemVerilog Files", "*.sv"), ("Verilog Files", "*.v"), ("All Files", "*.*")]
    )
    root.destroy()
    return file_path

def main():
    global WINDOW_WIDTH, WINDOW_HEIGHT
    
    # Initialize Pygame
    pygame.init()
    
    # Apply application icon BEFORE set_mode to ensure OS registers it properly
    try:
        icone = pygame.image.load(chemin_icone)
        pygame.display.set_icon(icone)
    except pygame.error:
        print(f"Impossible de charger l'image à l'emplacement : {chemin_icone}")

    pygame.display.set_caption("SystemVerilog Tool - Module & Testbench Designer")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    theme.init_fonts()
    
    # State variables
    module_name = "my_module"
    ports = [
        {"name": "clk", "dir": "IN", "width": "1"},
        {"name": "rst_n", "dir": "IN", "width": "1"},
        {"name": "data_in", "dir": "IN", "width": "8"},
        {"name": "data_out", "dir": "OUT", "width": "8"}
    ]
    
    is_sync_reset = False
    is_active_low_reset = True
    tb_mode = "standalone" # "standalone" or "chained" (With Master)
    code_font_size = 14 # adjustable font size
    
    # Active Panels / Tabs
    right_tab = "diagram" # "diagram", "code", "paste"
    code_subtab = "testbench" # "module", "testbench", "master"
    
    # Draggable Divider State
    sidebar_width = 500
    is_dragging_separator = False
    
    # Preferences Modal State
    show_preferences_modal = False
    ui_font_scale = 1.0
    current_theme_name = "Dark (Default)"
    
    # Toast Manager
    toast = ToastManager()
    
    # UI Elements Initialization (Left Panel Layout)
    from ui_components import InputBox
    module_name_input = InputBox((140, 55, 200, 26), text=module_name, placeholder="module_name")
    
    active_low_cb = Checkbox((20, 90, 200, 26), "Active Low Reset", initial_val=is_active_low_reset)
    sync_reset_cb = Checkbox((230, 90, 200, 26), "Synchronous Reset", initial_val=is_sync_reset)
    
    btn_add_clk = Button((20, 120, 100, 26), "Add Clock", callback=lambda: add_clock_preset())
    btn_add_rst = Button((130, 120, 100, 26), "Add Reset", callback=lambda: add_reset_preset())
    
    # Testbench Mode toggle (Standalone vs. With Master)
    tb_mode_toggle = ToggleButton((20, 185, 180, 26), ["Standalone", "With Master"], initial_index=0)
    
    # Port list headers
    btn_add_input = Button((230, 225, 110, 26), "+ Input", callback=lambda: add_input_port())
    btn_add_output = Button((350, 225, 110, 26), "+ Output", callback=lambda: add_output_port())
    
    # PortRows
    port_rows = []

    pref_card_w = 450
    pref_card_h = 350
    
    # Language toggle
    pref_lang_toggle = ToggleButton((0, 0, 180, 26), ["English", "Français"], initial_index=0)
    
    # Theme toggle
    pref_theme_toggle = ToggleButton((0, 0, 180, 26), ["Dark (Default)", "Light", "Solarized"], initial_index=0)
    
    # UI scale change functions
    def ui_dec():
        nonlocal ui_font_scale
        ui_font_scale = max(0.7, ui_font_scale - 0.1)
        theme.init_fonts(ui_scale=ui_font_scale)
        theme.fonts["code"] = pygame.font.SysFont(theme.mono_name, code_font_size)
        theme.fonts["code_large"] = pygame.font.SysFont(theme.mono_name, code_font_size + 2)
        recalculate_all_layouts()
        msg = f"Taille UI : {int(ui_font_scale * 100)}%" if ui_components.current_language == "fr" else f"UI Size: {int(ui_font_scale * 100)}%"
        toast.show(msg)
        
    def ui_inc():
        nonlocal ui_font_scale
        ui_font_scale = min(2.0, ui_font_scale + 0.1)
        theme.init_fonts(ui_scale=ui_font_scale)
        theme.fonts["code"] = pygame.font.SysFont(theme.mono_name, code_font_size)
        theme.fonts["code_large"] = pygame.font.SysFont(theme.mono_name, code_font_size + 2)
        recalculate_all_layouts()
        msg = f"Taille UI : {int(ui_font_scale * 100)}%" if ui_components.current_language == "fr" else f"UI Size: {int(ui_font_scale * 100)}%"
        toast.show(msg)
        
    btn_pref_ui_dec = Button((0, 0, 30, 26), "-", callback=ui_dec)
    btn_pref_ui_inc = Button((0, 0, 30, 26), "+", callback=ui_inc)
    
    # Editor scale change functions
    def ed_dec():
        nonlocal code_font_size
        code_font_size = max(10, code_font_size - 2)
        theme.fonts["code"] = pygame.font.SysFont(theme.mono_name, code_font_size)
        theme.fonts["code_large"] = pygame.font.SysFont(theme.mono_name, code_font_size + 2)
        code_preview_area.line_h = code_font_size + 4
        paste_area.line_h = code_font_size + 4
        update_code_cache()
        toast.show(f"Editor Font Size: {code_font_size}px")
        
    def ed_inc():
        nonlocal code_font_size
        code_font_size = min(32, code_font_size + 2)
        theme.fonts["code"] = pygame.font.SysFont(theme.mono_name, code_font_size)
        theme.fonts["code_large"] = pygame.font.SysFont(theme.mono_name, code_font_size + 2)
        code_preview_area.line_h = code_font_size + 4
        paste_area.line_h = code_font_size + 4
        update_code_cache()
        toast.show(f"Editor Font Size: {code_font_size}px")
        
    btn_pref_ed_dec = Button((0, 0, 30, 26), "-", callback=ed_dec)
    btn_pref_ed_inc = Button((0, 0, 30, 26), "+", callback=ed_inc)
    
    def close_pref():
        nonlocal show_preferences_modal
        show_preferences_modal = False
        
    btn_pref_close = Button((0, 0, 150, 30), "Close", callback=close_pref, is_accent=True)
    
    def open_pref():
        nonlocal show_preferences_modal
        show_preferences_modal = True
        pref_lang_toggle.index = 0 if ui_components.current_language == "en" else 1
        
    btn_prefs = Button((0, 0, 100, 26), "Preferences", callback=open_pref)
    
    def delete_port(idx):
        if 0 <= idx < len(ports):
            deleted_name = ports[idx]["name"]
            ports.pop(idx)
            rebuild_port_rows()
            toast.show(f"Deleted port '{deleted_name}'")
            
    def rebuild_port_rows():
        nonlocal port_rows
        port_rows = []
        for idx, p in enumerate(ports):
            row = PortRow(idx, p, delete_port)
            port_rows.append(row)
            
    rebuild_port_rows()
    
    # Presets & Add Port Buttons
    def add_clock_preset():
        if any(p["name"] == "clk" for p in ports):
            toast.show("Clock port 'clk' already exists", is_error=True)
            return
        ports.insert(0, {"name": "clk", "dir": "IN", "width": "1"})
        rebuild_port_rows()
        toast.show("Added clock 'clk'")
        
    def add_reset_preset():
        rst_name = "rst_n" if is_active_low_reset else "rst"
        if any(p["name"] == rst_name for p in ports):
            toast.show(f"Reset port '{rst_name}' already exists", is_error=True)
            return
        idx = 1 if (ports and ports[0]["name"] == "clk") else 0
        ports.insert(idx, {"name": rst_name, "dir": "IN", "width": "1"})
        rebuild_port_rows()
        toast.show(f"Added reset '{rst_name}'")

    def add_input_port():
        name = f"in_port_{len(ports)}"
        ports.append({"name": name, "dir": "IN", "width": "1"})
        rebuild_port_rows()
        ports_scroll.scroll_y = max(0, len(ports) * int(36 * ui_font_scale) - ports_scroll.rect.height)
        toast.show(f"Added input '{name}'")
        
    def add_output_port():
        name = f"out_port_{len(ports)}"
        ports.append({"name": name, "dir": "OUT", "width": "1"})
        rebuild_port_rows()
        ports_scroll.scroll_y = max(0, len(ports) * int(36 * ui_font_scale) - ports_scroll.rect.height)
        toast.show(f"Added output '{name}'")

    line1_y = 155
    lbl_tb_title_y = 162
    line2_y = 220
    lbl_ports_y = 228

    # Scroll Areas & Multi-Line TextAreas
    ports_scroll = ScrollArea((20, 260, sidebar_width - 40, WINDOW_HEIGHT - 280))
    
    # Read-only copiable Code Preview Area
    code_preview_area = TextArea((sidebar_width + 20, 110, WINDOW_WIDTH - (sidebar_width + 40), WINDOW_HEIGHT - 130), read_only=True, syntax_highlight=True)
    
    # Writable Paste SV Code Area
    paste_area = TextArea((sidebar_width + 20, 110, WINDOW_WIDTH - (sidebar_width + 40), WINDOW_HEIGHT - 180), placeholder="Paste your SystemVerilog module code here...")
    
    # Visual Diagram Area
    diagram_visualizer = BlockDiagram((sidebar_width + 20, 65, WINDOW_WIDTH - (sidebar_width + 40), WINDOW_HEIGHT - 85))
    
    def get_master_tb_code():
        if module_name.lower() in ["alu", "regfile", "reg_file"]:
            sub_tbs = [
                {"module_name": "alu"},
                {"module_name": "regfile"}
            ]
        else:
            sub_tbs = [
                {"module_name": module_name},
                {"module_name": "other_module"}
            ]
        return generate_master_tb_code(sub_tbs)

    def update_code_cache():
        if code_subtab == "module":
            code_str = generate_module_code(module_name, ports)
        elif code_subtab == "testbench":
            code_str = generate_testbench_code(
                module_name, ports, is_sync_reset, is_active_low_reset, tb_mode
            )
        else: # "master"
            code_str = get_master_tb_code()
            
        code_preview_area.text = code_str

    update_code_cache()
    
    # Right panel Tab selectors
    btn_tab_diagram = Button((sidebar_width + 20, 20, 150, 30), "Block Diagram", callback=lambda: set_right_tab("diagram"))
    btn_tab_code = Button((sidebar_width + 180, 20, 150, 30), "Code Preview", callback=lambda: set_right_tab("code"))
    btn_tab_paste = Button((sidebar_width + 340, 20, 150, 30), "Paste or Import", callback=lambda: set_right_tab("paste"))
    
    def set_right_tab(tab):
        nonlocal right_tab
        right_tab = tab
        update_code_cache()
        
    # Code subtabs
    btn_subtab_mod = Button((520, 65, 120, 26), "Module Code", callback=lambda: set_subtab("module"))
    btn_subtab_tb = Button((650, 65, 120, 26), "Testbench Code", callback=lambda: set_subtab("testbench"))
    btn_subtab_master = Button((780, 65, 120, 26), "Master TB Code", callback=lambda: set_subtab("master"))
    
    def set_subtab(sub):
        nonlocal code_subtab
        code_subtab = sub
        update_code_cache()
        
    # Save active code action
    def handle_save_active():
        if right_tab == "diagram":
            default_fn = f"{module_name}.sv"
            is_tb_save = False
            code_type = "module"
        elif right_tab == "paste":
            default_fn = "pasted_module.sv"
            is_tb_save = False
            code_type = "paste"
        else:
            if code_subtab == "module":
                default_fn = f"{module_name}.sv"
                is_tb_save = False
                code_type = "module"
            elif code_subtab == "testbench":
                default_fn = f"tb_{module_name}.sv"
                is_tb_save = True
                code_type = "testbench"
            else:
                default_fn = "master_tb.sv"
                is_tb_save = True
                code_type = "master"
                
        path = select_save_file(default_fn, is_tb=is_tb_save)
        if path:
            try:
                if code_type == "module":
                    code_str = generate_module_code(module_name, ports)
                elif code_type == "testbench":
                    code_str = generate_testbench_code(
                        module_name, ports, is_sync_reset, is_active_low_reset, tb_mode
                    )
                elif code_type == "paste":
                    code_str = paste_area.text
                else:
                    code_str = get_master_tb_code()
                    
                with open(path, 'w') as f:
                    f.write(code_str)
                toast.show(f"Saved file to {os.path.basename(path)}")
            except Exception as e:
                toast.show(f"Error saving: {e}", is_error=True)
                
    def handle_parse_file():
        path = select_open_file()
        if path:
            try:
                with open(path, 'r') as f:
                    content = f.read()
                paste_area.text = content
                paste_area.cursor_pos = len(content)
                perform_parse(content)
            except Exception as e:
                toast.show(f"{tr('toast_parse_error')}{e}", is_error=True)

    def handle_parse_pasted():
        content = paste_area.text
        if content.strip():
            perform_parse(content)
        else:
            toast.show("Paste area is empty!", is_error=True)

    def perform_parse(content):
        try:
            parsed_name, parsed_ports = parse_sv_file(content)
            if parsed_name:
                nonlocal module_name, ports, is_active_low_reset
                module_name = parsed_name
                module_name_input.text = parsed_name
                module_name_input.cursor_pos = len(parsed_name)
                ports = parsed_ports
                
                clk_p, rst_p = detect_clk_rst(ports)
                if rst_p:
                    is_active_low_reset = rst_p["name"].lower().endswith("n") or rst_p["name"].lower().endswith("b")
                    active_low_cb.checked = is_active_low_reset
                    
                rebuild_port_rows()
                update_code_cache()
                toast.show(f"Parsed module '{parsed_name}' ({len(ports)} ports)")
                set_right_tab("diagram")
            else:
                toast.show("No valid module declaration found", is_error=True)
        except Exception as e:
            toast.show(f"Error parsing code: {e}", is_error=True)

    def handle_copy_code():
        if code_subtab == "module":
            code_str = generate_module_code(module_name, ports)
        elif code_subtab == "testbench":
            code_str = generate_testbench_code(
                module_name, ports, is_sync_reset, is_active_low_reset, tb_mode
            )
        else:
            code_str = get_master_tb_code()
        set_clipboard_text(code_str)
        toast.show("Code copied to clipboard!")

    # Zoom functions
    def zoom_code_in():
        nonlocal code_font_size
        code_font_size = min(32, code_font_size + 2)
        theme.fonts["code"] = pygame.font.SysFont("consolas", code_font_size)
        code_preview_area.line_h = code_font_size + 4
        paste_area.line_h = code_font_size + 4
        update_code_cache()
        toast.show(f"Code Font Size: {code_font_size}px")
        
    def zoom_code_out():
        nonlocal code_font_size
        code_font_size = max(10, code_font_size - 2)
        theme.fonts["code"] = pygame.font.SysFont("consolas", code_font_size)
        code_preview_area.line_h = code_font_size + 4
        paste_area.line_h = code_font_size + 4
        update_code_cache()
        toast.show(f"Code Font Size: {code_font_size}px")

    def zoom_diag_in():
        diagram_visualizer.scale = min(2.0, diagram_visualizer.scale + 0.1)
        toast.show(f"Diagram Zoom: {int(diagram_visualizer.scale * 100)}%")
        
    def zoom_diag_out():
        diagram_visualizer.scale = max(0.5, diagram_visualizer.scale - 0.1)
        toast.show(f"Diagram Zoom: {int(diagram_visualizer.scale * 100)}%")

    # Buttons layout setup
    btn_save = Button((WINDOW_WIDTH - 60, 20, 40, 30), "", callback=handle_save_active, icon="save", no_bg=False)
    btn_copy = Button((WINDOW_WIDTH - 140, 65, 120, 26), "Copy Code", callback=handle_copy_code, bg_color_key="button.background")

    # Zoom Buttons for Diagram & Code Preview
    btn_diag_zoom_in = Button((WINDOW_WIDTH - 100, 80, 30, 30), "+", callback=zoom_diag_in)
    btn_diag_zoom_out = Button((WINDOW_WIDTH - 60, 80, 30, 30), "-", callback=zoom_diag_out)
    
    btn_code_zoom_in = Button((WINDOW_WIDTH - 250, 65, 30, 26), "+", callback=zoom_code_in)
    btn_code_zoom_out = Button((WINDOW_WIDTH - 210, 65, 30, 26), "-", callback=zoom_code_out)

    # Parse and Import buttons inside Paste or Import Tab
    btn_import_file = Button((WINDOW_WIDTH - 430, WINDOW_HEIGHT - 60, 200, 30), "Import SV File", callback=handle_parse_file, bg_color_key="list.activeSelectionBackground")
    btn_parse_pasted = Button((WINDOW_WIDTH - 220, WINDOW_HEIGHT - 60, 200, 30), "Parse Pasted Code", callback=handle_parse_pasted, is_accent=True)

    def update_sidebar_rects():
        scale = ui_font_scale
        pad = int(20 * scale)
        h_widget = int(26 * scale)
        
        # Title
        title_y = int(20 * scale)
        lbl_title_h = theme.fonts["header"].get_linesize()
        
        # Preferences button
        btn_prefs.rect.width = int(100 * scale)
        btn_prefs.rect.height = h_widget
        btn_prefs.rect.x = sidebar_width - btn_prefs.rect.width - pad
        btn_prefs.rect.y = title_y
        
        # Module Name Row
        mod_name_y = title_y + lbl_title_h + int(15 * scale)
        lbl_mod_w = theme.fonts["body"].size(tr("module_name"))[0]
        module_name_input.rect.x = pad + lbl_mod_w + int(10 * scale)
        module_name_input.rect.y = mod_name_y + (theme.fonts["body"].get_height() - h_widget) // 2
        module_name_input.rect.width = sidebar_width - module_name_input.rect.x - pad
        module_name_input.rect.height = h_widget
        
        # Checkboxes Row
        cb_y = max(module_name_input.rect.bottom, mod_name_y + theme.fonts["body"].get_height()) + int(12 * scale)
        cb_w = (sidebar_width - pad * 2 - int(10 * scale)) // 2
        active_low_cb.rect = pygame.Rect(pad, cb_y, cb_w, h_widget)
        sync_reset_cb.rect = pygame.Rect(pad + cb_w + int(10 * scale), cb_y, cb_w, h_widget)
        
        # Add Clock / Add Reset Buttons
        btn_y = cb_y + h_widget + int(12 * scale)
        btn_w = (sidebar_width - pad * 2 - int(10 * scale)) // 2
        btn_add_clk.rect = pygame.Rect(pad, btn_y, btn_w, h_widget)
        btn_add_rst.rect = pygame.Rect(pad + btn_w + int(10 * scale), btn_y, btn_w, h_widget)
        
        # Testbench Settings header Y
        nonlocal line1_y, lbl_tb_title_y, line2_y, lbl_ports_y
        line1_y = btn_y + h_widget + int(15 * scale)
        lbl_tb_title_y = line1_y + int(8 * scale)
        lbl_tb_title_h = theme.fonts["body_bold"].get_height()
        
        # TB Mode Toggle
        toggle_y = lbl_tb_title_y + lbl_tb_title_h + int(10 * scale)
        tb_mode_toggle.rect = pygame.Rect(pad, toggle_y, sidebar_width - pad * 2, h_widget)
        
        # Module Ports Header
        line2_y = toggle_y + h_widget + int(15 * scale)
        lbl_ports_y = line2_y + int(8 * scale)
        lbl_ports_h = theme.fonts["body_bold"].get_height()
        
        # Add Input / Add Output buttons
        btn_pw = int(110 * scale)
        btn_add_output.rect.width = btn_pw
        btn_add_output.rect.height = h_widget
        btn_add_output.rect.x = sidebar_width - pad - btn_pw
        btn_add_output.rect.y = lbl_ports_y + (lbl_ports_h - h_widget) // 2
        
        btn_add_input.rect.width = btn_pw
        btn_add_input.rect.height = h_widget
        btn_add_input.rect.x = btn_add_output.rect.x - int(10 * scale) - btn_pw
        btn_add_input.rect.y = btn_add_output.rect.y
        
        # Ports Scroll Area
        scroll_y_start = max(lbl_ports_y + lbl_ports_h, btn_add_input.rect.bottom) + int(10 * scale)
        ports_scroll.rect.x = pad
        ports_scroll.rect.y = scroll_y_start
        ports_scroll.rect.width = sidebar_width - pad * 2
        ports_scroll.rect.height = WINDOW_HEIGHT - scroll_y_start - int(20 * scale)
        
        row_total_h = h_widget + int(10 * scale)
        ports_scroll.virtual_height = len(ports) * row_total_h

    def update_right_panel_rects():
        scale = ui_font_scale
        right_margin = int(20 * scale)
        gap = int(10 * scale)
        
        # Tabs
        tab_w = int(150 * scale)
        tab_h = int(30 * scale)
        
        btn_tab_diagram.rect.width = tab_w
        btn_tab_diagram.rect.height = tab_h
        btn_tab_diagram.rect.x = sidebar_width + int(20 * scale)
        btn_tab_diagram.rect.y = int(20 * scale)
        
        btn_tab_code.rect.width = tab_w
        btn_tab_code.rect.height = tab_h
        btn_tab_code.rect.x = btn_tab_diagram.rect.right + gap
        btn_tab_code.rect.y = btn_tab_diagram.rect.y
        
        btn_tab_paste.rect.width = tab_w
        btn_tab_paste.rect.height = tab_h
        btn_tab_paste.rect.x = btn_tab_code.rect.right + gap
        btn_tab_paste.rect.y = btn_tab_diagram.rect.y
        
        # Save button
        save_w = int(40 * scale)
        save_h = int(30 * scale)
        btn_save.rect.width = save_w
        btn_save.rect.height = save_h
        btn_save.rect.x = WINDOW_WIDTH - save_w - right_margin
        btn_save.rect.y = btn_tab_diagram.rect.y
        
        # Subtabs for Code Tab
        sub_w = int(120 * scale)
        sub_h = int(26 * scale)
        subtab_y = btn_tab_diagram.rect.bottom + int(15 * scale)
        
        btn_subtab_mod.rect.width = sub_w
        btn_subtab_mod.rect.height = sub_h
        btn_subtab_mod.rect.x = sidebar_width + int(20 * scale)
        btn_subtab_mod.rect.y = subtab_y
        
        btn_subtab_tb.rect.width = sub_w
        btn_subtab_tb.rect.height = sub_h
        btn_subtab_tb.rect.x = btn_subtab_mod.rect.right + gap
        btn_subtab_tb.rect.y = subtab_y
        
        btn_subtab_master.rect.width = sub_w
        btn_subtab_master.rect.height = sub_h
        btn_subtab_master.rect.x = btn_subtab_tb.rect.right + gap
        btn_subtab_master.rect.y = subtab_y
        
        # Code Zoom & Copy Buttons
        w_zoom = int(30 * scale)
        btn_copy.rect.width = int(120 * scale)
        btn_copy.rect.height = sub_h
        btn_copy.rect.x = WINDOW_WIDTH - right_margin - btn_copy.rect.width
        btn_copy.rect.y = subtab_y
        
        btn_code_zoom_out.rect.width = w_zoom
        btn_code_zoom_out.rect.height = sub_h
        btn_code_zoom_out.rect.x = btn_copy.rect.x - gap - w_zoom
        btn_code_zoom_out.rect.y = subtab_y
        
        btn_code_zoom_in.rect.width = w_zoom
        btn_code_zoom_in.rect.height = sub_h
        btn_code_zoom_in.rect.x = btn_code_zoom_out.rect.x - gap - w_zoom
        btn_code_zoom_in.rect.y = subtab_y
        
        # Areas and diagram
        # Diagram Rect
        diagram_visualizer.rect.x = sidebar_width + int(20 * scale)
        diagram_visualizer.rect.y = btn_tab_diagram.rect.bottom + int(15 * scale)
        diagram_visualizer.rect.width = WINDOW_WIDTH - diagram_visualizer.rect.x - right_margin
        diagram_visualizer.rect.height = WINDOW_HEIGHT - diagram_visualizer.rect.y - right_margin
        
        # Diagram Zoom buttons
        w_diag_zoom = int(30 * scale)
        h_diag_zoom = int(30 * scale)
        btn_diag_zoom_out.rect.width = w_diag_zoom
        btn_diag_zoom_out.rect.height = h_diag_zoom
        btn_diag_zoom_out.rect.x = WINDOW_WIDTH - right_margin - w_diag_zoom - int(10 * scale)
        btn_diag_zoom_out.rect.y = diagram_visualizer.rect.y + int(15 * scale)
        
        btn_diag_zoom_in.rect.width = w_diag_zoom
        btn_diag_zoom_in.rect.height = h_diag_zoom
        btn_diag_zoom_in.rect.x = btn_diag_zoom_out.rect.x - w_diag_zoom - int(8 * scale)
        btn_diag_zoom_in.rect.y = btn_diag_zoom_out.rect.y
        
        # Code Preview Area
        code_preview_area.rect.x = sidebar_width + int(20 * scale)
        code_preview_area.rect.y = subtab_y + sub_h + int(10 * scale)
        code_preview_area.rect.width = WINDOW_WIDTH - code_preview_area.rect.x - right_margin
        code_preview_area.rect.height = WINDOW_HEIGHT - code_preview_area.rect.y - right_margin
        
        # Paste Tab Buttons & Area
        btn_w = int(200 * scale)
        btn_h = int(30 * scale)
        
        btn_parse_pasted.rect.width = btn_w
        btn_parse_pasted.rect.height = btn_h
        btn_parse_pasted.rect.x = WINDOW_WIDTH - right_margin - btn_w
        btn_parse_pasted.rect.y = WINDOW_HEIGHT - btn_h - int(20 * scale)
        
        btn_import_file.rect.width = btn_w
        btn_import_file.rect.height = btn_h
        btn_import_file.rect.x = btn_parse_pasted.rect.x - btn_w - int(15 * scale)
        btn_import_file.rect.y = btn_parse_pasted.rect.y
        
        paste_area.rect.x = sidebar_width + int(20 * scale)
        paste_area.rect.y = btn_tab_diagram.rect.bottom + int(15 * scale)
        paste_area.rect.width = WINDOW_WIDTH - paste_area.rect.x - right_margin
        paste_area.rect.height = btn_parse_pasted.rect.y - paste_area.rect.y - int(15 * scale)

    def update_pref_modal_rects():
        nonlocal pref_card_w, pref_card_h
        scale = ui_font_scale
        pref_card_w = int(450 * scale)
        pref_card_h = int(350 * scale)
        card_x = (WINDOW_WIDTH - pref_card_w) // 2
        card_y = (WINDOW_HEIGHT - pref_card_h) // 2
        h_widget = int(26 * scale)
        
        pref_lang_toggle.rect.topleft = (card_x + int(220 * scale), card_y + int(75 * scale))
        pref_lang_toggle.rect.width = int(180 * scale)
        pref_lang_toggle.rect.height = h_widget
        
        btn_pref_ui_dec.rect.topleft = (card_x + int(220 * scale), card_y + int(125 * scale))
        btn_pref_ui_dec.rect.width = int(30 * scale)
        btn_pref_ui_dec.rect.height = h_widget
        
        btn_pref_ui_inc.rect.topleft = (card_x + int(350 * scale), card_y + int(125 * scale))
        btn_pref_ui_inc.rect.width = int(30 * scale)
        btn_pref_ui_inc.rect.height = h_widget
        
        btn_pref_ed_dec.rect.topleft = (card_x + int(220 * scale), card_y + int(175 * scale))
        btn_pref_ed_dec.rect.width = int(30 * scale)
        btn_pref_ed_dec.rect.height = h_widget
        
        btn_pref_ed_inc.rect.topleft = (card_x + int(350 * scale), card_y + int(175 * scale))
        btn_pref_ed_inc.rect.width = int(30 * scale)
        btn_pref_ed_inc.rect.height = h_widget
        
        pref_theme_toggle.rect.topleft = (card_x + int(220 * scale), card_y + int(225 * scale))
        pref_theme_toggle.rect.width = int(180 * scale)
        pref_theme_toggle.rect.height = h_widget
        
        btn_pref_close.rect.width = int(150 * scale)
        btn_pref_close.rect.height = int(30 * scale)
        btn_pref_close.rect.topleft = (card_x + (pref_card_w - btn_pref_close.rect.width) // 2, card_y + int(290 * scale))

    def recalculate_all_layouts():
        update_sidebar_rects()
        update_right_panel_rects()
        update_pref_modal_rects()

    def update_tab_highlights():
        btn_tab_diagram.is_accent = (right_tab == "diagram")
        btn_tab_code.is_accent = (right_tab == "code")
        btn_tab_paste.is_accent = (right_tab == "paste")
        btn_subtab_mod.is_accent = (code_subtab == "module")
        btn_subtab_tb.is_accent = (code_subtab == "testbench")
        btn_subtab_master.is_accent = (code_subtab == "master")

    # Main Loop
    recalculate_all_layouts()
    while True:
        # State update checks
        if module_name != module_name_input.text:
            module_name = module_name_input.text
            update_code_cache()

        if is_sync_reset != sync_reset_cb.checked:
            is_sync_reset = sync_reset_cb.checked
            update_code_cache()
        if is_active_low_reset != active_low_cb.checked:
            is_active_low_reset = active_low_cb.checked
            update_code_cache()
            
        curr_mode = "standalone" if tb_mode_toggle.index == 0 else "chained"
        if tb_mode != curr_mode:
            tb_mode = curr_mode
            # Disable Master TB subtab in Standalone mode
            if tb_mode == "standalone" and code_subtab == "master":
                code_subtab = "testbench"
            update_code_cache()
            
        update_tab_highlights()

        # Cursor and separator drag handling
        mouse_pos = pygame.mouse.get_pos()
        on_separator = abs(mouse_pos[0] - sidebar_width) < 5
        if is_dragging_separator or on_separator:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEWE)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        # Update language and theme from toggle in preferences
        sel_lang = "en" if pref_lang_toggle.index == 0 else "fr"
        if ui_components.current_language != sel_lang:
            ui_components.current_language = sel_lang
            
        theme_names = ["Dark (Default)", "Light", "Solarized"]
        sel_theme = theme_names[pref_theme_toggle.index]
        if current_theme_name != sel_theme:
            current_theme_name = sel_theme
            theme.apply_preset(sel_theme)

        # Update responsive UI layouts
        recalculate_all_layouts()

        # Event handling
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.VIDEORESIZE:
                WINDOW_WIDTH = event.w
                WINDOW_HEIGHT = event.h
                screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)

            # Divider dragging event handling
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if on_separator and not show_preferences_modal:
                    is_dragging_separator = True
                    module_name_input.focused = False
                    for r in port_rows:
                        r.name_input.focused = False
                        r.width_input.focused = False
                    continue
                    
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                is_dragging_separator = False
                
            elif event.type == pygame.MOUSEMOTION:
                if is_dragging_separator:
                    sidebar_width = max(350, min(WINDOW_WIDTH - 400, event.pos[0]))
                    continue

            # Preferences Modal Event Interception
            if show_preferences_modal:
                pref_lang_toggle.handle_event(event)
                pref_theme_toggle.handle_event(event)
                btn_pref_ui_dec.handle_event(event)
                btn_pref_ui_inc.handle_event(event)
                btn_pref_ed_dec.handle_event(event)
                btn_pref_ed_inc.handle_event(event)
                btn_pref_close.handle_event(event)
                continue

            # Global keys
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    focusable = [module_name_input]
                    for r in port_rows:
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
                        
                        start_ports_idx = 1
                        if next_idx >= start_ports_idx:
                            row_idx = (next_idx - start_ports_idx) // 2
                            row_total_h = int(36 * ui_font_scale)
                            target_vy = row_idx * row_total_h
                            viewport_h = ports_scroll.rect.height
                            if target_vy < ports_scroll.scroll_y:
                                ports_scroll.scroll_y = target_vy
                            elif target_vy + row_total_h > ports_scroll.scroll_y + viewport_h:
                                ports_scroll.scroll_y = target_vy + row_total_h - viewport_h

            # Left panel inputs
            module_name_input.handle_event(event)
            active_low_cb.handle_event(event)
            sync_reset_cb.handle_event(event)
            
            btn_add_clk.handle_event(event)
            btn_add_rst.handle_event(event)
            tb_mode_toggle.handle_event(event)
            
            btn_add_input.handle_event(event)
            btn_add_output.handle_event(event)
            btn_prefs.handle_event(event)
            
            # Right panel tabs
            btn_tab_diagram.handle_event(event)
            btn_tab_code.handle_event(event)
            btn_tab_paste.handle_event(event)
            btn_save.handle_event(event)
            
            if right_tab == "diagram":
                btn_diag_zoom_in.handle_event(event)
                btn_diag_zoom_out.handle_event(event)
            
            elif right_tab == "code":
                btn_subtab_mod.handle_event(event)
                btn_subtab_tb.handle_event(event)
                if tb_mode == "chained": # Only handle Master TB tab if With Master mode
                    btn_subtab_master.handle_event(event)
                btn_copy.handle_event(event)
                btn_code_zoom_in.handle_event(event)
                btn_code_zoom_out.handle_event(event)
                code_preview_area.handle_event(event)
            
            elif right_tab == "paste":
                paste_area.handle_event(event)
                btn_parse_pasted.handle_event(event)
                btn_import_file.handle_event(event)

            # Ports scroll area handling
            ports_scroll.handle_event(event)
            
            mouse_pos = pygame.mouse.get_pos()
            in_scroll_viewport = ports_scroll.rect.collidepoint(mouse_pos)
            offset_pos = (mouse_pos[0], mouse_pos[1] + ports_scroll.scroll_y) if in_scroll_viewport else (-1, -1)
            
            row_start_y = ports_scroll.rect.y
            row_total_h = int(36 * ui_font_scale)
            pad_ports = int(20 * ui_font_scale)
            h_widget = int(26 * ui_font_scale)
            for idx, row in enumerate(port_rows):
                row.set_positions(pad_ports, row_start_y + idx * row_total_h, sidebar_width - pad_ports * 2, h_widget)
                row.handle_event(event, offset_pos)

        # Update
        if show_preferences_modal:
            pref_lang_toggle.update()
            pref_theme_toggle.update()
            btn_pref_ui_dec.update()
            btn_pref_ui_inc.update()
            btn_pref_ed_dec.update()
            btn_pref_ed_inc.update()
            btn_pref_close.update()
        else:
            module_name_input.update()
            sync_reset_cb.update()
            active_low_cb.update()
            
            btn_add_clk.update()
            btn_add_rst.update()
            tb_mode_toggle.update()
            
            btn_add_input.update()
            btn_add_output.update()
            btn_prefs.update()
            btn_save.update()
            
            btn_tab_diagram.update()
            btn_tab_code.update()
            btn_tab_paste.update()
            
            if right_tab == "diagram":
                btn_diag_zoom_in.update()
                btn_diag_zoom_out.update()
                
            elif right_tab == "code":
                btn_subtab_mod.update()
                btn_subtab_tb.update()
                if tb_mode == "chained":
                    btn_subtab_master.update()
                btn_copy.update()
                btn_code_zoom_in.update()
                btn_code_zoom_out.update()
                code_preview_area.update()
                
            elif right_tab == "paste":
                paste_area.update()
                btn_parse_pasted.update()
                btn_import_file.update()
                
            for r in port_rows:
                r.update()
            
        ports_scroll.virtual_height = len(ports) * 36
        
        # Always update code cache if right tab is "code" to avoid desync
        if right_tab == "code" and not show_preferences_modal:
            update_code_cache()

        # Rendering
        screen.fill(theme.colors["editor.background"])
                # 1. DRAW LEFT PANEL (SideBar)
        sidebar_rect = pygame.Rect(0, 0, sidebar_width, WINDOW_HEIGHT)
        pygame.draw.rect(screen, theme.colors["sideBar.background"], sidebar_rect)
        pygame.draw.line(screen, theme.colors["sideBar.border"], (sidebar_width, 0), (sidebar_width, WINDOW_HEIGHT), 2)
        
        pad = int(20 * ui_font_scale)
        lbl_title = theme.fonts["header"].render(tr("title"), True, theme.colors["editor.foreground"])
        screen.blit(lbl_title, (pad, int(20 * ui_font_scale)))
        btn_prefs.draw(screen)
        
        lbl_mod = theme.fonts["body"].render(tr("module_name"), True, theme.colors["editor.foreground"])
        lbl_mod_y = module_name_input.rect.y + (module_name_input.rect.height - lbl_mod.get_height()) // 2
        screen.blit(lbl_mod, (pad, lbl_mod_y))
        
        module_name_input.draw(screen)
        active_low_cb.draw(screen)
        sync_reset_cb.draw(screen)
        btn_add_clk.draw(screen)
        btn_add_rst.draw(screen)
        
        pygame.draw.line(screen, theme.colors["sideBar.border"], (pad, line1_y), (sidebar_width - pad, line1_y), 1)
        
        lbl_tb_title = theme.fonts["body_bold"].render(tr("tb_settings"), True, theme.colors["editor.foreground"])
        screen.blit(lbl_tb_title, (pad, lbl_tb_title_y))
        
        tb_mode_toggle.draw(screen)
        
        pygame.draw.line(screen, theme.colors["sideBar.border"], (pad, line2_y), (sidebar_width - pad, line2_y), 1)
        
        lbl_ports = theme.fonts["body_bold"].render(tr("module_ports"), True, theme.colors["editor.foreground"])
        screen.blit(lbl_ports, (pad, lbl_ports_y))
        
        btn_add_input.draw(screen)
        btn_add_output.draw(screen)
        
        def draw_ports_list(surface, scroll_y):
            row_start_y = ports_scroll.rect.y
            row_total_h = int(36 * ui_font_scale)
            pad_ports = int(20 * ui_font_scale)
            h_widget = int(26 * ui_font_scale)
            for idx, r in enumerate(port_rows):
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
                
        ports_scroll.draw(screen, draw_ports_list)
        
        # 2. DRAW RIGHT PANEL (Viewer)
        btn_tab_diagram.draw(screen)
        btn_tab_code.draw(screen)
        btn_tab_paste.draw(screen)
        btn_save.draw(screen)
        
        if right_tab == "diagram":
            diagram_visualizer.draw(screen, module_name, ports)
            btn_diag_zoom_in.draw(screen)
            btn_diag_zoom_out.draw(screen)
            
        elif right_tab == "code":
            scale = ui_font_scale
            pad = int(20 * scale)
            bg_y = btn_tab_diagram.rect.bottom + int(10 * scale)
            bg_h = WINDOW_HEIGHT - bg_y - int(20 * scale)
            code_bg_rect = pygame.Rect(sidebar_width + pad, bg_y, WINDOW_WIDTH - sidebar_width - pad * 2, bg_h)
            pygame.draw.rect(screen, theme.colors["sideBar.background"], code_bg_rect, border_radius=12)
            pygame.draw.rect(screen, theme.colors["sideBar.border"], code_bg_rect, width=2, border_radius=12)
            
            btn_subtab_mod.draw(screen)
            btn_subtab_tb.draw(screen)
            if tb_mode == "chained":
                btn_subtab_master.draw(screen)
            btn_copy.draw(screen)
            btn_code_zoom_in.draw(screen)
            btn_code_zoom_out.draw(screen)
            
            subtab_bottom = btn_subtab_mod.rect.bottom + int(5 * scale)
            pygame.draw.line(screen, theme.colors["sideBar.border"], (sidebar_width + pad, subtab_bottom), (WINDOW_WIDTH - pad, subtab_bottom), 1)
            code_preview_area.draw(screen)
            
        elif right_tab == "paste":
            paste_area.draw(screen)
            btn_parse_pasted.draw(screen)
            btn_import_file.draw(screen)

        # 3. DRAW PREFERENCES MODAL
        if show_preferences_modal:
            # Semi-transparent overlay backdrop
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            # Position the modal card in the center
            card_x = (WINDOW_WIDTH - pref_card_w) // 2
            card_y = (WINDOW_HEIGHT - pref_card_h) // 2
            
            card_rect = pygame.Rect(card_x, card_y, pref_card_w, pref_card_h)
            pygame.draw.rect(screen, theme.colors["sideBar.background"], card_rect, border_radius=12)
            pygame.draw.rect(screen, theme.colors["sideBar.border"], card_rect, width=2, border_radius=12)
            
            # Header Title
            lbl_pref_title = theme.fonts["header"].render(tr("pref_title"), True, theme.colors["editor.foreground"])
            screen.blit(lbl_pref_title, (card_x + (pref_card_w - lbl_pref_title.get_width()) // 2, card_y + int(20 * ui_font_scale)))
            
            # Row 1: Language
            lbl_lang = theme.fonts["body_bold"].render(tr("pref_lang"), True, theme.colors["editor.foreground"])
            screen.blit(lbl_lang, (card_x + int(30 * ui_font_scale), card_y + int(80 * ui_font_scale)))
            pref_lang_toggle.draw(screen)
            
            # Row 2: UI Scale
            lbl_ui = theme.fonts["body_bold"].render(tr("pref_ui_scale"), True, theme.colors["editor.foreground"])
            screen.blit(lbl_ui, (card_x + int(30 * ui_font_scale), card_y + int(130 * ui_font_scale)))
            btn_pref_ui_dec.draw(screen)
            btn_pref_ui_inc.draw(screen)
            
            lbl_ui_val = theme.fonts["body"].render(f"{int(ui_font_scale * 100)}%", True, theme.colors["editor.foreground"])
            lbl_ui_val_x = btn_pref_ui_dec.rect.right + (btn_pref_ui_inc.rect.left - btn_pref_ui_dec.rect.right - lbl_ui_val.get_width()) // 2
            lbl_ui_val_y = btn_pref_ui_dec.rect.y + (btn_pref_ui_dec.rect.height - lbl_ui_val.get_height()) // 2
            screen.blit(lbl_ui_val, (lbl_ui_val_x, lbl_ui_val_y))
            
            # Row 3: Editor Size
            lbl_ed = theme.fonts["body_bold"].render(tr("pref_editor_size"), True, theme.colors["editor.foreground"])
            screen.blit(lbl_ed, (card_x + int(30 * ui_font_scale), card_y + int(180 * ui_font_scale)))
            btn_pref_ed_dec.draw(screen)
            btn_pref_ed_inc.draw(screen)
            
            lbl_ed_val = theme.fonts["body"].render(f"{code_font_size}px", True, theme.colors["editor.foreground"])
            lbl_ed_val_x = btn_pref_ed_dec.rect.right + (btn_pref_ed_inc.rect.left - btn_pref_ed_dec.rect.right - lbl_ed_val.get_width()) // 2
            lbl_ed_val_y = btn_pref_ed_dec.rect.y + (btn_pref_ed_dec.rect.height - lbl_ed_val.get_height()) // 2
            screen.blit(lbl_ed_val, (lbl_ed_val_x, lbl_ed_val_y))
            
            # Row 4: Theme
            lbl_th = theme.fonts["body_bold"].render(tr("pref_theme"), True, theme.colors["editor.foreground"])
            screen.blit(lbl_th, (card_x + int(30 * ui_font_scale), card_y + int(230 * ui_font_scale)))
            pref_theme_toggle.draw(screen)
            
            # Bottom Close Button
            btn_pref_close.draw(screen)

        # Draw Toast notifications
        toast.draw(screen, WINDOW_WIDTH, WINDOW_HEIGHT)

        # Update Display
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
