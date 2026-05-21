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
