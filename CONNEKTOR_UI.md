# ConnekTor v4 — CYBER-MINIMALIST UI COMPLETE REBUILD + CRASH FIX
### Feed this entire file to Antigravity. This replaces ALL kv/ files, ALL screens/*.py files, and main.py. DO NOT touch anything inside core/.

---

## SECTION 0 — THE TWO PROBLEMS YOU ARE FIXING

### PROBLEM 1 — APP CRASHES ON CONNECT BUTTON PRESS
**Root cause:** The `result_callback` passed into `perform_login()` directly
touches Kivy widget properties from inside a background `threading.Thread`.
Kivy's rendering engine is not thread-safe. Any widget property write from
outside the main thread causes an immediate silent crash (SIGSEGV or
`CalledFromWrongThreadException` depending on Android version).

**The fix — apply this pattern in `screens/home.py` without fail:**
```python
# WRONG — crashes Android:
def my_callback(status, message):
    self.ids.some_label.text = message   # <-- direct widget write from thread

# CORRECT — always wrap with Clock.schedule_once:
def my_callback(status, message):
    Clock.schedule_once(lambda dt: self._apply_result(status, message), 0)

def _apply_result(self, status, message):
    self.ids.some_label.text = message   # safe — now on main thread
```

**Every single widget update triggered from a callback must go through
`Clock.schedule_once`. No exceptions. This includes:**
- Setting label text
- Setting label color
- Setting button background color
- Starting or stopping animations
- Changing widget opacity
- Any `self.ids.*` access whatsoever

### PROBLEM 2 — UGLY UI (painting colors over old layout instead of rebuilding)
The previous attempt kept the original KV layout structure and only changed
colors. The result was the original boxy Kivy layout with cyan paint on it.

**You must DELETE and REWRITE every `.kv` file from scratch.**
Do not modify existing KV. Delete it. Write new KV that matches the HTML
reference in Section 3. The structure, widget hierarchy, spacing philosophy,
and component shapes are all completely different from what exists.

---

## SECTION 1 — WHAT YOU MUST NEVER TOUCH

```
core/__init__.py        — DO NOT TOUCH
core/login.py           — DO NOT TOUCH. The login logic is verified working.
core/storage.py         — DO NOT TOUCH
core/wifi_monitor.py    — DO NOT TOUCH
buildozer.spec          — DO NOT TOUCH
.github/workflows/      — DO NOT TOUCH
requirements.txt        — DO NOT TOUCH
```

The ONLY files you are rewriting are:
```
main.py
theme/colors.py
screens/home.py
screens/profiles.py
screens/settings.py
kv/home.kv
kv/profiles.kv
kv/settings.kv
```

---

## SECTION 2 — DESIGN SYSTEM (from official Stitch design tokens)

This is the exact design system. Every color, radius, and spacing value below
came from the official project design tokens. Use these values — do not invent
your own.

### Color Palette
```
Background (deepest):    #0F0F0F   ← app root background
Surface base:            #131313   ← screen background
Card / glass surface:    #1A1A1A   ← all cards (80% opacity)
Card elevated:           #201f1f   ← slightly raised surfaces
Card border:             rgba(255,255,255,0.08)  ← subtle white border on cards
Nav bar:                 #1c1b1b   ← bottom nav background (80% opacity)

Primary (Electric Cyan): #00f0ff   ← ALL primary actions, glows, active states
Primary text/soft:       #dbfcff   ← primary text on dark (slightly softer)
Primary glow rgba:       rgba(0, 240, 255, 0.4)   ← standard glow
Primary glow intense:    rgba(0, 240, 255, 0.8)   ← pulse peak glow

Secondary (Violet):      #7000ff   ← secondary accents, gradients with cyan
Secondary soft:          #d1bcff   ← secondary text

Text primary:            #e5e2e1   ← all body/headline text
Text muted:              #b9cacb   ← subtitles, hints, labels
Text ultra-muted:        rgba(255,255,255,0.30)  ← placeholder text

Success:                 #00d18b   ← CONNECTED state (neon green)
Error:                   #ff4d4d   ← FAILED/ERROR state (neon red)
Warning/Amber:           #fed639   ← tertiary / warning state

Outline:                 #849495   ← inactive icon color
Outline variant:         #3b494b   ← subtle dividers
```

### Typography
Font: **Poppins-Bold.ttf** for headlines (already in assets/fonts/).
Font: **Poppins-Regular.ttf** for body (already in assets/fonts/).
There is no Geist font in Kivy — use Poppins as the direct substitute.
Poppins matches Geist's geometric precision and technical feel.

```
Display / App title:   Poppins-Bold, 28sp, letter_spacing=-0.5, color=#00f0ff
                       with canvas glow effect (text_shadow equivalent)
Screen title:          Poppins-Bold, 26sp, color=#e5e2e1
Section label (caps):  Poppins-Regular, 11sp, uppercase, letter_spacing=2,
                       color=#b9cacb, opacity=0.7
Card title:            Poppins-Bold, 18sp, color=#e5e2e1
Body text:             Poppins-Regular, 14sp, color=#e5e2e1
Hint / placeholder:    Poppins-Regular, 13sp, color=rgba(255,255,255,0.30)
```

