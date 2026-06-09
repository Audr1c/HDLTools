class AppState:
    def __init__(self, prefs):
        # Window & UI configurations
        self.ui_font_scale = prefs.get("ui_scale", 1.0)
        self.code_font_size = prefs.get("editor_font_size", 14)
        self.current_theme_name = prefs.get("theme", "Dark (Default)")
        self.current_language = prefs.get("language", "en")
        self.sidebar_width = prefs.get("sidebar_width", 300)
        self.hdl_lang = prefs.get("hdl_lang", "SystemVerilog")
        
        # Design configuration
        self.module_name = "my_module"
        self.ports = [
            {"name": "clk", "dir": "IN", "width": "1"},
            {"name": "rst_n", "dir": "IN", "width": "1"},
            {"name": "a_in", "dir": "IN", "width": "8"},
            {"name": "b_in", "dir": "IN", "width": "8"},
            {"name": "sum_out", "dir": "OUT", "width": "9"}
        ]
        
        # Reset and TB Mode State
        self.is_sync_reset = False
        self.is_active_low_reset = True
        self.tb_mode = "standalone" # standalone vs chained
        
        # UI Tabs & Views
        self.right_tab = "diagram"    # diagram, code, paste
        self.code_subtab = "module"    # module, testbench, master
        self.show_preferences_modal = False
        self.running = True
