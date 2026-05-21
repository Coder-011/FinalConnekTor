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
