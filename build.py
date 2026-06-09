import os
import sys
import struct
import subprocess

def png_to_ico(png_path, ico_path):
    """Converts a PNG image into a valid Windows ICO file without external dependencies."""
    if not os.path.exists(png_path):
        print(f"Error: PNG file not found at {png_path}")
        return False
        
    print(f"Converting {png_path} to {ico_path}...")
    with open(png_path, "rb") as f:
        png_data = f.read()
        
    # Assume 32x32 size (matching your icone.png generated size)
    width = 32
    height = 32
    
    # ICO Header: Reserved (0), Type (1 = Icon), Count (1 image)
    header = struct.pack("<HHH", 0, 1, 1)
    
    # Directory Entry: Width, Height, Colors (0), Reserved (0), Planes (1), BPP (32), Size of PNG, Offset (22)
    entry = struct.pack("<BBBBHHII", width, height, 0, 0, 1, 32, len(png_data), 22)
    
    with open(ico_path, "wb") as f:
        f.write(header)
        f.write(entry)
        f.write(png_data)
        
    print("ICO file successfully created.")
    return True

def main():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)
    
    png_icon = os.path.join("assets", "images", "icone.png")
    ico_icon = os.path.join("assets", "images", "icone.ico")
    
    # 1. Convert PNG to ICO
    if not png_to_ico(png_icon, ico_icon):
        print("Falling back to compiling without custom icon...")
        icon_arg = []
    else:
        icon_arg = ["--icon", ico_icon]
        
    # 2. Package with PyInstaller
    print("Starting PyInstaller packaging...")
    cmd = [
        "pyinstaller",
        "--noconsole",
        "--onefile",
        "--add-data", "assets;assets",
        "--add-data", "theme.json;.",
        "app.py",
        "--name=Tools HDL V0.1.1"
    ]
    
    # Add icon if available
    if icon_arg:
        cmd = cmd[:3] + icon_arg + cmd[3:]
        
    print("Running command:", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True)
        print("\n" + "="*50)
        print("Success! The standalone application has been compiled.")
        print("You can find the executable here:")
        print(os.path.join(project_dir, "dist", "Tools HDL.exe"))
        print("="*50)
    except subprocess.CalledProcessError as e:
        print(f"Error during packaging: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