### Spacing
```
Screen horizontal padding:  dp(20) on both sides
Card internal padding:       dp(20) top/bottom, dp(20) left/right
Card corner radius:          dp(24)  ← rounded-lg from design system
Button corner radius:        dp(999) ← fully pill-shaped (rounded-full)
Tab bar corner radius:        dp(16)
Input field corner radius:   dp(16)
Gap between cards:           dp(20)
```

### Elevation / Depth (Kivy implementation)
Kivy has no CSS box-shadow. Simulate depth using:
1. **Glow rings** — draw a slightly larger rounded rectangle behind a button
   using Canvas, filled with the glow color at low opacity (~0.12-0.15)
2. **Card borders** — 1px border in `rgba(255,255,255,0.08)` drawn via Canvas
3. **Pulse animation** — `Animation(opacity=0.6) + Animation(opacity=1.0)`
   on the glow ring widget behind the CONNECT button, repeating

---

## SECTION 3 — SCREEN-BY-SCREEN PIXEL SPEC

Study the HTML reference files alongside these specs. The HTML files are the
exact visual target. Translate them into Kivy KV layout.

---

### SCREEN A: HOME (kv/home.kv + screens/home.py)

**Reference:** `1779382591662_code.html`

#### Top App Bar (fixed, height dp(72))
```
Background: #131313 at 90% opacity (simulate with canvas)
Bottom border: 1px, rgba(255,255,255,0.08)

LEFT side:
  MDIconButton — icon: 'web' or 'language' equivalent
  color: #00f0ff

CENTER:
  MDLabel — text: 'CONNEKTOR'
  font_name: Poppins-Bold.ttf
  font_size: 22sp
  bold: True
  color: #00f0ff
  halign: center
  (add canvas glow behind text: rounded rect, color rgba(0,240,255,0.08),
   height dp(32), same width as text, radius dp(8))

RIGHT side:
  MDIconButton — icon: 'signal-cellular-3' or 'wifi'
  color: #00f0ff
```

#### CONNECT Button (CENTER of screen, most important element)
```
This is a CIRCLE, NOT a rounded square like the previous version.
The screenshots show a rounded square which is WRONG.
Correct shape from HTML: w-64 h-64 rounded-full = fully circular

Implementation in KV:
  Widget container: size dp(220) x dp(220)

  Layer 1 — Outer glow ring (canvas):
    Ellipse drawn slightly larger than button (dp(240) x dp(240))
    Color: rgba(0, 240, 255, 0.12)
    This layer pulses via Animation in home.py

  Layer 2 — Button body:
    MDBoxLayout, size dp(200) x dp(200)
    radius: [100, 100, 100, 100]  ← full circle
    md_bg_color: #201f1f
    border: canvas rectangle, 2px, rgba(0,240,255,0.25), same radius

  Layer 3 — Inner ring accent:
    Canvas ellipse inside button, radius dp(88), color rgba(0,240,255,0.06)

  Layer 4 — Icon:
    MDIcon, icon: 'web' (globe — matches HTML 'language' icon)
    font_size: 44sp
    color: #00f0ff
    halign: center

  Layer 5 — Label:
    MDLabel text: 'CONNECT'
    font_name: Poppins-Bold.ttf
    font_size: 20sp
    color: #00f0ff
    halign: center

  Touch behavior:
    on_touch_down + collide_point → calls root.on_connect_press()
    On press: scale animation 1.0 → 0.94 (active:scale-90 from HTML)
    While connecting: outer glow ring opacity pulses 0.12 → 0.45 → 0.12 (3s loop)
    On connected: border color changes to #00d18b, icon changes to 'lock'
    On failed: border color changes to #ff4d4d
```

#### Status Chip (below connect button, above profile card)
```
Pill-shaped badge — radius dp(999)
Default (idle):    background rgba(0,240,255,0.08),  border 1px #00f0ff,
                   text: 'SECURED', color: #00f0ff
Connecting:        background rgba(254,214,57,0.08), border 1px #fed639,
                   text: 'CONNECTING...', color: #fed639
Connected:         background rgba(0,209,139,0.08),  border 1px #00d18b,
                   text: 'CONNECTED', color: #00d18b
Failed:            background rgba(255,77,77,0.08),  border 1px #ff4d4d,
                   text: 'FAILED', color: #ff4d4d

Font: Poppins-Bold, 11sp, uppercase, letter_spacing=1.5
Padding: dp(10) horizontal, dp(5) vertical
```

#### Active Profile Card (bottom of screen, above nav)
```
Glass card style:
  md_bg_color: rgba(26,26,26,0.85)
  radius: dp(24)
  border: canvas 1px rgba(255,255,255,0.08)
  padding: dp(16) all sides

Layout: horizontal
  LEFT:
    Green pulse dot — canvas Ellipse dp(8)x dp(8), color #00f0ff
    animate opacity 1→0.3→1, duration 1.2s, repeat

  CENTER (vertical stack):
    Label: 'ACTIVE PROFILE' — 10sp, uppercase, letter_spacing=2, color #b9cacb
    Label: profile name — 16sp, Poppins-Bold, color #e5e2e1  [id: profile_name_label]

  RIGHT:
    MDIcon: 'chevron-right', color #b9cacb, size 20sp

  Tap gesture: calls root.on_profile_card_tap() → cycles profile 0→1→2→0
```

