from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout


Builder.load_file("setting.kv")

class SettingScreen(Screen):

    def __init__(self, *args, **kwargs):
        super(SettingScreen, self).__init__(*args, **kwargs)
        # self.configLayout.disabled = True



	pass
