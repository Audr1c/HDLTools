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

# Asset Paths Setup
DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
DOSSIER_IMAGES = os.path.join(DOSSIER_COURANT, "assets", "images")

# Ensure assets directory and default icon exist before loading
os.makedirs(DOSSIER_IMAGES, exist_ok=True)
chemin_icone = os.path.join(DOSSIER_IMAGES, "icone.png")
if not os.path.exists(chemin_icone):
    pygame.init()
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.rect(surf, (0, 229, 255), (6, 6, 20, 20), border_radius=4)
    for i in range(4):
        py = 9 + i * 5
        pygame.draw.line(surf, (0, 229, 255), (2, py), (5, py), 1)
        pygame.draw.line(surf, (0, 229, 255), (26, py), (29, py), 1)
    pygame.image.save(surf, chemin_icone)

# Ensure diskette.png exists
chemin_disquette = os.path.join(DOSSIER_IMAGES, "diskette.png")
if not os.path.exists(chemin_disquette):
    pygame.init()
    temp_d = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.rect(temp_d, (201, 209, 217), (4, 4, 24, 24), border_radius=2)
    pygame.draw.rect(temp_d, (20, 24, 33), (8, 6, 16, 6))
    pygame.draw.rect(temp_d, (20, 24, 33), (10, 18, 12, 10))
    pygame.image.save(temp_d, chemin_disquette)

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
        toast.show(f"UI Font Scale: {int(ui_font_scale * 100)}%")
        
    def ui_inc():
        nonlocal ui_font_scale
        ui_font_scale = min(2.0, ui_font_scale + 0.1)
        theme.init_fonts(ui_scale=ui_font_scale)
        theme.fonts["code"] = pygame.font.SysFont(theme.mono_name, code_font_size)
        theme.fonts["code_large"] = pygame.font.SysFont(theme.mono_name, code_font_size + 2)
        toast.show(f"UI Font Scale: {int(ui_font_scale * 100)}%")
        
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
        ports_scroll.scroll_y = max(0, len(ports) * 36 - ports_scroll.rect.height)
        toast.show(f"Added input '{name}'")
        
    def add_output_port():
        name = f"out_port_{len(ports)}"
        ports.append({"name": name, "dir": "OUT", "width": "1"})
        rebuild_port_rows()
        ports_scroll.scroll_y = max(0, len(ports) * 36 - ports_scroll.rect.height)
        toast.show(f"Added output '{name}'")

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

    def update_tab_highlights():
        btn_tab_diagram.is_accent = (right_tab == "diagram")
        btn_tab_code.is_accent = (right_tab == "code")
        btn_tab_paste.is_accent = (right_tab == "paste")
        btn_subtab_mod.is_accent = (code_subtab == "module")
        btn_subtab_tb.is_accent = (code_subtab == "testbench")
        btn_subtab_master.is_accent = (code_subtab == "master")

    # Main Loop
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
        ports_scroll.rect.width = sidebar_width - 40
        ports_scroll.rect.height = WINDOW_HEIGHT - 280 # Extended to bottom!
        
        # Recalculate Right Panel Widgets
        w_right = WINDOW_WIDTH - (sidebar_width + 40)
        code_scroll_h = WINDOW_HEIGHT - 130
        
        code_preview_area.rect.x = sidebar_width + 20
        code_preview_area.rect.width = w_right
        code_preview_area.rect.height = code_scroll_h
        
        paste_area.rect.x = sidebar_width + 20
        paste_area.rect.width = w_right
        paste_area.rect.height = WINDOW_HEIGHT - 180
        
        diagram_visualizer.rect.x = sidebar_width + 20
        diagram_visualizer.rect.width = w_right
        diagram_visualizer.rect.height = WINDOW_HEIGHT - 85
        
        # Button placement offsets
        btn_tab_diagram.rect.x = sidebar_width + 20
        btn_tab_code.rect.x = sidebar_width + 180
        btn_tab_paste.rect.x = sidebar_width + 340
        
        btn_subtab_mod.rect.x = sidebar_width + 20
        btn_subtab_tb.rect.x = sidebar_width + 150
        btn_subtab_master.rect.x = sidebar_width + 280
        
        btn_save.rect.x = WINDOW_WIDTH - 60
        btn_prefs.rect.x = sidebar_width - 120
        
        btn_copy.rect.x = WINDOW_WIDTH - 140
        btn_code_zoom_in.rect.x = WINDOW_WIDTH - 250
        btn_code_zoom_out.rect.x = WINDOW_WIDTH - 210
        
        btn_diag_zoom_in.rect.x = WINDOW_WIDTH - 100
        btn_diag_zoom_out.rect.x = WINDOW_WIDTH - 60
        
        btn_import_file.rect.x = WINDOW_WIDTH - 430
        btn_import_file.rect.y = WINDOW_HEIGHT - 60
        btn_parse_pasted.rect.x = WINDOW_WIDTH - 220
        btn_parse_pasted.rect.y = WINDOW_HEIGHT - 60

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
                            target_vy = row_idx * 36
                            viewport_h = ports_scroll.rect.height
                            if target_vy < ports_scroll.scroll_y:
                                ports_scroll.scroll_y = target_vy
                            elif target_vy + 36 > ports_scroll.scroll_y + viewport_h:
                                ports_scroll.scroll_y = target_vy + 36 - viewport_h

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
            
            for idx, row in enumerate(port_rows):
                row.set_positions(20, 260 + idx * 36, sidebar_width - 40)
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
        
        lbl_title = theme.fonts["header"].render(tr("title"), True, theme.colors["editor.foreground"])
        screen.blit(lbl_title, (20, 20))
        btn_prefs.draw(screen)
        
        lbl_mod = theme.fonts["body"].render(tr("module_name"), True, theme.colors["editor.foreground"])
        screen.blit(lbl_mod, (20, 60))
        
        # Scale input box dynamically
        module_name_input.rect.width = sidebar_width - 160
        module_name_input.draw(screen)
        
        active_low_cb.draw(screen)
        sync_reset_cb.draw(screen)
        
        btn_add_clk.draw(screen)
        btn_add_rst.draw(screen)
        
        pygame.draw.line(screen, theme.colors["sideBar.border"], (20, 155), (sidebar_width - 20, 155), 1)
        
        lbl_tb_title = theme.fonts["body_bold"].render(tr("tb_settings"), True, theme.colors["editor.foreground"])
        screen.blit(lbl_tb_title, (20, 162))
        
        # Scale toggle button to fill space
        tb_mode_toggle.rect.width = sidebar_width - 40
        tb_mode_toggle.draw(screen)
        
        pygame.draw.line(screen, theme.colors["sideBar.border"], (20, 220), (sidebar_width - 20, 220), 1)
        
        lbl_ports = theme.fonts["body_bold"].render(tr("module_ports"), True, theme.colors["editor.foreground"])
        screen.blit(lbl_ports, (20, 228))
        
        btn_add_output.rect.x = sidebar_width - 130
        btn_add_input.rect.x = sidebar_width - 250
        btn_add_input.draw(screen)
        btn_add_output.draw(screen)
        
        def draw_ports_list(surface, scroll_y):
            for idx, r in enumerate(port_rows):
                ry = 260 + idx * 36
                r.set_positions(20, ry, sidebar_width - 40)
                
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
            code_bg_rect = pygame.Rect(sidebar_width + 20, 65, w_right, WINDOW_HEIGHT - 85)
            pygame.draw.rect(screen, theme.colors["sideBar.background"], code_bg_rect, border_radius=12)
            pygame.draw.rect(screen, theme.colors["sideBar.border"], code_bg_rect, width=2, border_radius=12)
            
            btn_subtab_mod.draw(screen)
            btn_subtab_tb.draw(screen)
            if tb_mode == "chained":
                btn_subtab_master.draw(screen)
            btn_copy.draw(screen)
            btn_code_zoom_in.draw(screen)
            btn_code_zoom_out.draw(screen)
            
            pygame.draw.line(screen, theme.colors["sideBar.border"], (sidebar_width + 20, 100), (WINDOW_WIDTH - 20, 100), 1)
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
            screen.blit(lbl_pref_title, (card_x + (pref_card_w - lbl_pref_title.get_width()) // 2, card_y + 20))
            
            # Row 1: Language
            lbl_lang = theme.fonts["body_bold"].render(tr("pref_lang"), True, theme.colors["editor.foreground"])
            screen.blit(lbl_lang, (card_x + 30, card_y + 80))
            pref_lang_toggle.rect.topleft = (card_x + 220, card_y + 75)
            pref_lang_toggle.draw(screen)
            
            # Row 2: UI Scale
            lbl_ui = theme.fonts["body_bold"].render(tr("pref_ui_scale"), True, theme.colors["editor.foreground"])
            screen.blit(lbl_ui, (card_x + 30, card_y + 130))
            
            btn_pref_ui_dec.rect.topleft = (card_x + 220, card_y + 125)
            btn_pref_ui_inc.rect.topleft = (card_x + 350, card_y + 125)
            btn_pref_ui_dec.draw(screen)
            btn_pref_ui_inc.draw(screen)
            
            lbl_ui_val = theme.fonts["body"].render(f"{int(ui_font_scale * 100)}%", True, theme.colors["editor.foreground"])
            screen.blit(lbl_ui_val, (card_x + 270 + (60 - lbl_ui_val.get_width()) // 2, card_y + 128))
            
            # Row 3: Editor Size
            lbl_ed = theme.fonts["body_bold"].render(tr("pref_editor_size"), True, theme.colors["editor.foreground"])
            screen.blit(lbl_ed, (card_x + 30, card_y + 180))
            
            btn_pref_ed_dec.rect.topleft = (card_x + 220, card_y + 175)
            btn_pref_ed_inc.rect.topleft = (card_x + 350, card_y + 175)
            btn_pref_ed_dec.draw(screen)
            btn_pref_ed_inc.draw(screen)
            
            lbl_ed_val = theme.fonts["body"].render(f"{code_font_size}px", True, theme.colors["editor.foreground"])
            screen.blit(lbl_ed_val, (card_x + 270 + (60 - lbl_ed_val.get_width()) // 2, card_y + 178))
            
            # Row 4: Theme
            lbl_th = theme.fonts["body_bold"].render(tr("pref_theme"), True, theme.colors["editor.foreground"])
            screen.blit(lbl_th, (card_x + 30, card_y + 230))
            pref_theme_toggle.rect.topleft = (card_x + 220, card_y + 225)
            pref_theme_toggle.draw(screen)
            
            # Bottom Close Button
            btn_pref_close.rect.topleft = (card_x + (pref_card_w - 150) // 2, card_y + 290)
            btn_pref_close.draw(screen)

        # Draw Toast notifications
        toast.draw(screen, WINDOW_WIDTH, WINDOW_HEIGHT)

        # Update Display
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