#### Bottom Navigation Bar
```
Height: dp(72)
Background: #1c1b1b at 80% opacity
Top border: 1px rgba(255,255,255,0.08)
Top shadow glow line: canvas Line, color rgba(0,240,255,0.10), width 1px

Three tabs: HOME (active), PROFILES, SETTINGS

ACTIVE tab style (HOME on this screen):
  Background: rgba(0,240,255,0.08), radius dp(14)
  Icon color: #00f0ff
  Icon style: filled (use MDIcon with the right icon name)
  Label color: #00f0ff
  Drop glow below icon: canvas Ellipse dp(4)xdp(4) color #00f0ff at opacity 0.9

INACTIVE tab style:
  No background
  Icon color: #849495
  Label color: #849495

Tab icons:
  Home:     'home' (filled when active)
  Profiles: 'router' (matches HTML — use 'access-point-network' in KivyMD
             or 'web' as fallback)
  Settings: 'cog' or 'settings'

Tab labels: 10sp, Poppins-Bold, uppercase
```

---

### SCREEN B: PROFILES (kv/profiles.kv + screens/profiles.py)

**Reference:** `1779382603565_code.html`

#### Top App Bar
Identical to Home screen bar. Title: 'CONNEKTOR' centered in cyan.

#### Profile Tab Selector (below app bar, above form)
```
Container:
  Background: rgba(32,31,31,0.4)
  radius: dp(18)
  border: 1px rgba(255,255,255,0.05)
  padding: dp(6) all sides
  Height: dp(56)

Three buttons inside (P1, P2, P3):
  Each: flex-1 (equal width), height fills container

  ACTIVE tab:
    Background: rgba(0,240,255,0.10)
    border: 1px solid #00f0ff
    text color: #00f0ff
    glow: canvas rounded rect behind, color rgba(0,240,255,0.08)
    radius: dp(12)
    font: Poppins-Bold, 12sp, uppercase, letter_spacing=1

  INACTIVE tab:
    Background: transparent
    text color: #849495
    font: Poppins-Bold, 12sp, uppercase

  Switching tabs: calls root.switch_tab(index)
```

#### Main Profile Form Card (glass card)
```
Background: rgba(26,26,26,0.85)
radius: dp(24)
border: canvas 1px rgba(255,255,255,0.08)
padding: dp(20) all sides
Spacing between fields: dp(20)

Decorative accent (top-right corner):
  Canvas Ellipse: size dp(100)xdp(100), pos top-right offset,
  color rgba(0,240,255,0.06), blur_radius dp(40)
  (simulate with a semi-transparent MDBoxLayout with border_radius dp(50))

FIELD 1 — STUDENT IDENTIFICATION:
  Label: 'STUDENT IDENTIFICATION' — 10sp, uppercase, letter_spacing=2,
         color rgba(185,202,203,0.6)
  Input row (dark card within card):
    Background: #1c1b1b
    radius: dp(16)
    border: 1px rgba(255,255,255,0.05)
    On focus: border becomes 1px #00f0ff + inner glow canvas
    padding: dp(16) horizontal, dp(14) vertical
    Left icon: MDIcon 'badge' or 'account', color #849495,
               on focus → color #00f0ff
    MDTextField: id=username_input, mode='fill' or custom canvas style
                 background_color=[0,0,0,0] (transparent — let card show)
                 foreground_color=#e5e2e1
                 hint_text='e.g. 080bel042'
                 hint_text_color rgba(255,255,255,0.30)
                 font_name Poppins-Regular.ttf
                 font_size 16sp

FIELD 2 — SECURE ACCESS TOKEN:
  Label: 'SECURE ACCESS TOKEN' — same style as above
  Input row: same dark card style as above
    Left icon: MDIcon 'lock', color #849495
    MDTextField: id=password_input, password=True
                 hint_text='Quantum Password'
                 same styling as username
    Right side: small MDRaisedButton or MDTextButton
                text: 'REVEAL', font_size 10sp
                md_bg_color rgba(0,240,255,0.08)
                text_color #00f0ff
                on_release: toggles password=True/False on password_input

PROFILE NAME FIELD (above the two fields above, or as first field):
  Label: 'PROFILE NAME' — same label style
  MDTextField: id=profile_name_input, hint_text='e.g. My Profile'
               same dark card styling

SAVE BUTTON:
  Full-width, height dp(54)
  radius: dp(999) ← fully pill-shaped
  background: #00f0ff
  text color: #00363a (dark teal — high contrast on cyan bg)
  text: 'SAVE CHANGES' — Poppins-Bold, 14sp, uppercase, letter_spacing=1
  glow: canvas rounded rect behind button, color rgba(0,240,255,0.30),
        blur approximated by a slightly larger rounded rect at low opacity
  on_release: calls root.on_save()
  on press: scale animation to 0.97

Save feedback: MDLabel id=save_feedback_label
  text: '' initially, shows 'Saved ✓' in #00d18b for 1.5s then fades
```

#### Bottom Bento Stats Cards (decorative, below form)
```
Two equal-width glass cards side by side:
  Card 1:
    Left border accent: 3px solid #00f0ff (canvas Line on left edge)
    Label: 'UPTIME' — 10sp uppercase muted
    Value: '99.9%' — 18sp Poppins-Bold white
    Icon: MDIcon 'wifi' — 16sp #00f0ff

  Card 2:
    Left border accent: 3px solid #7000ff
    Label: 'NODES' — 10sp uppercase muted
    Value: '14 Active' — 18sp Poppins-Bold white
    Icon: MDIcon 'access-point' — 16sp #7000ff

These are DECORATIVE ONLY — no functional logic needed.
```

