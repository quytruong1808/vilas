import kivy
kivy.require('1.9.0') # replace with your current kivy version !

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.popup import Popup
from kivy.uix.label import Label

#python tools
#ListView

#import module
from LabpiLoad import LoadScreen
from LabpiReceptor import ReceptorScreen
from LabpiConfiguration import ConfigurationScreen
from LabpiSetting import SettingScreen
from LabpiRunning import RunningScreen
from Utils import DataController
from parsePdb import Variable

# pymol
import pymol
from multiprocessing import Process


# Builder.load_file("LabpiLoad.py").

#--------------------------------------------------------#
# Main function

class ScreenManagement(ScreenManager):

    def changeScreen(self, screen):
        if(screen == 'receptor'):
            #Check data input
            Receptors = Variable.parsepdb.Receptors
            Ligands = Variable.parsepdb.Ligands
            if(len(Receptors) == 0 or len(Ligands) == 0):
                popup = Popup(title='Warning!',
                content=Label(text='Please insert your data to two \ncolumn Receptors and Ligands before \nrunning this simulation'),
                size_hint=(None, None), size=(300, 200))
                popup.open()
                return

        if(screen == 'load'):
            self.get_screen(screen).setupView()
        elif(screen == 'receptor'):
            self.get_screen(screen).setupView()
        elif (screen == 'running'):
            self.get_screen(screen).setupView()
        elif (screen == 'configuration'):
            self.get_screen(screen).setupView()

        self.current = screen

    pass

class LabpiApp(App):
    def build(self):
        sm = ScreenManagement(transition = FadeTransition())
        sm.add_widget(LoadScreen(name='load'))
        sm.add_widget(ReceptorScreen(name='receptor'))
        sm.add_widget(ConfigurationScreen(name='configuration'))
        sm.add_widget(RunningScreen(name='running'))
        sm.add_widget(SettingScreen(name='setting'))

        sm.get_screen('load').set_pymol(pymol)
        sm.get_screen('receptor').set_pymol(pymol)
        return sm

def main():

    #Check settings file exist?
    dataController = DataController()
    dataController.checkExist()

    LabpiApp().run()



if __name__ == '__main__':
    main()

