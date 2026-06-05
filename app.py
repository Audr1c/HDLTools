import pygame
import sys
import os
import tkinter as tk
from tkinter import filedialog

# Import our custom components
from ui_components import (
    theme, Button, ToggleButton, InputBox, Checkbox, 
    ScrollArea, PortRow, BlockDiagram, ToastManager,
    set_clipboard_text
)
from sv_parser import parse_sv_file, detect_clk_rst
from sv_generator import generate_module_code, generate_testbench_code, generate_master_tb_code

DOSSIER_COURANT = os.path.dirname(__file__)
DOSSIER_IMAGES = os.path.join(DOSSIER_COURANT, "assets", "images")

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

def draw_highlighted_line(surface, font, line_text, x, y):
    import re
    words = re.split(r'(\s+|[;,().#`]|//.*)', line_text)
    curr_x = x
    
    for word in words:
        if not word:
            continue
            
        color = theme.colors["editor.foreground"]
        
        # Color matching
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

def main():
    # Initialize Pygame and Setup theme fonts
    pygame.init()
    pygame.display.set_caption("SystemVerilog Tool - Module & Testbench Designer")

    # Charger l'icône
    chemin_icone = os.path.join(DOSSIER_IMAGES, "icone.png")
    icone = pygame.image.load(chemin_icone)

    # Appliquer l'icône
    if sys.platform == "win32":
        import ctypes
        # Donne un identifiant unique à votre application pour Windows
        myappid = "Tools.hdl.1.0"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    try:
        # icone = pygame.image.load(chemin_icone)
        pygame.display.set_icon(icone)
    except pygame.error:
        print(f"Impossible de charger l'image à l'emplacement : {chemin_icone}")

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
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
    
    # Checkbox States for TB generation
    is_sync_reset = False
    is_active_low_reset = True
    
    # New simulation settings
    tb_mode = "standalone" # "standalone" or "chained"
    wait_event = ""
    trig_event = ""
    call_finish = True
    
    # Active Panels / Tabs
    right_tab = "diagram" 
    code_subtab = "testbench" # "module", "testbench", "master"
    
    # Toast Manager
    toast = ToastManager()
    
    # UI Elements Initialization (Left Panel Layout)
    module_name_input = InputBox((140, 55, 200, 26), text=module_name, placeholder="module_name")
    
    active_low_cb = Checkbox((20, 90, 200, 26), "Active Low Reset", initial_val=is_active_low_reset)
    sync_reset_cb = Checkbox((230, 90, 200, 26), "Synchronous Reset", initial_val=is_sync_reset)
    
    btn_add_clk = Button((20, 120, 100, 26), "Add Clock", callback=lambda: add_clock_preset())
    btn_add_rst = Button((130, 120, 100, 26), "Add Reset", callback=lambda: add_reset_preset())
    
    # Testbench Mode widgets
    tb_mode_toggle = ToggleButton((20, 185, 140, 26), ["Standalone", "Master-Chained"], initial_index=0)
    call_finish_cb = Checkbox((180, 185, 150, 26), "Call $finish", initial_val=call_finish)
    
    wait_event_input = InputBox((70, 215, 170, 26), text=wait_event, placeholder="master_tb.event")
    trig_event_input = InputBox((300, 215, 180, 26), text=trig_event, placeholder="master_tb.event")
    
    # Port list headers
    btn_add_input = Button((230, 253, 110, 26), "+ Input", callback=lambda: add_input_port())
    btn_add_output = Button((350, 253, 110, 26), "+ Output", callback=lambda: add_output_port())
    
    # PortRows
    port_rows = []
    
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

    # Scroll Areas
    ports_scroll = ScrollArea((20, 285, 460, 335))
    code_scroll = ScrollArea((520, 110, 740, 590))
    
    # Visual Diagram Area
    diagram_visualizer = BlockDiagram((520, 65, 740, 635))
    
    # Generated Code lines cache
    generated_code_lines = []
    
    def get_master_tb_code():
        # Build master simulation chain
        # The master tb includes current module and illustrates chaining setup
        sub_tbs = [
            {"module_name": module_name, "wait_event": wait_event, "trigger_event": trig_event}
        ]
        
        # Add dynamic chained testbench examples to demonstrate concept
        if trig_event:
            clean_trig = trig_event.replace("master_tb.", "")
            sub_tbs.append({
                "module_name": "next_module",
                "wait_event": trig_event,
                "trigger_event": f"master_tb.next_module_is_done"
            })
        elif wait_event:
            clean_wait = wait_event.replace("master_tb.", "")
            sub_tbs.insert(0, {
                "module_name": "prev_module",
                "wait_event": "",
                "trigger_event": wait_event
            })
        else:
            # Simple demonstration default
            sub_tbs.append({
                "module_name": "other_module",
                "wait_event": f"master_tb.{module_name}_is_done",
                "trigger_event": ""
            })
            
        return generate_master_tb_code(sub_tbs)

    def update_code_cache():
        nonlocal generated_code_lines
        if code_subtab == "module":
            code_str = generate_module_code(module_name, ports)
        elif code_subtab == "testbench":
            code_str = generate_testbench_code(
                module_name, ports, is_sync_reset, is_active_low_reset,
                tb_mode, wait_event, trig_event, call_finish
            )
        else: # "master"
            code_str = get_master_tb_code()
            
        generated_code_lines = code_str.split("\n")
        code_scroll.virtual_height = len(generated_code_lines) * 18
        
    update_code_cache()
    
    # Right panel Tab selectors
    btn_tab_diagram = Button((520, 20, 150, 30), "Block Diagram", callback=lambda: set_right_tab("diagram"))
    btn_tab_code = Button((680, 20, 150, 30), "Code Preview", callback=lambda: set_right_tab("code"))
    
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
        
    # Action Buttons
    def handle_save_module():
        path = select_save_file(f"{module_name}.sv", is_tb=False)
        if path:
            try:
                code_str = generate_module_code(module_name, ports)
                with open(path, 'w') as f:
                    f.write(code_str)
                toast.show(f"Saved module to {os.path.basename(path)}")
            except Exception as e:
                toast.show(f"Error saving: {e}", is_error=True)
                
    def handle_save_testbench():
        if code_subtab == "master":
            default_fn = "master_tb.sv"
            is_tb_save = True
        else:
            default_fn = f"tb_{module_name}.sv" if code_subtab == "testbench" else f"{module_name}.sv"
            is_tb_save = (code_subtab == "testbench")
            
        path = select_save_file(default_fn, is_tb=is_tb_save)
        if path:
            try:
                if code_subtab == "module":
                    code_str = generate_module_code(module_name, ports)
                elif code_subtab == "testbench":
                    code_str = generate_testbench_code(
                        module_name, ports, is_sync_reset, is_active_low_reset,
                        tb_mode, wait_event, trig_event, call_finish
                    )
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
                parsed_name, parsed_ports = parse_sv_file(content)
                if parsed_name:
                    nonlocal module_name, ports, is_active_low_reset
                    module_name = parsed_name
                    module_name_input.text = parsed_name
                    module_name_input.cursor_pos = len(parsed_name)
                    ports = parsed_ports
                    
                    # Detect clk/rst to configure checkboxes
                    clk_p, rst_p = detect_clk_rst(ports)
                    if rst_p:
                        is_active_low_reset = rst_p["name"].lower().endswith("n") or rst_p["name"].lower().endswith("b")
                        active_low_cb.checked = is_active_low_reset
                        
                    rebuild_port_rows()
                    update_code_cache()
                    toast.show(f"Parsed module '{parsed_name}' ({len(ports)} ports)")
                else:
                    toast.show("No valid module declaration found", is_error=True)
            except Exception as e:
                toast.show(f"Error parsing file: {e}", is_error=True)
                
    def handle_copy_code():
        if code_subtab == "module":
            code_str = generate_module_code(module_name, ports)
        elif code_subtab == "testbench":
            code_str = generate_testbench_code(
                module_name, ports, is_sync_reset, is_active_low_reset,
                tb_mode, wait_event, trig_event, call_finish
            )
        else:
            code_str = get_master_tb_code()
        set_clipboard_text(code_str)
        toast.show("Code copied to clipboard!")

    btn_gen_mod = Button((20, 635, 220, 35), "Generate Module (.sv)", callback=handle_save_module, is_accent=True)
    btn_gen_tb = Button((250, 635, 230, 35), "Generate Testbench (.sv)", callback=handle_save_testbench, is_accent=True)
    btn_parse = Button((20, 675, 460, 35), "Parse SV Module File", callback=handle_parse_file, bg_color_key="list.activeSelectionBackground")
    btn_copy = Button((1140, 65, 120, 26), "Copy Code", callback=handle_copy_code, bg_color_key="button.background")

    def update_tab_highlights():
        btn_tab_diagram.is_accent = (right_tab == "diagram")
        btn_tab_code.is_accent = (right_tab == "code")
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
            
        # Check simulation config changes
        curr_mode = "standalone" if tb_mode_toggle.getValue() == "Standalone" else "chained"
        if tb_mode != curr_mode:
            tb_mode = curr_mode
            update_code_cache()
            
        if call_finish != call_finish_cb.checked:
            call_finish = call_finish_cb.checked
            update_code_cache()
            
        if wait_event != wait_event_input.text:
            wait_event = wait_event_input.text
            update_code_cache()
            
        if trig_event != trig_event_input.text:
            trig_event = trig_event_input.text
            update_code_cache()
            
        update_tab_highlights()

        # Event handling
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Global keys
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    focusable = [module_name_input]
                    if tb_mode == "chained":
                        focusable.append(wait_event_input)
                        focusable.append(trig_event_input)
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
                        
                        # Handle scroll to focus
                        # We need to compute if the next focused item is a port row
                        # Ports start at index 3 if chained, else 1
                        start_ports_idx = 3 if tb_mode == "chained" else 1
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
            
            # Action buttons
            btn_add_clk.handle_event(event)
            btn_add_rst.handle_event(event)
            
            # TB settings events (only handle wait/trig if chained)
            tb_mode_toggle.handle_event(event)
            call_finish_cb.handle_event(event)
            if tb_mode == "chained":
                wait_event_input.handle_event(event)
                trig_event_input.handle_event(event)
            else:
                wait_event_input.focused = False
                trig_event_input.focused = False
            
            btn_add_input.handle_event(event)
            btn_add_output.handle_event(event)
            
            btn_gen_mod.handle_event(event)
            btn_gen_tb.handle_event(event)
            btn_parse.handle_event(event)
            
            # Right panel tabs
            btn_tab_diagram.handle_event(event)
            btn_tab_code.handle_event(event)
            
            if right_tab == "code":
                btn_subtab_mod.handle_event(event)
                btn_subtab_tb.handle_event(event)
                btn_subtab_master.handle_event(event)
                btn_copy.handle_event(event)
                code_scroll.handle_event(event)

            # Ports scroll area handling
            ports_scroll.handle_event(event)
            
            mouse_pos = pygame.mouse.get_pos()
            in_scroll_viewport = ports_scroll.rect.collidepoint(mouse_pos)
            offset_pos = (mouse_pos[0], mouse_pos[1] + ports_scroll.scroll_y) if in_scroll_viewport else (-1, -1)
            
            for idx, row in enumerate(port_rows):
                row.set_positions(20, 285 + idx * 36)
                row.handle_event(event, offset_pos)

        # Update
        module_name_input.update()
        sync_reset_cb.update()
        active_low_cb.update()
        
        btn_add_clk.update()
        btn_add_rst.update()
        
        tb_mode_toggle.update()
        call_finish_cb.update()
        if tb_mode == "chained":
            wait_event_input.update()
            trig_event_input.update()
            
        btn_add_input.update()
        btn_add_output.update()
        
        btn_gen_mod.update()
        btn_gen_tb.update()
        btn_parse.update()
        
        btn_tab_diagram.update()
        btn_tab_code.update()
        
        if right_tab == "code":
            btn_subtab_mod.update()
            btn_subtab_tb.update()
            btn_subtab_master.update()
            btn_copy.update()
            
        for r in port_rows:
            r.update()
            
        ports_scroll.virtual_height = len(ports) * 36
        
        # Trigger cache update if editing
        if pygame.key.get_focused() or any(r.name_input.focused or r.width_input.focused for r in port_rows):
            update_code_cache()

        # Rendering
        screen.fill(theme.colors["editor.background"])
        
        # 1. DRAW LEFT PANEL (SideBar)
        sidebar_rect = pygame.Rect(0, 0, 500, WINDOW_HEIGHT)
        pygame.draw.rect(screen, theme.colors["sideBar.background"], sidebar_rect)
        pygame.draw.line(screen, theme.colors["sideBar.border"], (500, 0), (500, WINDOW_HEIGHT), 2)
        
        # Panel Title
        lbl_title = theme.fonts["header"].render("HDL Tools", True, theme.colors["editor.foreground"])
        screen.blit(lbl_title, (20, 20))
        
        # Module name input
        lbl_mod = theme.fonts["body"].render("Module Name:", True, theme.colors["editor.foreground"])
        screen.blit(lbl_mod, (20, 60))
        module_name_input.draw(screen)
        
        # Checkboxes
        active_low_cb.draw(screen)
        sync_reset_cb.draw(screen)
        
        # Presets
        btn_add_clk.draw(screen)
        btn_add_rst.draw(screen)
        
        # Divider 1
        pygame.draw.line(screen, theme.colors["sideBar.border"], (20, 155), (480, 155), 1)
        
        # Testbench Mode Labels & Fields
        lbl_tb_title = theme.fonts["body_bold"].render("Testbench Settings", True, theme.colors["editor.foreground"])
        screen.blit(lbl_tb_title, (20, 162))
        
        tb_mode_toggle.draw(screen)
        call_finish_cb.draw(screen)
        
        # Wait event
        lbl_wait = theme.fonts["body"].render("Wait:", True, theme.colors["editor.foreground"])
        screen.blit(lbl_wait, (20, 220))
        wait_event_input.draw(screen)
        
        # Trigger event
        lbl_trig = theme.fonts["body"].render("Trig:", True, theme.colors["editor.foreground"])
        screen.blit(lbl_trig, (255, 220))
        trig_event_input.draw(screen)
        
        # Overlay if disabled (Standalone Mode)
        if tb_mode == "standalone":
            overlay_w = pygame.Surface((170, 26), pygame.SRCALPHA)
            overlay_w.fill((0, 0, 0, 130))
            screen.blit(overlay_w, (70, 215))
            pygame.draw.rect(screen, theme.colors["sideBar.border"], (70, 215, 170, 26), width=1, border_radius=6)
            
            overlay_t = pygame.Surface((180, 26), pygame.SRCALPHA)
            overlay_t.fill((0, 0, 0, 130))
            screen.blit(overlay_t, (300, 215))
            pygame.draw.rect(screen, theme.colors["sideBar.border"], (300, 215, 180, 26), width=1, border_radius=6)
            
        # Divider 2
        pygame.draw.line(screen, theme.colors["sideBar.border"], (20, 250), (480, 250), 1)
        
        # Ports title
        lbl_ports = theme.fonts["body_bold"].render("Module Ports", True, theme.colors["editor.foreground"])
        screen.blit(lbl_ports, (20, 258))
        
        btn_add_input.draw(screen)
        btn_add_output.draw(screen)
        
        # Ports list drawing
        def draw_ports_list(surface, scroll_y):
            for idx, r in enumerate(port_rows):
                ry = 285 + idx * 36
                r.set_positions(20, ry)
                
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
        
        # Bottom Actions
        pygame.draw.line(screen, theme.colors["sideBar.border"], (20, 627), (480, 627), 1)
        btn_gen_mod.draw(screen)
        btn_gen_tb.draw(screen)
        btn_parse.draw(screen)
        
        # 2. DRAW RIGHT PANEL (Viewer)
        btn_tab_diagram.draw(screen)
        btn_tab_code.draw(screen)
        
        if right_tab == "diagram":
            diagram_visualizer.draw(screen, module_name, ports)
        else:
            # Code preview panel background
            code_bg_rect = pygame.Rect(520, 65, 740, 635)
            pygame.draw.rect(screen, theme.colors["sideBar.background"], code_bg_rect, border_radius=12)
            pygame.draw.rect(screen, theme.colors["sideBar.border"], code_bg_rect, width=2, border_radius=12)
            
            # Sub-tabs
            btn_subtab_mod.draw(screen)
            btn_subtab_tb.draw(screen)
            btn_subtab_master.draw(screen)
            btn_copy.draw(screen)
            
            # Draw separator
            pygame.draw.line(screen, theme.colors["sideBar.border"], (520, 100), (1260, 100), 1)
            
            # Render scrollable code
            def draw_code_viewport(surface, scroll_y):
                font = theme.fonts["code"]
                line_h = 18
                for idx, line in enumerate(generated_code_lines):
                    vy = idx * line_h
                    sy = 110 + vy - scroll_y
                    
                    if 110 - line_h < sy < 700:
                        draw_highlighted_line(surface, font, line, 535, sy)
                        
            code_scroll.draw(screen, draw_code_viewport)

        # Draw Toast notifications
        toast.draw(screen, WINDOW_WIDTH, WINDOW_HEIGHT)

        # Update Display
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
