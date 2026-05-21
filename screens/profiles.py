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
