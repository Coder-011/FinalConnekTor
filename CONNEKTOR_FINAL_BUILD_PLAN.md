# ConnekTor v4 — FINAL MASTER BUILD PLAN
### Single source of truth for Antigravity. Do not use any other document.

This document supersedes all previous plans. It consolidates the APK
disassembly findings, all verified implementation decisions, the background
auto-login feature, the color-theme system, and the complete GitHub Actions
CI/CD pipeline. Build ONLY from this document.

---

## PART 0 — CRITICAL CONSTRAINTS (READ FIRST, VIOLATE NOTHING)

These are hard rules. Every single one has caused a real build failure before.

```
PYTHON VERSION    : 3.11 exactly. Not 3.12. Not 3.10.
                    The APK binary was compiled with libpython3.11.so.
                    python-for-android's kivy recipe pins to 3.11 on the
                    buildozer Docker image used below. 3.12 breaks p4a.

KIVY VERSION      : kivy==2.3.0 exactly. Do not use "kivy" with no version.
                    KivyMD must be pinned to kivymd==1.1.1 — later versions
                    changed MDBottomNavigation API and break the layout.

BUILDOZER VERSION : buildozer==1.5.0 exactly.
                    Do not use pip install buildozer with no pin — latest
                    buildozer (1.5+) changed how requirements are resolved.

NDK VERSION       : 25b (r25b). Set android.ndk = 25b in buildozer.spec.
                    NDK 26+ breaks the SDL2 recipe on arm64.

SDK BUILD-TOOLS   : 33.0.2. Set android.sdk_build_tools = 33.0.2.

JAVA VERSION      : 17. GitHub Actions must use actions/setup-java@v3
                    with java-version: '17'. Java 21 breaks some dx steps.

NO SPACES IN PATH : The build must happen in /home/runner/work/ which has
                    no spaces. Never cd into a path with spaces.

THREADING RULE    : EVERY network call runs in threading.Thread(daemon=True).
                    EVERY widget update from a thread uses Clock.schedule_once.
                    Zero exceptions. Violating this causes silent ANR crashes.

WINDOW SIZE RULE  : Window.size is ONLY set when platform != 'android'.
                    Setting it unconditionally breaks Android fullscreen layout.

NO SESSION REUSE  : Never use a persistent requests.Session() across login
                    attempts. Always construct a fresh POST. The portal issues
                    new state per connection.
```

---

## PART 1 — EXACT REPOSITORY STRUCTURE

Create every file listed. Zero deviations. `__init__.py` files must exist.

```
connektor/                        ← repo root
├── .github/
│   └── workflows/
│       └── build.yml             ← GitHub Actions CI/CD
├── main.py                       ← MDApp entry point
├── buildozer.spec                ← complete build config
├── requirements.txt              ← for GitHub Actions pip install
├── core/
│   ├── __init__.py               ← empty file, required for imports
│   ├── login.py                  ← captive portal POST logic
│   ├── storage.py                ← JSON read/write
│   └── wifi_monitor.py           ← background probe thread
├── screens/
│   ├── __init__.py               ← empty file, required for imports
│   ├── home.py                   ← HomeScreen class
│   ├── profiles.py               ← ProfilesScreen class
│   └── settings.py               ← SettingsScreen class
├── theme/
│   ├── __init__.py               ← empty file, required for imports
│   └── colors.py                 ← all color theme definitions
├── kv/
│   ├── home.kv
│   ├── profiles.kv
│   └── settings.kv
└── assets/
    ├── fonts/
    │   ├── Poppins-Bold.ttf      ← extracted from original APK
    │   ├── Poppins-Regular.ttf   ← download from Google Fonts if missing
    │   └── MaterialIcons.ttf     ← download from Google Fonts
    └── icon.png                  ← 512x512 app icon, dark navy bg
```

---

## PART 2 — buildozer.spec (COMPLETE, EXACT)

```ini
[app]
title = ConnekTor
package.name = connektor
package.domain = org.citpc
source.dir = .
source.include_exts = py,kv,json,ttf,otf,png,jpg
version = 4.0.0

requirements = python3==3.11.0,kivy==2.3.0,kivymd==1.1.1,requests,certifi,charset-normalizer,urllib3==1.26.18,idna

# urllib3 MUST be pinned to 1.26.18 — version 2.x dropped the
# urllib3.exceptions.InsecureRequestWarning class that requests relies on
# when verify=False. This will cause an AttributeError at runtime on 2.x.

orientation = portrait
fullscreen = 0
android.minapi = 21
android.targetapi = 33
android.ndk = 25b
android.sdk_build_tools = 33.0.2
android.archs = arm64-v8a, armeabi-v7a

android.permissions = INTERNET, ACCESS_WIFI_STATE, CHANGE_WIFI_STATE, ACCESS_NETWORK_STATE, CHANGE_NETWORK_STATE

android.allow_backup = False
android.logcat_filters = *:S python:D

# Presplash color matches app background — avoids white flash on launch
presplash.color = #0D0E1A
icon.filename = %(source.dir)s/assets/icon.png

[buildozer]
log_level = 2
warn_on_root = 1
```

---

## PART 3 — GitHub Actions Workflow (.github/workflows/build.yml)

```yaml
name: Build ConnekTor APK

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-22.04        # DO NOT use ubuntu-latest — it may resolve
                                  # to 24.04 which has OpenJDK 21 by default

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Java 17
        uses: actions/setup-java@v3
        with:
          distribution: temurin
          java-version: '17'

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install system dependencies
        run: |
          sudo apt-get update -qq
          sudo apt-get install -y \
            git zip unzip openjdk-17-jdk \
            autoconf libtool pkg-config \
            zlib1g-dev libncurses5-dev libncursesw5-dev \
            libtinfo5 cmake libffi-dev libssl-dev \
            build-essential libltdl-dev ccache \
            python3-pip python3-setuptools

      - name: Install Python build tools
        run: |
          pip install --upgrade pip
          pip install buildozer==1.5.0
          pip install cython==0.29.37

          # Cython MUST be 0.29.37 — Cython 3.x changed how .pyx files
          # are compiled and breaks the kivy extension modules.

      - name: Cache Buildozer global directory
        uses: actions/cache@v4
        with:
          path: ~/.buildozer
          key: buildozer-${{ runner.os }}-${{ hashFiles('buildozer.spec') }}
          restore-keys: |
            buildozer-${{ runner.os }}-

      - name: Cache pip
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: pip-${{ runner.os }}-${{ hashFiles('requirements.txt') }}

      - name: Build APK
        run: |
          buildozer android debug 2>&1 | tee build.log

      - name: Upload APK artifact
        uses: actions/upload-artifact@v4
        with:
          name: ConnekTor-debug
          path: bin/*.apk
          retention-days: 30

      - name: Upload build log on failure
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: build-log
          path: build.log
```

