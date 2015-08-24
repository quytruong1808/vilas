import kivy
kivy.require('1.9.0') # replace with your current kivy version !

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition

Builder.load_file("labpi.kv")

class AnotherScreen(Screen):
    pass

class LabpiMain(Screen):
    pass

class ScreenManagement(ScreenManager):
    pass


class LabpiApp(App):
    def build(self):
        sm = ScreenManager(transition = FadeTransition())
        sm.add_widget(LabpiMain(name='main'))
        sm.add_widget(AnotherScreen(name='another'))
        return sm


if __name__ == '__main__':
    LabpiApp().run()