#### Bottom Nav
Identical structure to Home. PROFILES tab is active on this screen.

---

### SCREEN C: SETTINGS (kv/settings.kv + screens/settings.py)

**Reference:** `1779382582521_code.html`

#### Top App Bar
Identical structure. Title: 'CONNEKTOR'.

#### Screen Header Section
```
Below app bar, padding dp(20):
  Label: 'Settings' — Poppins-Bold, 26sp, color #e5e2e1
  Label: 'Configure your network experience' — 13sp, color #b9cacb
```

#### AUTO CONNECT Section
```
Section label: 'AUTO CONNECT' — 11sp, uppercase, letter_spacing=2,
               color #00f0ff (accent color)

Glass card (full width):
  background rgba(26,26,26,0.85), radius dp(24),
  border 1px rgba(255,255,255,0.08)
  padding dp(20)

  Layout: horizontal, vertically centered

  LEFT — Icon container:
    MDBoxLayout: size dp(48)xdp(48), radius dp(999) (circle)
    background rgba(0,240,255,0.08)
    border 1px rgba(0,240,255,0.15)
    MDIcon inside: 'flash' or 'bolt', color #00f0ff, size 22sp

  CENTER — Text block:
    Label: 'Auto Connect' — Poppins-Bold, 16sp, color #e5e2e1
    Label: 'Instantly pair with trusted hubs' — 13sp, color #b9cacb

  RIGHT — Custom Toggle Switch:
    DO NOT use MDSwitch — it renders inconsistently.
    Build a custom toggle using pure Canvas:

    TOGGLE IMPLEMENTATION (critical — do this exactly):
    ```python
    # In settings.py:
    class ToggleSwitch(Widget):
        active = BooleanProperty(False)

        def on_touch_down(self, touch):
            if self.collide_point(*touch.pos):
                self.active = not self.active
                self._animate()
                root_app = App.get_running_app()
                root_app.app_data['auto_login'] = self.active
                from core.storage import save_data
                save_data(root_app.app_data)
                return True

        def _animate(self):
            # Animate knob position left↔right
            knob = self.ids.knob
            if self.active:
                Animation(x=self.x + self.width - dp(28), duration=0.25,
                          t='out_cubic').start(knob)
            else:
                Animation(x=self.x + dp(4), duration=0.25,
                          t='out_cubic').start(knob)
    ```

    KV for custom toggle:
    ```kv
    <ToggleSwitch>:
        size_hint: None, None
        size: dp(54), dp(30)
        canvas:
            # Track
            Color:
                rgba: (0, 240/255, 255/255, 0.12) if self.active else (0.1, 0.1, 0.1, 1)
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [dp(15)]
            # Track border
            Color:
                rgba: (0, 240/255, 255/255, 0.8) if self.active else (1,1,1,0.1)
            Line:
                rounded_rectangle: [self.x, self.y, self.width, self.height, dp(15)]
                width: 1.2
        # Knob drawn as child widget in Python
    ```
```

#### THEME SELECTOR Section
```
Section label: 'THEME SELECTOR' — same label style, color #00f0ff

Glass card — same card styling as above
padding dp(20), spacing dp(16)

  Row 1 — section title row:
    MDIcon: 'palette', color #00f0ff, size 20sp
    Label: 'Theme Selector' — Poppins-Bold, 16sp, color #e5e2e1

  Row 2 — description:
    Label: 'Choose your accent color. Dark Obsidian is always kept.'
    13sp, color #b9cacb

  Row 3 — Color swatches (GRID 4 columns):
    Each swatch is a touchable square with rounded corners (radius dp(12))
    Size: (screen_width - dp(40) - dp(20)*3) / 4 per swatch
    Arrangement: 2 rows of 4 swatches

    8 SWATCHES (exact colors from HTML):
      Cyan:    #00f0ff  ← default active (key: 'cyan')
      Violet:  #7000ff  (key: 'violet')
      Amber:   #fed639  (key: 'amber')
      Emerald: #00d18b  (key: 'emerald')
      Crimson: #ff4d4d  (key: 'crimson')
      Indigo:  #3f51b5  (key: 'indigo')
      Rose:    #e91e63  (key: 'rose')
      Slate:   #3b494b  (key: 'slate')

    ACTIVE swatch:
      Border: 2px solid #00f0ff (or the active color itself)
      Extra glow canvas behind: rgba(0,240,255,0.20), radius dp(14)

    INACTIVE swatch:
      No border (or 1px rgba(255,255,255,0.05))

    Each swatch tap: calls root.on_theme_select(key)

  Row 4 — current theme label:
    'Current theme: Quantum Link Secured'
    (update text when theme changes: use a dict mapping key → display name)
    13sp, color #b9cacb

    Theme display names:
      'cyan':    'Quantum Link Secured'
      'violet':  'Neon Violet Protocol'
      'amber':   'Solar Flare Mode'
      'emerald': 'Ghost Network'
      'crimson': 'Red Alert Mode'
      'indigo':  'Deep Space Mode'
      'rose':    'Quantum Rose'
      'slate':   'Stealth Mode'
```