---

## PART 4 — requirements.txt (for GitHub Actions pip installs)

```
buildozer==1.5.0
cython==0.29.37
```

This file is only used by the CI pip install steps. The actual APK dependencies
are declared in buildozer.spec requirements — not here.

---

## PART 5 — THEME SYSTEM (theme/colors.py)

The app is ALWAYS dark. The dark background never changes.
What changes between themes is the ACCENT color — the glow color, text
highlights, button borders, status indicators, and active nav tab color.
The background (`#0D0E1A`) and card colors (`#161829`) are fixed.

```python
# theme/colors.py

# ── FIXED COLORS — never change regardless of theme ───────────────────────
BG_PRIMARY    = '#0D0E1A'   # main background — always dark navy
BG_CARD       = '#161829'   # card/section background
BG_NAV        = '#111220'   # bottom nav bar
TEXT_PRIMARY  = '#FFFFFF'   # main text
TEXT_MUTED    = '#8E8EA0'   # subtitles, hints, placeholders
STATUS_FAIL   = '#FF4757'   # red — FAILED badge
STATUS_OK     = '#2ED573'   # green — CONNECTED badge
STATUS_WAIT   = '#FFA502'   # amber — CONNECTING badge
BTN_IDLE_A    = '#FF6B6B'   # connect button gradient start (coral)
BTN_IDLE_B    = '#FF8E53'   # connect button gradient end (orange)
BTN_OK_A      = '#43C59E'   # connect button success gradient start
BTN_OK_B      = '#2ECC71'   # connect button success gradient end

# ── ACCENT THEMES — the user picks one of these ───────────────────────────
# Each theme is a dict with 3 keys:
#   accent      : primary highlight color (titles, active nav, card borders)
#   accent_soft : lighter tint for secondary highlights
#   glow        : rgba tuple for canvas glow effects (e.g. button outer glow)
#
# Used on: screen titles, active bottom-nav icon, profile name text,
#          section header labels, input field focus border, Save button,
#          toggle switch track, MDDialog ENABLE button, WiFiMonitor
#          status pulse ring around CONNECT button.

ACCENT_THEMES = {

    'electric_blue': {
        'name':       'Electric Blue',    # display name in Settings
        'accent':     '#5B6BF5',          # original / default
        'accent_soft':'#7C89FF',
        'glow':       (0.36, 0.42, 0.96, 0.25),
    },

    'cyber_violet': {
        'name':       'Cyber Violet',
        'accent':     '#A855F7',
        'accent_soft':'#C084FC',
        'glow':       (0.66, 0.33, 0.97, 0.25),
    },

    'neon_green': {
        'name':       'Neon Green',
        'accent':     '#22C55E',
        'accent_soft':'#4ADE80',
        'glow':       (0.13, 0.77, 0.37, 0.25),
    },

    'hot_pink': {
        'name':       'Hot Pink',
        'accent':     '#EC4899',
        'accent_soft':'#F472B6',
        'glow':       (0.93, 0.28, 0.60, 0.25),
    },

    'solar_orange': {
        'name':       'Solar Orange',
        'accent':     '#F97316',
        'accent_soft':'#FB923C',
        'glow':       (0.98, 0.45, 0.09, 0.25),
    },

    'ice_cyan': {
        'name':       'Ice Cyan',
        'accent':     '#06B6D4',
        'accent_soft':'#22D3EE',
        'glow':       (0.02, 0.71, 0.83, 0.25),
    },

    'gold': {
        'name':       'Gold',
        'accent':     '#EAB308',
        'accent_soft':'#FBBF24',
        'glow':       (0.92, 0.70, 0.03, 0.25),
    },
}

DEFAULT_ACCENT = 'electric_blue'


def get_accent(theme_key: str) -> dict:
    """Returns the theme dict for the given key, falling back to default."""
    return ACCENT_THEMES.get(theme_key, ACCENT_THEMES[DEFAULT_ACCENT])
```

---

## PART 6 — app_data.json SCHEMA

Stored at `os.path.join(App.get_running_app().user_data_dir, 'app_data.json')`.
Created with defaults on first launch if not present.

```json
{
  "active_profile": 0,
  "auto_login": false,
  "auto_login_confirmed": false,
  "accent_theme": "electric_blue",
  "profiles": [
    {"name": "Profile 1", "username": "", "password": ""},
    {"name": "Profile 2", "username": "", "password": ""},
    {"name": "Profile 3", "username": "", "password": ""}
  ]
}
```

Key notes:
- `"theme"` key is REMOVED — there is no light/dark toggle. App is always dark.
- `"accent_theme"` replaces it — stores the chosen accent key from `ACCENT_THEMES`.
- `"auto_login_confirmed"` tracks whether the first-enable dialog has been shown.
  Set to `true` after user clicks ENABLE. Once true, re-enabling skips the dialog.
- Passwords stored as base64-encoded strings. Encode on save, decode on load.
  Use `import base64; base64.b64encode(pw.encode()).decode()` and reverse.
  NOT plaintext like the original — minimum viable obfuscation.

---

## PART 7 — core/storage.py (COMPLETE SOURCE)

```python
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
```

---

## PART 8 — core/login.py (COMPLETE SOURCE)

This is the exact logic reconstructed from the APK bytecode. Do not refactor
the payload encoding. Do not switch to `data=dict` in requests.post.
Do not change the field names. Do not change the URL.

