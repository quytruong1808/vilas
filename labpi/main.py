import kivy
kivy.require('1.9.0') # replace with your current kivy version !

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition

#python tools
#ListView

#import module
from LabpiLoad import LoadScreen
from LabpiReceptor import ReceptorScreen
from LabpiConfiguration import ConfigurationScreen
from LabpiSetting import SettingScreen

# Builder.load_file("LabpiLoad.py")

#--------------------------------------------------------#
# Main function

class ScreenManagement(ScreenManager):

    def changeScreen(self, screen):
        if(screen == 'receptor'):
            self.get_screen(screen).setupView()
        self.current = screen
        print screen

    pass

class LabpiApp(App):
    def build(self):
        sm = ScreenManagement(transition = FadeTransition())
        sm.add_widget(ConfigurationScreen(name='configuration'))
        sm.add_widget(LoadScreen(name='load'))
        sm.add_widget(ReceptorScreen(name='receptor'))
        sm.add_widget(SettingScreen(name='setting'))
        return sm

def main():
    LabpiApp().run()

if __name__ == '__main__':
    main()

