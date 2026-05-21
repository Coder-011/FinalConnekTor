# screens/home.py
from kivy.uix.screenmanager import Screen
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.app import App
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from core.login import perform_login
from theme.colors import get_accent, STATUS_FAIL, STATUS_OK, STATUS_WAIT


class HomeScreen(Screen):

    _info_dialog = None

    def on_enter(self):
        self._refresh_profile_card()
        self._apply_accent()

    def _apply_accent(self):
        app   = App.get_running_app()
        theme = get_accent(app.app_data.get('accent_theme', 'electric_cyan'))
        accent_color = self._hex_to_rgba(theme['accent'])
        
        self.ids.title_label.text_color = accent_color
        self.ids.profile_name_label.text_color = accent_color
        self.ids.status_badge.line_color = accent_color
        self.ids.status_label.text_color = accent_color
        self.ids.connect_btn.md_bg_color = accent_color
        self.ids.connect_glow.md_bg_color = [accent_color[0], accent_color[1], accent_color[2], 0.1]

    def _refresh_profile_card(self):
        app  = App.get_running_app()
        idx  = app.app_data.get('active_profile', 0)
        prof = app.app_data['profiles'][idx]
        self.ids.profile_name_label.text   = prof['name'] or f'Profile {idx+1}'
        self.ids.profile_index_label.text  = 'Tonal layering enabled'

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
            self._set_status('failed', 'CREDENTIALS MISSING')
            return
        self.start_login()

    def start_login(self):
        app  = App.get_running_app()
        idx  = app.app_data.get('active_profile', 0)
        prof = app.app_data['profiles'][idx]
        self._set_status('connecting', 'CONNECTING...')
        self._start_pulse()
        perform_login(prof['username'], prof['password'], self._on_login_result)

    def _on_login_result(self, status: str, message: str):
        self._stop_pulse()
        self._set_status(status, message)

    def _set_status(self, status: str, message: str):
        badge = self.ids.status_badge
        label = self.ids.status_label
        label.text = message.upper()
        colors = {
            'connected':  STATUS_OK,
            'failed':     STATUS_FAIL,
            'connecting': STATUS_WAIT,
            'error':      STATUS_FAIL,
        }
        badge.line_color = self._hex_to_rgba(colors.get(status, STATUS_OK))
        label.text_color = self._hex_to_rgba(colors.get(status, STATUS_OK))

    def _start_pulse(self):
        btn = self.ids.connect_btn
        self._pulse_anim = Animation(
            scale_x=1.05, scale_y=1.05, duration=0.5
        ) + Animation(
            scale_x=1.0, scale_y=1.0, duration=0.5
        )
        self._pulse_anim.repeat = True
        self._pulse_anim.start(btn)

    def _stop_pulse(self):
        if hasattr(self, '_pulse_anim'):
            self._pulse_anim.stop(self.ids.connect_btn)
        self.ids.connect_btn.scale_x = 1.0
        self.ids.connect_btn.scale_y = 1.0

    def show_info_dialog(self):
        """Displays connection instructions."""
        if not self._info_dialog:
            self._info_dialog = MDDialog(
                title="WiFi Connection Guide",
                text=(
                    "1. Ensure you are connected to the college WiFi SSID.\n"
                    "2. Configure your login credentials in the 'Profiles' tab.\n"
                    "3. Tap the central 'CONNECT' button to authenticate.\n"
                    "4. Enable 'Auto Connect' in Settings for background automation."
                ),
                buttons=[
                    MDFlatButton(
                        text="UNDERSTOOD",
                        theme_text_color="Custom",
                        text_color=self._hex_to_rgba('#00F0FF'),
                        on_release=lambda x: self._info_dialog.dismiss(),
                    ),
                ],
            )
        self._info_dialog.open()

    @staticmethod
    def _hex_to_rgba(hex_color: str) -> list:
        h = hex_color.lstrip('#')
        return [int(h[i:i+2], 16)/255 for i in (0, 2, 4)] + [1.0]