```python
# core/login.py
import time
import threading
import requests
import urllib3
from kivy.clock import Clock

# Suppress InsecureRequestWarning — portal uses self-signed cert
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ── PORTAL CONSTANTS (extracted verbatim from APK bytecode) ────────────────
LOGIN_URL   = 'https://10.100.1.1:8090/login.xml'
REFERER     = 'https://10.100.1.1:8090/'
MODE        = '191'
PRODUCTTYPE = 'your_producttype'   # literal string from binary — do not change
USER_AGENT  = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/58.0.3029.110 Safari/537.3'
)
SUCCESS_STRING = 'You are signed in as'  # portal response on success

def perform_login(username: str, password: str, result_callback):
    """
    Fires a POST to the captive portal login endpoint.
    Runs in a daemon thread — never call this directly on the main thread.

    result_callback(status: str, message: str) — called via Clock.schedule_once
    status is one of: 'connected', 'failed', 'error'
    message is a human-readable string for the UI status badge.
    """
    def _worker():
        # Fresh timestamp on EVERY call — prevents replay rejection
        timestamp = int(time.time() * 1000)

        payload = {
            'mode':        MODE,
            'username':    username,
            'password':    password,
            'a':           timestamp,
            'producttype': PRODUCTTYPE,
        }

        # Manual URL-encoding — exactly as the original APK does it.
        # Do NOT replace with data=payload in requests.post.
        payload_encoded = '&'.join([
            f'{k}={requests.utils.quote(str(v))}'
            for k, v in payload.items()
        ])

        headers = {
            'User-Agent':   USER_AGENT,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer':      REFERER,
        }

        # Retry loop — up to 2 attempts on Timeout
        for attempt in range(2):
            try:
                response = requests.post(
                    LOGIN_URL,
                    data=payload_encoded,
                    headers=headers,
                    verify=False,    # portal has self-signed cert
                    timeout=10,
                )

                if SUCCESS_STRING in response.text:
                    Clock.schedule_once(
                        lambda dt: result_callback('connected', 'Connected'), 0
                    )
                else:
                    Clock.schedule_once(
                        lambda dt: result_callback('failed', 'Login Failed'), 0
                    )
                return

            except requests.exceptions.Timeout:
                if attempt == 0:
                    # Refresh timestamp and retry once
                    time.sleep(2)
                    timestamp = int(time.time() * 1000)
                    payload['a'] = timestamp
                    payload_encoded = '&'.join([
                        f'{k}={requests.utils.quote(str(v))}'
                        for k, v in payload.items()
                    ])
                    continue
                Clock.schedule_once(
                    lambda dt: result_callback('failed', 'Timed Out'), 0
                )
                return

            except requests.exceptions.ConnectionError:
                Clock.schedule_once(
                    lambda dt: result_callback('error', 'No Network'), 0
                )
                return

            except requests.exceptions.RequestException as e:
                msg = str(e)[:40]
                Clock.schedule_once(
                    lambda dt: result_callback('error', f'Error: {msg}'), 0
                )
                return

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
```

---

## PART 9 — core/wifi_monitor.py (COMPLETE SOURCE)

```python
# core/wifi_monitor.py
import threading
import time
import requests
from kivy.clock import Clock

POLL_INTERVAL  = 8    # seconds between probes
COOLDOWN       = 30   # seconds between auto-login attempts
PORTAL_HOST    = '10.100.1.1'
PROBE_URL      = 'http://captive.apple.com'   # plain HTTP — portals intercept this


class WiFiMonitor:
    """
    Background probe thread. Polls every POLL_INTERVAL seconds.
    When it detects the campus captive portal (redirect to 10.100.1.1),
    it fires login_callback on the main thread via Clock.schedule_once.

    Reads get_enabled() on every cycle — toggle changes take effect immediately
    without restarting the thread.

    Only one thread runs at a time. Calling start() when already running
    is a no-op.
    """

    def __init__(self, login_callback, get_enabled):
        self._running         = False
        self._thread          = None
        self._login_callback  = login_callback   # called on main thread
        self._get_enabled     = get_enabled      # () -> bool
        self._last_attempt    = 0

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._running = True
        self._thread  = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _run(self):
        while self._running:
            time.sleep(POLL_INTERVAL)
            if not self._running:
                break
            if not self._get_enabled():
                continue
            if time.time() - self._last_attempt < COOLDOWN:
                continue
            try:
                self._probe()
            except Exception:
                pass   # never let the monitor thread crash

    def _probe(self):
        try:
            r = requests.get(
                PROBE_URL,
                timeout=5,
                allow_redirects=True,
                verify=False,
            )
            if PORTAL_HOST in r.url or PORTAL_HOST in r.text:
                self._last_attempt = time.time()
                Clock.schedule_once(lambda dt: self._login_callback(), 0)
        except (requests.exceptions.ConnectionError,
                requests.exceptions.Timeout):
            pass
```

---

## PART 10 — main.py (COMPLETE SOURCE)

```python
# main.py
import os
import urllib3
from kivy.utils import platform
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.clock import Clock
from kivymd.app import MDApp

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if platform != 'android':
    Window.size = (390, 780)   # desktop preview only — NOT set on Android

from core.storage    import load_data, save_data
from core.wifi_monitor import WiFiMonitor
from screens.home    import HomeScreen
from screens.profiles import ProfilesScreen
from screens.settings import SettingsScreen

KV_FILES = ['kv/home.kv', 'kv/profiles.kv', 'kv/settings.kv']


class ConnekTorApp(MDApp):

    def build(self):
        self.theme_cls.theme_style    = 'Dark'
        self.theme_cls.primary_palette = 'DeepPurple'

        for kv in KV_FILES:
            Builder.load_file(kv)

        self.app_data = load_data()

        self.sm = ScreenManager(transition=NoTransition())
        self.sm.add_widget(HomeScreen(name='home'))
        self.sm.add_widget(ProfilesScreen(name='profiles'))
        self.sm.add_widget(SettingsScreen(name='settings'))

        self.monitor = WiFiMonitor(
            login_callback=self._auto_login_trigger,
            get_enabled=lambda: self.app_data.get('auto_login', False),
        )
        self.monitor.start()

        return self.sm

    def _auto_login_trigger(self):
        """Called on main thread when monitor detects captive portal."""
        if not self.app_data.get('auto_login', False):
            return
        home = self.sm.get_screen('home')
        home.start_login()

    def on_stop(self):
        self.monitor.stop()
        save_data(self.app_data)


if __name__ == '__main__':
    ConnekTorApp().run()
```

