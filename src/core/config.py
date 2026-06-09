import ctypes
import os
import sys
import pygame
import tkinter as tk
from tkinter import filedialog

# Set DPI awareness and AppUserModelID for Windows to prevent blurry fonts and generic taskbar icon
def setup_dpi_and_app_id():
    if sys.platform.startswith("win"):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass
        try:
            myappid = "Tools.hdl.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

def resource_path(relative_path):
    """Obtains the absolute path to the resource, working in dev and PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_path, relative_path)

# Asset Paths Setup
DOSSIER_COURANT = resource_path(".")
DOSSIER_IMAGES = os.path.join(DOSSIER_COURANT, "assets", "images")
chemin_icone = os.path.join(DOSSIER_IMAGES, "icone.png")
chemin_disquette = os.path.join(DOSSIER_IMAGES, "diskette.png")

# FPS settings
FPS = 60

def ensure_assets_exist():
    """Checks if default image assets exist, and builds them using Pygame if missing."""
    try:
        os.makedirs(DOSSIER_IMAGES, exist_ok=True)
    except Exception:
        pass

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
        except Exception as e:
            print("Failed to generate default icon:", e)

    if not os.path.exists(chemin_disquette):
        try:
            pygame.init()
            temp_d = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.rect(temp_d, (201, 209, 217), (4, 4, 24, 24), border_radius=2)
            pygame.draw.rect(temp_d, (20, 24, 33), (8, 6, 16, 6))
            pygame.draw.rect(temp_d, (20, 24, 33), (10, 18, 12, 10))
            pygame.image.save(temp_d, chemin_disquette)
        except Exception as e:
            print("Failed to generate default diskette asset:", e)

def select_open_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Open HDL Module",
        filetypes=[
            ("HDL Files", "*.sv;*.v;*.vhd;*.vhdl"),
            ("SystemVerilog Files", "*.sv"),
            ("Verilog Files", "*.v"),
            ("VHDL Files", "*.vhd;*.vhdl"),
            ("All Files", "*.*")
        ]
    )
    root.destroy()
    return file_path

def select_save_file(default_name, is_tb=False):
    root = tk.Tk()
    root.withdraw()
    ext = os.path.splitext(default_name)[1] or ".sv"
    title = "Save Testbench File" if is_tb else "Save Module File"
    file_path = filedialog.asksaveasfilename(
        title=title,
        initialfile=default_name,
        defaultextension=ext,
        filetypes=[
            ("HDL Files", "*.sv;*.v;*.vhd;*.vhdl"),
            ("SystemVerilog Files", "*.sv"),
            ("Verilog Files", "*.v"),
            ("VHDL Files", "*.vhd;*.vhdl"),
            ("All Files", "*.*")
        ]
    )
    root.destroy()
    return file_path
