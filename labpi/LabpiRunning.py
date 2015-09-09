#Kivy libs
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

#from python libs
import os
from subprocess import call
import threading

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
        call('mkdir '+self.dataController.getdata('path '), shell=True)
        call('mkdir '+self.dataController.getdata('path ')+'/run', shell=True)
        call('mkdir '+self.dataController.getdata('path ')+'/output', shell=True)
        call('mkdir '+self.dataController.getdata('path ')+'/output/receptor', shell=True)
        call('mkdir '+self.dataController.getdata('path ')+'/output/ligand', shell=True)

        thread = threading.Thread(target= self.gromacsRun.main)
        thread.start()
        