---

## PART 11 — screens/home.py (COMPLETE SOURCE)

```python
# screens/home.py
from kivy.uix.screenmanager import Screen
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.app import App
from core.login import perform_login
from theme.colors import get_accent, STATUS_FAIL, STATUS_OK, STATUS_WAIT


class HomeScreen(Screen):

    def on_enter(self):
        self._refresh_profile_card()
        self._apply_accent()

    def _apply_accent(self):
        app   = App.get_running_app()
        theme = get_accent(app.app_data.get('accent_theme', 'electric_blue'))
        # Apply accent color to title label
        self.ids.title_label.color = theme['accent']
        # Apply to active profile name
        self.ids.profile_name_label.color = theme['accent']
        # Apply accent to nav indicator — done in kv via app binding

    def _refresh_profile_card(self):
        app  = App.get_running_app()
        idx  = app.app_data.get('active_profile', 0)
        prof = app.app_data['profiles'][idx]
        self.ids.profile_name_label.text   = prof['name'] or f'Profile {idx+1}'
        self.ids.profile_index_label.text  = f'{idx+1} / 3 — tap to switch'

    def on_profile_card_tap(self):
        app = App.get_running_app()
        idx = app.app_data.get('active_profile', 0)
        app.app_data['active_profile'] = (idx + 1) % 3
        from core.storage import save_data
        save_data(app.app_data)
        self._refresh_profile_card()

    def on_connect_press(self):
        app  = App.get_running_app()
        idx  = app.app_data.get('active_profile', 0)
        prof = app.app_data['profiles'][idx]
        if not prof.get('username') or not prof.get('password'):
            self._set_status('failed', 'No Credentials Saved')
            return
        self.start_login()

    def start_login(self):
        """Called by CONNECT button AND by auto-login trigger."""
        app  = App.get_running_app()
        idx  = app.app_data.get('active_profile', 0)
        prof = app.app_data['profiles'][idx]
        self._set_status('connecting', 'Connecting...')
        self._start_pulse()
        perform_login(prof['username'], prof['password'], self._on_login_result)

    def _on_login_result(self, status: str, message: str):
        """Called on main thread via Clock.schedule_once inside login.py."""
        self._stop_pulse()
        self._set_status(status, message)

    def _set_status(self, status: str, message: str):
        """Always called on main thread — safe to touch widgets directly."""
        badge = self.ids.status_badge
        label = self.ids.status_label
        label.text = message.upper()
        colors = {
            'connected':  STATUS_OK,
            'failed':     STATUS_FAIL,
            'connecting': STATUS_WAIT,
            'error':      STATUS_FAIL,
        }
        badge.md_bg_color = self._hex_to_rgba(colors.get(status, STATUS_FAIL))

    def _start_pulse(self):
        btn = self.ids.connect_btn
        self._pulse_anim = Animation(
            scale_x=1.05, scale_y=1.05, duration=0.4
        ) + Animation(
            scale_x=1.0, scale_y=1.0, duration=0.4
        )
        self._pulse_anim.repeat = True
        self._pulse_anim.start(btn)

    def _stop_pulse(self):
        if hasattr(self, '_pulse_anim'):
            self._pulse_anim.stop(self.ids.connect_btn)
        self.ids.connect_btn.scale_x = 1.0
        self.ids.connect_btn.scale_y = 1.0

    @staticmethod
    def _hex_to_rgba(hex_color: str) -> list:
        h = hex_color.lstrip('#')
        return [int(h[i:i+2], 16)/255 for i in (0, 2, 4)] + [1.0]
```

---

## PART 12 — screens/profiles.py (COMPLETE SOURCE)

```python
# screens/profiles.py
from kivy.uix.screenmanager import Screen
from kivy.app import App
from core.storage import save_data
from theme.colors import get_accent


class ProfilesScreen(Screen):

    current_tab = 0   # 0, 1, or 2

    def on_enter(self):
        self._load_tab(self.current_tab)
        self._apply_accent()

    def _apply_accent(self):
        app   = App.get_running_app()
        theme = get_accent(app.app_data.get('accent_theme', 'electric_blue'))
        self.ids.title_label.color    = theme['accent']
        self.ids.section_label.color  = theme['accent']
        for btn_id in ['tab_p1', 'tab_p2', 'tab_p3']:
            self.ids[btn_id].md_bg_color = [0.086, 0.094, 0.157, 1]
        active_tab_id = ['tab_p1', 'tab_p2', 'tab_p3'][self.current_tab]
        self.ids[active_tab_id].md_bg_color = self._hex_to_rgba(theme['accent'])

    def switch_tab(self, index: int):
        self._save_current_tab()
        self.current_tab = index
        self._load_tab(index)
        self._apply_accent()

    def _load_tab(self, index: int):
        app  = App.get_running_app()
        prof = app.app_data['profiles'][index]
        self.ids.profile_name_input.text = prof.get('name', '')
        self.ids.username_input.text     = prof.get('username', '')
        self.ids.password_input.text     = prof.get('password', '')

    def _save_current_tab(self):
        app  = App.get_running_app()
        prof = app.app_data['profiles'][self.current_tab]
        prof['name']     = self.ids.profile_name_input.text
        prof['username'] = self.ids.username_input.text
        prof['password'] = self.ids.password_input.text

    def on_save(self):
        self._save_current_tab()
        app = App.get_running_app()
        save_data(app.app_data)
        self.ids.save_feedback_label.text    = 'Saved!'
        self.ids.save_feedback_label.opacity = 1
        from kivy.animation import Animation
        Animation(opacity=0, duration=1.5, t='out_quad').start(
            self.ids.save_feedback_label
        )

    @staticmethod
    def _hex_to_rgba(hex_color: str) -> list:
        h = hex_color.lstrip('#')
        return [int(h[i:i+2], 16)/255 for i in (0, 2, 4)] + [1.0]
```

