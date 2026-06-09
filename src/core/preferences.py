import os
import sys
import json

def get_preferences_path():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        # relative to the project root directory
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(base_dir, "preferences.json")
    try:
        test_file = path + ".tmp"
        with open(test_file, "w") as f:
            f.write("")
        os.remove(test_file)
        return path
    except Exception:
        appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
        dir_path = os.path.join(appdata, "ToolsHDL")
        os.makedirs(dir_path, exist_ok=True)
        return os.path.join(dir_path, "preferences.json")

def load_preferences():
    path = get_preferences_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print("Failed to load preferences:", e)
    return {}

def save_preferences(prefs):
    path = get_preferences_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(prefs, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print("Failed to save preferences:", e)
