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
