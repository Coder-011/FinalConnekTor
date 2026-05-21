# core/storage.py
import json
import os
import base64
from kivy.app import App

DEFAULT_DATA = {
    "active_profile": 0,
    "auto_login": False,
    "auto_login_confirmed": False,
    "accent_theme": "electric_blue",
    "profiles": [
        {"name": "Profile 1", "username": "", "password": ""},
        {"name": "Profile 2", "username": "", "password": ""},
        {"name": "Profile 3", "username": "", "password": ""},
    ]
}

def _get_path():
    return os.path.join(App.get_running_app().user_data_dir, 'app_data.json')

def load_data() -> dict:
    path = _get_path()
    if not os.path.exists(path):
        save_data(DEFAULT_DATA.copy())
        return DEFAULT_DATA.copy()
    with open(path, 'r') as f:
        data = json.load(f)
    # Decode passwords from base64
    for p in data.get('profiles', []):
        if p.get('password'):
            try:
                p['password'] = base64.b64decode(p['password'].encode()).decode()
            except Exception:
                pass  # already plain if decode fails — leave as-is
    return data

def save_data(data: dict):
    path = _get_path()
    # Encode passwords to base64 before writing
    import copy
    data_to_write = copy.deepcopy(data)
    for p in data_to_write.get('profiles', []):
        if p.get('password'):
            p['password'] = base64.b64encode(p['password'].encode()).decode()
    with open(path, 'w') as f:
        json.dump(data_to_write, f, indent=2)