#### SYSTEM INFO Section
```
Glass card:
  Row 1:
    MDIcon: 'shield-check', color #00f0ff (or 'shield' if not available)
    Label: 'Quantum V4.0.0 Stable' — 15sp Poppins-Bold, color #e5e2e1
    (No separate STABLE badge — integrate into label text)

  Divider: 1px rgba(255,255,255,0.05), full width

  Row 2:
    MDIcon: 'information-outline', color #849495
    Label: 'Made by Anup Aryal' — 14sp, color #e5e2e1
```

#### Bottom Nav
Identical. SETTINGS tab active on this screen.

---

## SECTION 4 — THEME SYSTEM REBUILD

The 8 swatches replace the 7 themes from the old `theme/colors.py`.
Rewrite `theme/colors.py` completely:

```python
# theme/colors.py

BG_ROOT    = [0.059, 0.059, 0.059, 1]     # #0F0F0F
BG_SURFACE = [0.075, 0.075, 0.075, 1]     # #131313
BG_CARD    = [0.102, 0.102, 0.102, 0.85]  # #1A1A1A 85%
BG_NAV     = [0.110, 0.106, 0.106, 0.85]  # #1c1b1b 85%
BG_INPUT   = [0.110, 0.106, 0.106, 1]     # #1c1b1b solid

TEXT_PRIMARY = [0.898, 0.886, 0.882, 1]   # #e5e2e1
TEXT_MUTED   = [0.725, 0.792, 0.796, 1]   # #b9cacb
TEXT_HINT    = [1, 1, 1, 0.30]

STATUS_CONNECTED = [0, 0.820, 0.545, 1]   # #00d18b
STATUS_FAILED    = [1, 0.302, 0.302, 1]   # #ff4d4d
STATUS_WAITING   = [0.992, 0.839, 0.224, 1] # #fed639
STATUS_IDLE      = [0, 0.941, 1, 1]       # #00f0ff

ACCENT_THEMES = {
    'cyan':    {'name': 'Quantum Link Secured', 'hex': '#00f0ff',
                'rgba': [0, 0.941, 1, 1],
                'glow': [0, 0.941, 1, 0.18]},
    'violet':  {'name': 'Neon Violet Protocol', 'hex': '#7000ff',
                'rgba': [0.439, 0, 1, 1],
                'glow': [0.439, 0, 1, 0.18]},
    'amber':   {'name': 'Solar Flare Mode',     'hex': '#fed639',
                'rgba': [0.996, 0.839, 0.224, 1],
                'glow': [0.996, 0.839, 0.224, 0.18]},
    'emerald': {'name': 'Ghost Network',        'hex': '#00d18b',
                'rgba': [0, 0.820, 0.545, 1],
                'glow': [0, 0.820, 0.545, 0.18]},
    'crimson': {'name': 'Red Alert Mode',       'hex': '#ff4d4d',
                'rgba': [1, 0.302, 0.302, 1],
                'glow': [1, 0.302, 0.302, 0.18]},
    'indigo':  {'name': 'Deep Space Mode',      'hex': '#3f51b5',
                'rgba': [0.247, 0.318, 0.710, 1],
                'glow': [0.247, 0.318, 0.710, 0.18]},
    'rose':    {'name': 'Quantum Rose',         'hex': '#e91e63',
                'rgba': [0.914, 0.118, 0.388, 1],
                'glow': [0.914, 0.118, 0.388, 0.18]},
    'slate':   {'name': 'Stealth Mode',         'hex': '#849495',
                'rgba': [0.518, 0.580, 0.584, 1],
                'glow': [0.518, 0.580, 0.584, 0.18]},
}

DEFAULT_ACCENT = 'cyan'

def get_accent(key: str) -> dict:
    return ACCENT_THEMES.get(key, ACCENT_THEMES[DEFAULT_ACCENT])
```

---

## SECTION 5 — screens/home.py COMPLETE SOURCE