---

## PART 13 — screens/settings.py (COMPLETE SOURCE)

```python
# screens/settings.py
from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from core.storage import save_data
from theme.colors import get_accent, ACCENT_THEMES, DEFAULT_ACCENT


class SettingsScreen(Screen):

    _dialog = None

    def on_enter(self):
        self._apply_accent()
        self._load_toggles()

    def _apply_accent(self):
        app   = App.get_running_app()
        theme = get_accent(app.app_data.get('accent_theme', DEFAULT_ACCENT))
        self.ids.title_label.color           = theme['accent']
        self.ids.appearance_section.color    = theme['accent']
        self.ids.sysinfo_section.color       = theme['accent']
        self.ids.stable_badge.md_bg_color    = [0.13, 0.77, 0.37, 1]

    def _load_toggles(self):
        app = App.get_running_app()
        self.ids.auto_login_toggle.active = app.app_data.get('auto_login', False)

    # ── AUTO LOGIN TOGGLE ───────────────────────────────────────────────────

    def on_auto_login_toggle(self, value: bool):
        app = App.get_running_app()
        if value:
            if not app.app_data.get('auto_login_confirmed', False):
                self._show_auto_login_dialog()
                # Revert toggle visually until confirmed
                self.ids.auto_login_toggle.active = False
            else:
                app.app_data['auto_login'] = True
                save_data(app.app_data)
        else:
            app.app_data['auto_login'] = False
            save_data(app.app_data)

    def _show_auto_login_dialog(self):
        app = App.get_running_app()
        theme = get_accent(app.app_data.get('accent_theme', DEFAULT_ACCENT))
        if self._dialog:
            self._dialog.dismiss()
        self._dialog = MDDialog(
            title='Enable Auto Login?',
            text=(
                'ConnekTor will automatically try to connect to the campus '
                'portal whenever your phone joins a WiFi network, while this '
                'app is open.\n\nYour active profile credentials will be used.'
            ),
            buttons=[
                MDFlatButton(
                    text='CANCEL',
                    theme_text_color='Custom',
                    text_color=[0.557, 0.557, 0.627, 1],
                    on_release=lambda x: self._dialog.dismiss(),
                ),
                MDRaisedButton(
                    text='ENABLE',
                    md_bg_color=self._hex_to_rgba(theme['accent']),
                    on_release=lambda x: self._confirm_auto_login(),
                ),
            ],
        )
        self._dialog.open()

    def _confirm_auto_login(self):
        app = App.get_running_app()
        app.app_data['auto_login']           = True
        app.app_data['auto_login_confirmed'] = True
        save_data(app.app_data)
        self.ids.auto_login_toggle.active = True
        if self._dialog:
            self._dialog.dismiss()

    # ── ACCENT THEME PICKER ─────────────────────────────────────────────────

    def on_theme_select(self, theme_key: str):
        """Called when user taps a theme swatch button."""
        app = App.get_running_app()
        app.app_data['accent_theme'] = theme_key
        save_data(app.app_data)
        # Re-apply accent across all screens
        self._apply_accent()
        sm = App.get_running_app().sm
        for screen_name in ['home', 'profiles']:
            screen = sm.get_screen(screen_name)
            if hasattr(screen, '_apply_accent'):
                screen._apply_accent()

    @staticmethod
    def _hex_to_rgba(hex_color: str) -> list:
        h = hex_color.lstrip('#')
        return [int(h[i:i+2], 16)/255 for i in (0, 2, 4)] + [1.0]
```

---

## PART 14 — kv/home.kv

