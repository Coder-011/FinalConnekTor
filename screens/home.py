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