```python
# screens/home.py
from kivy.uix.screenmanager import Screen
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.app import App
from core.login import perform_login
from theme.colors import get_accent, STATUS_CONNECTED, STATUS_FAILED, \
    STATUS_WAITING, STATUS_IDLE


class HomeScreen(Screen):

    def on_enter(self):
        self._refresh_profile_card()
        self._apply_accent()
        self._start_idle_pulse()

    def on_leave(self):
        self._stop_pulse()

    # ── ACCENT APPLICATION ──────────────────────────────────────────────────

    def _apply_accent(self):
        app   = App.get_running_app()
        theme = get_accent(app.app_data.get('accent_theme', 'cyan'))
        # Title color
        self.ids.title_label.color = theme['rgba']
        # Profile name color
        self.ids.profile_name_label.color = theme['rgba']
        # Connect button border glow — update canvas color
        self._set_btn_border(theme['rgba'])

    def _set_btn_border(self, color):
        # The connect button border is drawn via canvas in KV.
        # Update the Color instruction via a bound property.
        self.ids.connect_glow_color.rgba = [
            color[0], color[1], color[2], 0.25
        ]

    # ── PROFILE CARD ────────────────────────────────────────────────────────

    def _refresh_profile_card(self):
        app  = App.get_running_app()
        idx  = app.app_data.get('active_profile', 0)
        prof = app.app_data['profiles'][idx]
        self.ids.profile_name_label.text = prof.get('name') or f'Profile {idx+1}'
        self.ids.profile_index_hint.text = f'{idx+1} / 3'

    def on_profile_card_tap(self):
        app = App.get_running_app()
        idx = (app.app_data.get('active_profile', 0) + 1) % 3
        app.app_data['active_profile'] = idx
        from core.storage import save_data
        save_data(app.app_data)
        self._refresh_profile_card()

    # ── CONNECT BUTTON ───────────────────────────────────────────────────────

    def on_connect_press(self):
        app  = App.get_running_app()
        idx  = app.app_data.get('active_profile', 0)
        prof = app.app_data['profiles'][idx]

        if not prof.get('username') or not prof.get('password'):
            # No credentials — show failed state immediately, no network call
            Clock.schedule_once(
                lambda dt: self._apply_result('error', 'NO CREDENTIALS'), 0
            )
            return

        self._set_status('connecting', 'CONNECTING...')
        self._start_connect_pulse()

        # ── THREAD-SAFE CALLBACK WRAPPER ─────────────────────────────────────
        # This is the crash fix. perform_login() calls result_callback()
        # from a background thread. We NEVER touch widgets in that callback
        # directly. We ALWAYS use Clock.schedule_once to marshal back to main.
        def _safe_callback(status, message):
            # This function is called from background thread.
            # It must NOT touch any widget properties.
            # It ONLY schedules work on the main thread.
            Clock.schedule_once(
                lambda dt: self._apply_result(status, message), 0
            )

        perform_login(prof['username'], prof['password'], _safe_callback)

    def _apply_result(self, status: str, message: str):
        # This is called via Clock.schedule_once — safe to touch widgets.
        self._stop_pulse()
        self._set_status(status, message)

    # ── STATUS MANAGEMENT ────────────────────────────────────────────────────

    def _set_status(self, status: str, message: str):
        """Always called on main thread."""
        self.ids.status_label.text = message

        color_map = {
            'connected':  STATUS_CONNECTED,
            'failed':     STATUS_FAILED,
            'error':      STATUS_FAILED,
            'connecting': STATUS_WAITING,
        }
        accent_color = color_map.get(status, STATUS_IDLE)
        self.ids.status_badge_color.rgba  = [
            accent_color[0], accent_color[1], accent_color[2], 0.10
        ]
        self.ids.status_border_color.rgba = accent_color
        self.ids.status_label.color       = accent_color

    # ── ANIMATIONS ──────────────────────────────────────────────────────────

    def _start_idle_pulse(self):
        """Slow ambient pulse on glow ring when idle."""
        glow = self.ids.connect_outer_glow
        self._idle_anim = (
            Animation(opacity=0.3, duration=1.5, t='in_out_sine') +
            Animation(opacity=1.0, duration=1.5, t='in_out_sine')
        )
        self._idle_anim.repeat = True
        self._idle_anim.start(glow)

    def _start_connect_pulse(self):
        """Fast intense pulse while connecting."""
        self._stop_pulse()
        glow = self.ids.connect_outer_glow
        self._connect_anim = (
            Animation(opacity=0.15, duration=0.4, t='out_sine') +
            Animation(opacity=0.9, duration=0.4, t='out_sine')
        )
        self._connect_anim.repeat = True
        self._connect_anim.start(glow)

    def _stop_pulse(self):
        for anim_attr in ('_idle_anim', '_connect_anim'):
            anim = getattr(self, anim_attr, None)
            if anim:
                anim.stop(self.ids.connect_outer_glow)
        self.ids.connect_outer_glow.opacity = 1.0
```

---

## SECTION 6 — screens/profiles.py COMPLETE SOURCE

```python
# screens/profiles.py
from kivy.uix.screenmanager import Screen
from kivy.animation import Animation
from kivy.app import App
from core.storage import save_data
from theme.colors import get_accent


class ProfilesScreen(Screen):

    current_tab = 0

    def on_enter(self):
        self._load_tab(self.current_tab)
        self._apply_accent()
        self._highlight_tab(self.current_tab)

    def _apply_accent(self):
        app   = App.get_running_app()
        theme = get_accent(app.app_data.get('accent_theme', 'cyan'))
        self.ids.title_label.color    = theme['rgba']
        self.ids.save_btn_color.rgba  = theme['rgba']
        self._highlight_tab(self.current_tab)

    def switch_tab(self, index: int):
        self._save_current_tab()
        self.current_tab = index
        self._load_tab(index)
        self._highlight_tab(index)

    def _highlight_tab(self, index: int):
        app   = App.get_running_app()
        theme = get_accent(app.app_data.get('accent_theme', 'cyan'))
        for i, tab_id in enumerate(['tab_p1', 'tab_p2', 'tab_p3']):
            tab = self.ids[tab_id]
            if i == index:
                tab.color       = theme['rgba']
                tab.bold        = True
            else:
                tab.color       = [0.518, 0.580, 0.584, 1]
                tab.bold        = False

    def _load_tab(self, index: int):
        app  = App.get_running_app()
        prof = app.app_data['profiles'][index]
        self.ids.profile_name_input.text = prof.get('name', '')
        self.ids.username_input.text     = prof.get('username', '')
        self.ids.password_input.text     = prof.get('password', '')

    def _save_current_tab(self):
        app  = App.get_running_app()
        prof = app.app_data['profiles'][self.current_tab]
        prof['name']     = self.ids.profile_name_input.text.strip()
        prof['username'] = self.ids.username_input.text.strip()
        prof['password'] = self.ids.password_input.text

    def on_save(self):
        self._save_current_tab()
        save_data(App.get_running_app().app_data)
        lbl = self.ids.save_feedback_label
        lbl.text    = 'Saved ✓'
        lbl.opacity = 1
        Animation(opacity=0, duration=1.8, t='out_quad').start(lbl)

    def toggle_password_reveal(self):
        inp = self.ids.password_input
        inp.password = not inp.password
        self.ids.reveal_btn_label.text = 'HIDE' if not inp.password else 'REVEAL'
```

