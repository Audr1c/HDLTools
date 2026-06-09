import pygame
from src.ui.widgets.base import Widget
from src.ui.widgets.button import ToggleButton, Button
from src.ui.widgets.input_box import InputBox

class PortRow:
    def __init__(self, index, port_data, on_delete):
        self.index = index
        self.port_data = port_data
        self.on_delete = on_delete
        
        self.dir_toggle = ToggleButton((0,0,50,26), ["IN", "OUT"], 
                                      initial_index=0 if port_data["dir"] == "IN" else 1,
                                      callback=self.set_dir)
        self.name_input = InputBox((0,0,180,26), text=port_data["name"], placeholder="port_name")
        self.width_input = InputBox((0,0,80,26), text=port_data["width"], placeholder="1", is_number_range=True)
        self.del_btn = Button((0,0,20,26), "", callback=self.delete_self, 
                              no_bg=True, fg_color_key="ports.reset_light", 
                              hover_fg_color_key="ports.reset", icon="X")

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

    def set_positions(self, x, y, width=366, height=26):
        active_w = width - 16
        del_w = height
        width_w = int(70 * (height / 26))
        dir_w = int(50 * (height / 26))
        
        del_x = x + active_w - del_w
        width_x = del_x - 10 - width_w
        
        self.dir_toggle.rect.topleft = (x, y)
        self.dir_toggle.rect.width = dir_w
        self.dir_toggle.rect.height = height
        
        name_w = max(50, width_x - (x + dir_w + 10) - 10)
        self.name_input.rect.topleft = (x + dir_w + 10, y)
        self.name_input.rect.width = name_w
        self.name_input.rect.height = height
        
        self.width_input.rect.topleft = (width_x, y)
        self.width_input.rect.width = width_w
        self.width_input.rect.height = height
        
        self.del_btn.rect.topleft = (del_x, y)
        self.del_btn.rect.width = del_w
        self.del_btn.rect.height = height

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
