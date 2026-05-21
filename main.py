# main.py
import os
import urllib3
from kivy.utils import platform
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.clock import Clock
from kivymd.app import MDApp

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if platform != 'android':
    Window.size = (390, 780)   # desktop preview only — NOT set on Android

from core.storage    import load_data, save_data
from core.wifi_monitor import WiFiMonitor
from screens.home    import HomeScreen
from screens.profiles import ProfilesScreen
from screens.settings import SettingsScreen

KV_FILES = ['kv/home.kv', 'kv/profiles.kv', 'kv/settings.kv']


class ConnekTorApp(MDApp):

    def build(self):
        self.theme_cls.theme_style    = 'Dark'
        self.theme_cls.primary_palette = 'DeepPurple'

        for kv in KV_FILES:
            Builder.load_file(kv)

        self.app_data = load_data()

        self.sm = ScreenManager(transition=NoTransition())
        self.sm.add_widget(HomeScreen(name='home'))
        self.sm.add_widget(ProfilesScreen(name='profiles'))
        self.sm.add_widget(SettingsScreen(name='settings'))

        self.monitor = WiFiMonitor(
            login_callback=self._auto_login_trigger,
            get_enabled=lambda: self.app_data.get('auto_login', False),
        )
        self.monitor.start()

        return self.sm

    def _auto_login_trigger(self):
        """Called on main thread when monitor detects captive portal."""
        if not self.app_data.get('auto_login', False):
            return
        home = self.sm.get_screen('home')
        home.start_login()

    def on_stop(self):
        self.monitor.stop()
        save_data(self.app_data)


if __name__ == '__main__':
    ConnekTorApp().run()