---

## SECTION 7 — screens/settings.py COMPLETE SOURCE

```python
# screens/settings.py
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.properties import BooleanProperty
from kivy.animation import Animation
from kivy.app import App
from kivy.metrics import dp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from core.storage import save_data
from theme.colors import get_accent, ACCENT_THEMES, DEFAULT_ACCENT


class SettingsScreen(Screen):

    _dialog = None

    def on_enter(self):
        app = App.get_running_app()
        self._apply_accent()
        self._load_auto_login_state()
        self._update_theme_label()

    def _apply_accent(self):
        app   = App.get_running_app()
        theme = get_accent(app.app_data.get('accent_theme', DEFAULT_ACCENT))
        self.ids.title_label.color             = [0.898, 0.886, 0.882, 1]
        self.ids.autoconnect_section_label.color = theme['rgba']
        self.ids.theme_section_label.color      = theme['rgba']
        self.ids.sysinfo_section_label.color    = theme['rgba']
        self._highlight_active_swatch()

    def _load_auto_login_state(self):
        app = App.get_running_app()
        self.ids.auto_toggle.active = app.app_data.get('auto_login', False)

    def _update_theme_label(self):
        app   = App.get_running_app()
        key   = app.app_data.get('accent_theme', DEFAULT_ACCENT)
        theme = get_accent(key)
        self.ids.current_theme_label.text = f'Current theme: {theme["name"]}'

    def _highlight_active_swatch(self):
        app = App.get_running_app()
        active_key = app.app_data.get('accent_theme', DEFAULT_ACCENT)
        for key, swatch_id in [
            ('cyan', 'swatch_cyan'), ('violet', 'swatch_violet'),
            ('amber', 'swatch_amber'), ('emerald', 'swatch_emerald'),
            ('crimson', 'swatch_crimson'), ('indigo', 'swatch_indigo'),
            ('rose', 'swatch_rose'), ('slate', 'swatch_slate'),
        ]:
            swatch = self.ids.get(swatch_id)
            if swatch:
                swatch.active = (key == active_key)

    # ── AUTO LOGIN TOGGLE ───────────────────────────────────────────────────

    def on_auto_toggle_changed(self, value: bool):
        app = App.get_running_app()
        if value and not app.app_data.get('auto_login_confirmed', False):
            self._show_confirm_dialog()
            self.ids.auto_toggle.active = False
            return
        app.app_data['auto_login'] = value
        save_data(app.app_data)

    def _show_confirm_dialog(self):
        app   = App.get_running_app()
        theme = get_accent(app.app_data.get('accent_theme', DEFAULT_ACCENT))
        if self._dialog:
            self._dialog.dismiss()
        self._dialog = MDDialog(
            title='Enable Auto Connect?',
            text=(
                'ConnekTor will automatically try to connect to the campus '
                'portal whenever your phone joins a WiFi network while this '
                'app is open.\n\nYour active profile credentials will be used.'
            ),
            buttons=[
                MDFlatButton(
                    text='CANCEL',
                    theme_text_color='Custom',
                    text_color=[0.518, 0.580, 0.584, 1],
                    on_release=lambda x: self._dialog.dismiss(),
                ),
                MDRaisedButton(
                    text='ENABLE',
                    md_bg_color=theme['rgba'],
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
        self.ids.auto_toggle.active = True
        if self._dialog:
            self._dialog.dismiss()

    # ── THEME SELECTION ─────────────────────────────────────────────────────

    def on_theme_select(self, key: str):
        app = App.get_running_app()
        app.app_data['accent_theme'] = key
        save_data(app.app_data)
        self._apply_accent()
        self._update_theme_label()
        # Propagate to other screens
        sm = app.sm
        for screen_name in ['home', 'profiles']:
            s = sm.get_screen(screen_name)
            if hasattr(s, '_apply_accent'):
                s._apply_accent()
```

---

## SECTION 8 — main.py COMPLETE SOURCE

```python
# main.py
import urllib3
from kivy.utils import platform
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivymd.app import MDApp

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if platform != 'android':
    Window.size = (390, 780)

from core.storage    import load_data, save_data
from core.wifi_monitor import WiFiMonitor
from screens.home    import HomeScreen
from screens.profiles import ProfilesScreen
from screens.settings import SettingsScreen


class ConnekTorApp(MDApp):

    def build(self):
        self.theme_cls.theme_style     = 'Dark'
        self.theme_cls.primary_palette = 'Cyan'

        # Load KV files AFTER screen classes are imported
        Builder.load_file('kv/home.kv')
        Builder.load_file('kv/profiles.kv')
        Builder.load_file('kv/settings.kv')

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
        if not self.app_data.get('auto_login', False):
            return
        home = self.sm.get_screen('home')
        # Already on main thread (Clock.schedule_once in WiFiMonitor)
        home.on_connect_press()

    def on_stop(self):
        self.monitor.stop()
        save_data(self.app_data)


if __name__ == '__main__':
    ConnekTorApp().run()
```

