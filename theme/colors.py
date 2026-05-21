# theme/colors.py

# ── CYBER-MINIMALIST THEME (Stitch System) ───────────────────────────────
BG_PRIMARY    = '#131313'   # Obsidian black base
BG_CARD       = '#1C1B1B'   # Surface container low
BG_NAV        = '#0E0E0E'   # Surface container lowest
TEXT_PRIMARY  = '#E5E2E1'   # Main readable text
TEXT_MUTED    = '#B9CACB'   # Subtitles/Metadata
STATUS_FAIL   = '#FFB4AB'   # Red - Neon Error
STATUS_OK     = '#00F0FF'   # Cyan - Connected
STATUS_WAIT   = '#7000FF'   # Violet - Connecting
BTN_IDLE_A    = '#00F0FF'   # Cyan active
BTN_IDLE_B    = '#006970'   # Darker Cyan
BTN_OK_A      = '#00F0FF'
BTN_OK_B      = '#00F0FF'

# ── ACCENT THEMES (Retained structure but updated for Cyber palette) ──────
ACCENT_THEMES = {
    'electric_cyan': {
        'name':       'Electric Cyan',
        'accent':     '#00F0FF',
        'accent_soft':'#7DF4FF',
        'glow':       (0.0, 0.94, 1.0, 0.25),
    },
    'neon_violet': {
        'name':       'Neon Violet',
        'accent':     '#7000FF',
        'accent_soft':'#D1BCFF',
        'glow':       (0.44, 0.0, 1.0, 0.25),
    },
    'solar_orange': {
        'name':       'Solar Orange',
        'accent':     '#F97316',
        'accent_soft':'#FB923C',
        'glow':       (0.98, 0.45, 0.09, 0.25),
    },
    'ghost_white': {
        'name':       'Ghost White',
        'accent':     '#E5E2E1',
        'accent_soft':'#FFFFFF',
        'glow':       (0.9, 0.9, 0.9, 0.25),
    }
}

DEFAULT_ACCENT = 'electric_cyan'

def get_accent(theme_key: str) -> dict:
    return ACCENT_THEMES.get(theme_key, ACCENT_THEMES[DEFAULT_ACCENT])