```kv
#:import dp kivy.metrics.dp
#:import get_color_from_hex kivy.utils.get_color_from_hex

<HomeScreen>:
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: get_color_from_hex('#0D0E1A')
            Rectangle:
                pos: self.pos
                size: self.size

        # ── TOP BAR ─────────────────────────────────────────────────────────
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(70)
            padding: [dp(24), dp(16), dp(16), 0]

            BoxLayout:
                orientation: 'vertical'
                MDLabel:
                    id: title_label
                    text: 'ConnekTor'
                    font_name: 'assets/fonts/Poppins-Bold.ttf'
                    font_size: '26sp'
                    bold: True
                    size_hint_y: None
                    height: dp(36)
                MDLabel:
                    text: 'College WiFi, automated.'
                    font_size: '13sp'
                    theme_text_color: 'Custom'
                    text_color: get_color_from_hex('#8E8EA0')
                    size_hint_y: None
                    height: dp(20)

        # ── STATUS BADGE ────────────────────────────────────────────────────
        BoxLayout:
            size_hint_y: None
            height: dp(44)
            padding: [0, dp(8), 0, 0]
            pos_hint: {'center_x': .5}

            MDBoxLayout:
                id: status_badge
                size_hint: (None, None)
                size: (dp(130), dp(32))
                pos_hint: {'center_x': .5}
                radius: [16, 16, 16, 16]
                md_bg_color: get_color_from_hex('#FF4757')

                MDLabel:
                    id: status_label
                    text: 'FAILED'
                    font_size: '12sp'
                    bold: True
                    halign: 'center'
                    theme_text_color: 'Custom'
                    text_color: 1, 1, 1, 1

        # ── CONNECT BUTTON ───────────────────────────────────────────────────
        Widget:
            size_hint_y: 0.06

        BoxLayout:
            size_hint_y: None
            height: dp(220)
            pos_hint: {'center_x': .5}

            MDFloatLayout:
                pos_hint: {'center_x': .5}

                # Glow ring — outer circle behind button
                MDBoxLayout:
                    id: connect_glow
                    size_hint: (None, None)
                    size: (dp(220), dp(220))
                    pos_hint: {'center_x': .5, 'center_y': .5}
                    radius: [110, 110, 110, 110]
                    md_bg_color: 0.36, 0.42, 0.96, 0.12

                # Button circle
                MDBoxLayout:
                    id: connect_btn
                    size_hint: (None, None)
                    size: (dp(190), dp(190))
                    pos_hint: {'center_x': .5, 'center_y': .5}
                    radius: [95, 95, 95, 95]
                    md_bg_color: get_color_from_hex('#FF6B6B')
                    on_touch_down:
                        if self.collide_point(*args[1].pos): root.on_connect_press()

                    MDBoxLayout:
                        orientation: 'vertical'
                        pos_hint: {'center_x': .5, 'center_y': .5}

                        MDIcon:
                            icon: 'wifi'
                            halign: 'center'
                            theme_text_color: 'Custom'
                            text_color: 1, 1, 1, 1
                            font_size: '44sp'

                        MDLabel:
                            text: 'CONNECT'
                            font_size: '15sp'
                            bold: True
                            halign: 'center'
                            theme_text_color: 'Custom'
                            text_color: 1, 1, 1, 1
                            size_hint_y: None
                            height: dp(22)

        Widget:
            size_hint_y: 1

        # ── ACTIVE PROFILE CARD ──────────────────────────────────────────────
        MDBoxLayout:
            size_hint_y: None
            height: dp(90)
            padding: [dp(20), 0, dp(20), dp(16)]

            MDBoxLayout:
                id: profile_card
                orientation: 'vertical'
                radius: [16, 16, 16, 16]
                md_bg_color: get_color_from_hex('#161829')
                padding: [dp(20), dp(12)]
                on_touch_down:
                    if self.collide_point(*args[1].pos): root.on_profile_card_tap()

                MDLabel:
                    text: 'ACTIVE PROFILE'
                    font_size: '10sp'
                    bold: True
                    theme_text_color: 'Custom'
                    text_color: get_color_from_hex('#8E8EA0')
                    size_hint_y: None
                    height: dp(16)

                MDLabel:
                    id: profile_name_label
                    text: 'Profile 1'
                    font_size: '17sp'
                    bold: True
                    size_hint_y: None
                    height: dp(26)

                MDLabel:
                    id: profile_index_label
                    text: '1 / 3 — tap to switch'
                    font_size: '12sp'
                    theme_text_color: 'Custom'
                    text_color: get_color_from_hex('#8E8EA0')
                    size_hint_y: None
                    height: dp(18)

        # ── BOTTOM NAV ───────────────────────────────────────────────────────
        BoxLayout:
            size_hint_y: None
            height: dp(62)
            canvas.before:
                Color:
                    rgba: get_color_from_hex('#111220')
                Rectangle:
                    pos: self.pos
                    size: self.size

            MDIconButton:
                icon: 'home'
                theme_text_color: 'Custom'
                text_color: get_color_from_hex('#5B6BF5')
                on_release: app.sm.current = 'home'

            MDIconButton:
                icon: 'account'
                theme_text_color: 'Custom'
                text_color: get_color_from_hex('#8E8EA0')
                on_release: app.sm.current = 'profiles'

            MDIconButton:
                icon: 'cog'
                theme_text_color: 'Custom'
                text_color: get_color_from_hex('#8E8EA0')
                on_release: app.sm.current = 'settings'
```

---

## PART 15 — kv/profiles.kv

```kv
#:import dp kivy.metrics.dp
#:import get_color_from_hex kivy.utils.get_color_from_hex

<ProfilesScreen>:
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: get_color_from_hex('#0D0E1A')
            Rectangle:
                pos: self.pos
                size: self.size

        BoxLayout:
            size_hint_y: None
            height: dp(70)
            padding: [dp(24), dp(16), 0, 0]
            orientation: 'vertical'

            MDLabel:
                id: title_label
                text: 'Profiles'
                font_name: 'assets/fonts/Poppins-Bold.ttf'
                font_size: '26sp'
                bold: True
                size_hint_y: None
                height: dp(36)

            MDLabel:
                id: section_label
                text: 'Configure your login credentials'
                font_size: '13sp'
                theme_text_color: 'Custom'
                text_color: get_color_from_hex('#8E8EA0')
                size_hint_y: None
                height: dp(20)

        # ── TAB ROW ──────────────────────────────────────────────────────────
        BoxLayout:
            size_hint_y: None
            height: dp(48)
            padding: [dp(20), dp(8)]
            spacing: dp(10)

            MDRaisedButton:
                id: tab_p1
                text: 'P1'
                size_hint_x: 1
                on_release: root.switch_tab(0)

            MDRaisedButton:
                id: tab_p2
                text: 'P2'
                size_hint_x: 1
                on_release: root.switch_tab(1)

            MDRaisedButton:
                id: tab_p3
                text: 'P3'
                size_hint_x: 1
                on_release: root.switch_tab(2)

        # ── PROFILE FORM CARD ────────────────────────────────────────────────
        MDBoxLayout:
            orientation: 'vertical'
            radius: [16, 16, 16, 16]
            md_bg_color: get_color_from_hex('#161829')
            padding: [dp(20), dp(16)]
            spacing: dp(12)
            size_hint_y: None
            height: dp(320)
            pos_hint: {'center_x': .5}
            size_hint_x: 0.92

            MDLabel:
                text: 'PROFILE NAME'
                font_size: '11sp'
                bold: True
                theme_text_color: 'Custom'
                text_color: get_color_from_hex('#8E8EA0')
                size_hint_y: None
                height: dp(16)

            MDTextField:
                id: profile_name_input
                hint_text: 'e.g. My Profile'
                mode: 'rectangle'
                font_size: '14sp'

            MDLabel:
                text: 'USERNAME'
                font_size: '11sp'
                bold: True
                theme_text_color: 'Custom'
                text_color: get_color_from_hex('#8E8EA0')
                size_hint_y: None
                height: dp(16)

            MDTextField:
                id: username_input
                hint_text: 'e.g. 080bel042'
                mode: 'rectangle'
                font_size: '14sp'

            MDLabel:
                text: 'PASSWORD'
                font_size: '11sp'
                bold: True
                theme_text_color: 'Custom'
                text_color: get_color_from_hex('#8E8EA0')
                size_hint_y: None
                height: dp(16)

            MDTextField:
                id: password_input
                hint_text: 'Your password'
                password: True
                mode: 'rectangle'
                font_size: '14sp'

            MDRaisedButton:
                text: 'Save Changes'
                size_hint_x: 1
                on_release: root.on_save()

            MDLabel:
                id: save_feedback_label
                text: ''
                opacity: 0
                halign: 'center'
                theme_text_color: 'Custom'
                text_color: get_color_from_hex('#2ED573')
                size_hint_y: None
                height: dp(20)

        Widget:
            size_hint_y: 1

        # ── BOTTOM NAV ───────────────────────────────────────────────────────
        BoxLayout:
            size_hint_y: None
            height: dp(62)
            canvas.before:
                Color:
                    rgba: get_color_from_hex('#111220')
                Rectangle:
                    pos: self.pos
                    size: self.size

            MDIconButton:
                icon: 'home'
                theme_text_color: 'Custom'
                text_color: get_color_from_hex('#8E8EA0')
                on_release: app.sm.current = 'home'

            MDIconButton:
                icon: 'account'
                theme_text_color: 'Custom'
                text_color: get_color_from_hex('#5B6BF5')
                on_release: app.sm.current = 'profiles'

            MDIconButton:
                icon: 'cog'
                theme_text_color: 'Custom'
                text_color: get_color_from_hex('#8E8EA0')
                on_release: app.sm.current = 'settings'
```

