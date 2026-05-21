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
