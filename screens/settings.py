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

    def _load_toggles(self):
        app = App.get_running_app()
        self.ids.auto_login_toggle.active = app.app_data.get('auto_login', False)

    def on_auto_login_toggle(self, value: bool):
        app = App.get_running_app()
        if value:
            if not app.app_data.get('auto_login_confirmed', False):
                self._show_auto_login_dialog()
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
            title='Enable Cyber-Auto Connect?',
            text=(
                "Instantly pair with trusted hubs when available in the background.\n\n"
                "Requires keeping the application active in the process stack."
            ),
            buttons=[
                MDFlatButton(
                    text='CANCEL',
                    on_release=lambda x: self._dialog.dismiss(),
                ),
                MDRaisedButton(
                    text='INITIALIZE',
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

    def on_theme_select(self, theme_key: str):
        app = App.get_running_app()
        app.app_data['accent_theme'] = theme_key
        save_data(app.app_data)
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