---

## PART 16 — kv/settings.kv

```kv
#:import dp kivy.metrics.dp
#:import get_color_from_hex kivy.utils.get_color_from_hex

<SettingsScreen>:
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: get_color_from_hex('#0D0E1A')
            Rectangle:
                pos: self.pos
                size: self.size

        BoxLayout:
            size_hint_y: None
            height: dp(70)
            padding: [dp(24), dp(16), 0, 0]
            orientation: 'vertical'

            MDLabel:
                id: title_label
                text: 'Settings'
                font_name: 'assets/fonts/Poppins-Bold.ttf'
                font_size: '26sp'
                bold: True
                size_hint_y: None
                height: dp(36)

            MDLabel:
                text: 'Manage your preferences'
                font_size: '13sp'
                theme_text_color: 'Custom'
                text_color: get_color_from_hex('#8E8EA0')
                size_hint_y: None
                height: dp(20)

        ScrollView:
            BoxLayout:
                orientation: 'vertical'
                spacing: dp(12)
                padding: [dp(16), dp(12)]
                size_hint_y: None
                height: self.minimum_height

                # ── SECTION: APPEARANCE ──────────────────────────────────────
                MDLabel:
                    id: appearance_section
                    text: 'APPEARANCE & BEHAVIOR'
                    font_size: '11sp'
                    bold: True
                    size_hint_y: None
                    height: dp(24)

                # Appearance card
                MDBoxLayout:
                    orientation: 'vertical'
                    radius: [16, 16, 16, 16]
                    md_bg_color: get_color_from_hex('#161829')
                    padding: [dp(20), dp(16)]
                    spacing: dp(16)
                    size_hint_y: None
                    height: dp(80)

                    BoxLayout:
                        size_hint_y: None
                        height: dp(48)
                        spacing: dp(12)

                        MDIcon:
                            icon: 'flash'
                            theme_text_color: 'Custom'
                            text_color: get_color_from_hex('#8E8EA0')
                            size_hint_x: None
                            width: dp(28)

                        BoxLayout:
                            orientation: 'vertical'

                            MDLabel:
                                text: 'Auto Login'
                                font_size: '15sp'
                                bold: True
                                size_hint_y: None
                                height: dp(22)

                            MDLabel:
                                text: 'Connect when WiFi is available'
                                font_size: '12sp'
                                theme_text_color: 'Custom'
                                text_color: get_color_from_hex('#8E8EA0')
                                size_hint_y: None
                                height: dp(18)

                        MDSwitch:
                            id: auto_login_toggle
                            pos_hint: {'center_y': .5}
                            on_active: root.on_auto_login_toggle(self.active)

                # ── SECTION: COLOR THEME ─────────────────────────────────────
                MDLabel:
                    text: 'ACCENT COLOR'
                    font_size: '11sp'
                    bold: True
                    theme_text_color: 'Custom'
                    text_color: get_color_from_hex('#5B6BF5')
                    size_hint_y: None
                    height: dp(24)

                MDBoxLayout:
                    orientation: 'vertical'
                    radius: [16, 16, 16, 16]
                    md_bg_color: get_color_from_hex('#161829')
                    padding: [dp(20), dp(16)]
                    spacing: dp(12)
                    size_hint_y: None
                    height: dp(270)

                    MDLabel:
                        text: 'Choose your accent color. Dark background is always kept.'
                        font_size: '12sp'
                        theme_text_color: 'Custom'
                        text_color: get_color_from_hex('#8E8EA0')
                        size_hint_y: None
                        height: dp(36)

                    # Row 1: 4 swatches
                    BoxLayout:
                        size_hint_y: None
                        height: dp(52)
                        spacing: dp(10)

                        MDRaisedButton:
                            text: 'Blue'
                            md_bg_color: get_color_from_hex('#5B6BF5')
                            on_release: root.on_theme_select('electric_blue')

                        MDRaisedButton:
                            text: 'Violet'
                            md_bg_color: get_color_from_hex('#A855F7')
                            on_release: root.on_theme_select('cyber_violet')

                        MDRaisedButton:
                            text: 'Green'
                            md_bg_color: get_color_from_hex('#22C55E')
                            on_release: root.on_theme_select('neon_green')

                        MDRaisedButton:
                            text: 'Pink'
                            md_bg_color: get_color_from_hex('#EC4899')
                            on_release: root.on_theme_select('hot_pink')

                    # Row 2: 3 swatches
                    BoxLayout:
                        size_hint_y: None
                        height: dp(52)
                        spacing: dp(10)

                        MDRaisedButton:
                            text: 'Orange'
                            md_bg_color: get_color_from_hex('#F97316')
                            on_release: root.on_theme_select('solar_orange')

                        MDRaisedButton:
                            text: 'Cyan'
                            md_bg_color: get_color_from_hex('#06B6D4')
                            on_release: root.on_theme_select('ice_cyan')

                        MDRaisedButton:
                            text: 'Gold'
                            md_bg_color: get_color_from_hex('#EAB308')
                            on_release: root.on_theme_select('gold')

                    MDLabel:
                        text: 'Current theme updates all screens instantly.'
                        font_size: '11sp'
                        theme_text_color: 'Custom'
                        text_color: get_color_from_hex('#8E8EA0')
                        size_hint_y: None
                        height: dp(20)

                # ── SECTION: SYSTEM INFO ─────────────────────────────────────
                MDLabel:
                    id: sysinfo_section
                    text: 'SYSTEM INFO'
                    font_size: '11sp'
                    bold: True
                    size_hint_y: None
                    height: dp(24)

                MDBoxLayout:
                    orientation: 'vertical'
                    radius: [16, 16, 16, 16]
                    md_bg_color: get_color_from_hex('#161829')
                    padding: [dp(20), dp(16)]
                    spacing: dp(8)
                    size_hint_y: None
                    height: dp(120)

                    BoxLayout:
                        size_hint_y: None
                        height: dp(40)
                        spacing: dp(12)

                        MDIcon:
                            icon: 'shield-check'
                            theme_text_color: 'Custom'
                            text_color: get_color_from_hex('#8E8EA0')
                            size_hint_x: None
                            width: dp(28)

                        MDLabel:
                            text: 'Version\n4.0.0 Elite Build'
                            font_size: '13sp'

                        MDBoxLayout:
                            id: stable_badge
                            size_hint: (None, None)
                            size: (dp(70), dp(26))
                            radius: [8, 8, 8, 8]
                            pos_hint: {'center_y': .5}

                            MDLabel:
                                text: 'STABLE'
                                font_size: '11sp'
                                bold: True
                                halign: 'center'
                                theme_text_color: 'Custom'
                                text_color: 1, 1, 1, 1

                    BoxLayout:
                        size_hint_y: None
                        height: dp(30)
                        spacing: dp(12)

                        MDIcon:
                            icon: 'information-outline'
                            theme_text_color: 'Custom'
                            text_color: get_color_from_hex('#8E8EA0')
                            size_hint_x: None
                            width: dp(28)

                        MDLabel:
                            text: 'Made by Anup Aryal'
                            font_size: '13sp'

        # ── BOTTOM NAV ───────────────────────────────────────────────────────
        BoxLayout:
            size_hint_y: None
            height: dp(62)
            canvas.before:
                Color:
                    rgba: get_color_from_hex('#111220')
                Rectangle:
                    pos: self.pos
                    size: self.size

            MDIconButton:
                icon: 'home'
                theme_text_color: 'Custom'
                text_color: get_color_from_hex('#8E8EA0')
                on_release: app.sm.current = 'home'

            MDIconButton:
                icon: 'account'
                theme_text_color: 'Custom'
                text_color: get_color_from_hex('#8E8EA0')
                on_release: app.sm.current = 'profiles'

            MDIconButton:
                icon: 'cog'
                theme_text_color: 'Custom'
                text_color: get_color_from_hex('#5B6BF5')
                on_release: app.sm.current = 'settings'
```

