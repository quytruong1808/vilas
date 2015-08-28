import kivy
kivy.require('1.9.0') # replace with your current kivy version !

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition

#python tools
#ListView

#import module
from LabpiLoad import LoadScreen

# Builder.load_file("LabpiLoad.py")

#--------------------------------------------------------#
# Screen class
class AnotherScreen(Screen):
    pass

class SettingScreen(Screen):
    pass


#--------------------------------------------------------#
# Main function

class ScreenManagement(ScreenManager):
    pass

class LabpiApp(App):
    def build(self):
        sm = ScreenManager(transition = FadeTransition())
        sm.add_widget(LoadScreen(name='load'))
        sm.add_widget(AnotherScreen(name='another'))
        sm.add_widget(SettingScreen(name='setting'))
        return sm

def main():
    LabpiApp().run()

if __name__ == '__main__':
    main()