---

## SECTION 9 — KV IMPLEMENTATION RULES (Critical for Kivy)

These rules prevent the most common KV translation mistakes when going from HTML to Kivy:

```
RULE 1 — Canvas colors must use Color instruction objects with ids:
  canvas:
    Color:
      id: my_color_instruction   ← give it an id
      rgba: 0, 0.941, 1, 0.25
    RoundedRectangle:
      ...
  Then in Python: self.ids.my_color_instruction.rgba = new_color
  This is how you dynamically change canvas-drawn colors.

RULE 2 — All sizes must use dp():
  size: dp(200), dp(200)
  NOT size: 200, 200

RULE 3 — Touchable areas that are not buttons:
  Use on_touch_down with collide_point check:
    on_touch_down:
      if self.collide_point(*args[1].pos): root.some_method()

RULE 4 — MDTextField styling:
  Use mode: 'fill' for dark-background fields.
  Set fill_color: rgba(28,27,27,1) to match BG_INPUT.
  Set line_color_focus: the accent color rgba tuple.

RULE 5 — Circular shapes:
  radius: [dp(100), dp(100), dp(100), dp(100)]  ← all 4 corners equal
  For a dp(200) widget, use dp(100) radius = perfect circle.

RULE 6 — Opacity-based glow simulation:
  Draw a second, larger RoundedRectangle in canvas.before,
  with the glow color at opacity 0.12–0.18 and a slightly larger size.
  Animate its opacity to simulate neon pulse.

RULE 7 — Bottom nav must be at the VERY BOTTOM of the BoxLayout:
  Use size_hint_y: None, height: dp(72).
  The main content above must use size_hint_y: 1 to fill remaining space.

RULE 8 — Font files referenced in KV must be relative to main.py:
  font_name: 'assets/fonts/Poppins-Bold.ttf'   ← correct
  font_name: 'Poppins-Bold'                    ← WRONG, will crash

RULE 9 — ScrollView for settings screen:
  Wrap the card stack in a ScrollView.
  The inner BoxLayout must have size_hint_y: None, height: self.minimum_height
  This is mandatory or the content will overflow off-screen.

RULE 10 — No MDBottomNavigation widget:
  Do not use KivyMD's MDBottomNavigation. It has version-dependent API changes.
  Build the bottom nav manually as a BoxLayout with 3 vertical BoxLayouts
  inside, each containing an MDIcon and MDLabel, with on_touch_down handlers.
```

---

## SECTION 10 — FINAL VERIFICATION CHECKLIST

Before pushing to GitHub, verify each item:

```
CRASH FIX
[ ] HomeScreen._apply_result() is the ONLY method that touches widget ids
[ ] perform_login() callback NEVER directly writes to self.ids.*
[ ] _safe_callback() inside on_connect_press() only calls Clock.schedule_once
[ ] No other background thread touches any widget property anywhere

UI FIDELITY
[ ] CONNECT button is a CIRCLE (radius = half of width), not a rounded square
[ ] App background is #0F0F0F / #131313 — pure near-black, not navy
[ ] All cards use rgba(26,26,26,0.85) — NOT #161829 from old plan
[ ] Bottom nav has cyan glow shadow on top edge
[ ] Active nav tab has cyan glow dot indicator below icon
[ ] Status badge is pill-shaped (radius dp(999))
[ ] Save button on Profiles is pill-shaped (radius dp(999)) with cyan bg
[ ] 8 color swatches on Settings in 4x2 grid
[ ] Toggle switch is custom Canvas widget, NOT MDSwitch

THEME SYSTEM
[ ] 8 themes defined in theme/colors.py with name, hex, rgba, glow keys
[ ] Changing theme immediately updates all 3 screens via _apply_accent()
[ ] Active swatch shows cyan ring border highlight
[ ] Current theme name updates below swatches

FONTS
[ ] All headlines use Poppins-Bold.ttf via font_name: 'assets/fonts/Poppins-Bold.ttf'
[ ] All body text uses Poppins-Regular.ttf
[ ] No fallback to Roboto for headlines

LOGIN LOGIC (untouched)
[ ] core/login.py is byte-for-byte identical to CONNEKTOR_FINAL_BUILD_PLAN.md
[ ] POST URL still https://10.100.1.1:8090/login.xml
[ ] payload still has mode='191', a=timestamp_ms, producttype='your_producttype'
[ ] verify=False still set
[ ] Manual URL encoding with requests.utils.quote still used
[ ] Success check still 'You are signed in as' in response.text

BUILD
[ ] All threading.Thread calls have daemon=True
[ ] urllib3 warnings suppressed in main.py
[ ] Window.size only set when platform != 'android'
[ ] __init__.py exists in core/, screens/, theme/
```

---

*End of document. Antigravity must implement exactly this. Do not approximate.*