---

## PART 17 — FINAL CHECKLIST BEFORE PUSHING TO GITHUB

```
REPOSITORY
[ ] All files listed in PART 1 exist at correct paths
[ ] All __init__.py files exist (even if empty)
[ ] assets/fonts/Poppins-Bold.ttf present (download from Google Fonts if needed)
[ ] assets/icon.png present (512x512, dark navy background)
[ ] .github/workflows/build.yml present

VERSIONS (double-check buildozer.spec requirements line)
[ ] python3==3.11.0
[ ] kivy==2.3.0
[ ] kivymd==1.1.1
[ ] urllib3==1.26.18  ← critical, not 2.x
[ ] cython==0.29.37 set in GitHub Actions pip install, NOT in buildozer.spec

BUILD SYSTEM
[ ] ubuntu-22.04 in build.yml (not ubuntu-latest)
[ ] java-version: '17' in build.yml
[ ] python-version: '3.11' in build.yml
[ ] buildozer==1.5.0 in pip install step

LOGIN LOGIC (core/login.py)
[ ] POST URL: https://10.100.1.1:8090/login.xml
[ ] payload keys: mode='191', username, password, a=timestamp_ms, producttype='your_producttype'
[ ] Manual URL-encoding with requests.utils.quote() + '&'.join()
[ ] verify=False
[ ] timeout=10
[ ] Success check: 'You are signed in as' in response.text
[ ] All network code in daemon thread
[ ] All UI updates via Clock.schedule_once

THREADING
[ ] Every threading.Thread has daemon=True
[ ] Zero direct widget property access from outside main thread
[ ] urllib3 warnings suppressed at top of main.py AND core/login.py

PLATFORM GUARD
[ ] Window.size set only when platform != 'android'

STORAGE
[ ] Passwords base64-encoded on write, decoded on read
[ ] app_data.json includes accent_theme key
[ ] auto_login defaults to False

THEME SYSTEM
[ ] 7 accent themes defined in theme/colors.py
[ ] All 3 screens call _apply_accent() in on_enter()
[ ] Changing theme in Settings immediately updates all screens
[ ] Background color never changes (always #0D0E1A)

AUTO-LOGIN
[ ] WiFiMonitor starts in main.py on_start / build()
[ ] Probe uses http://captive.apple.com (plain HTTP)
[ ] Checks for 10.100.1.1 in response URL or body
[ ] 30-second cooldown between attempts
[ ] Confirmation dialog shown on first enable
[ ] auto_login_confirmed persists so dialog doesn't repeat
[ ] Toggle off stops probing immediately (reads flag live)
```

---

*End of document. Build from this. Reference nothing else.*
