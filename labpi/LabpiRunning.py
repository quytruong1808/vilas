#Kivy libs
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

# import core labpi
from core.labpi import GromacsRun
from source.Utils import DataController

Builder.load_file("running.kv")

class RunningScreen(Screen):
	gromacsRun = GromacsRun()
	dataController = DataController()

    def __init__(self, *args, **kwargs):
        super(RunningScreen, self).__init__(*args, **kwargs)
    pass

    def setupView(self):
        #Check if folder is exits
        if not os.path.exists(self.dataController.getdata('path ')):
            os.makedirs(self.dataController.getdata('path '))

        if not os.path.exists(self.dataController.getdata('path ')+'/run'):
            os.makedirs(self.dataController.getdata('path ')+'/run')

        if not os.path.exists(self.dataController.getdata('path ')+'/output'):
            os.makedirs(self.dataController.getdata('path ')+'/output')

        self.gromacsRun.main()
