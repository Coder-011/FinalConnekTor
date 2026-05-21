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
