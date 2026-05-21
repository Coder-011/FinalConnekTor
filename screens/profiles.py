# screens/profiles.py
from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from core.storage import save_data
from theme.colors import get_accent


class ProfilesScreen(Screen):

    current_tab = 0   # 0, 1, or 2
    _name_dialog = None

    def on_enter(self):
        self._load_tab(self.current_tab)
        self._apply_accent()

    def _apply_accent(self):
        app   = App.get_running_app()
        theme = get_accent(app.app_data.get('accent_theme', 'electric_cyan'))
        accent_color = self._hex_to_rgba(theme['accent'])
        
        self.ids.title_label.text_color = accent_color
        self.ids.section_label.text_color = accent_color
        
        # Style tabs
        for i, btn_id in enumerate(['tab_p1', 'tab_p2', 'tab_p3']):
            if i == self.current_tab:
                self.ids[btn_id].md_bg_color = accent_color
                self.ids[btn_id].text_color = [0.07, 0.07, 0.07, 1]
            else:
                self.ids[btn_id].md_bg_color = [0.11, 0.11, 0.11, 1]
                self.ids[btn_id].text_color = [0.9, 0.9, 0.9, 1]

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
        self.ids.save_feedback_label.text    = 'QUANTUM LINK SAVED'
        self.ids.save_feedback_label.opacity = 1
        from kivy.animation import Animation
        Animation(opacity=0, duration=2.0).start(self.ids.save_feedback_label)

    def edit_profile_name(self):
        """Opens a quick dialog to change the profile name."""
        app = App.get_running_app()
        theme = get_accent(app.app_data.get('accent_theme', 'electric_cyan'))
        
        content = MDTextField(
            text=self.ids.profile_name_input.text,
            hint_text="New Profile Name",
            mode="rectangle"
        )
        
        def update_name(obj):
            new_name = content.text
            if new_name:
                self.ids.profile_name_input.text = new_name
                self._save_current_tab()
                save_data(app.app_data)
                # If this was the active profile, home screen will automatically update on enter
            self._name_dialog.dismiss()

        self._name_dialog = MDDialog(
            title="Edit Profile Name",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self._name_dialog.dismiss()
                ),
                MDRaisedButton(
                    text="UPDATE",
                    md_bg_color=self._hex_to_rgba(theme['accent']),
                    on_release=update_name
                ),
            ],
        )
        self._name_dialog.open()

    @staticmethod
    def _hex_to_rgba(hex_color: str) -> list:
        h = hex_color.lstrip('#')
        return [int(h[i:i+2], 16)/255 for i in (0, 2, 4)] + [1.0]
