import pygame
import tkinter as tk

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

def find_word_boundary(text, pos, direction):
    """
    Finds word boundaries for Ctrl+Arrow movement/deletion.
    direction: -1 for left, 1 for right.
    """
    if direction == -1:
        i = pos - 1
        while i >= 0 and text[i].isspace():
            i -= 1
        if i >= 0:
            is_al = text[i].isalnum() or text[i] == '_'
            while i >= 0 and ((text[i].isalnum() or text[i] == '_') == is_al) and not text[i].isspace():
                i -= 1
        return i + 1
    else:
        i = pos
        while i < len(text) and text[i].isspace():
            i += 1
        if i < len(text):
            is_al = text[i].isalnum() or text[i] == '_'
            while i < len(text) and ((text[i].isalnum() or text[i] == '_') == is_al) and not text[i].isspace():
                i += 1
        return i

class Widget:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.focused = False
        self.hovered = False

    def handle_event(self, event, offset_mouse_pos=None):
        pos = offset_mouse_pos if offset_mouse_pos else pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.focused = self.hovered
            return self.focused
        return False

    def update(self):
        pass

    def draw(self, surface):
        pass
