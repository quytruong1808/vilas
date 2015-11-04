#Kivy libs
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.core.image import Image
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button

from subprocess import check_output
import subprocess
import os


from Utils import DataController

#Kivy file
Builder.load_file(os.path.dirname(__file__)+"/LabpiConfiguration.kv")

class ConfigurationScreen(Screen):
    root_path = os.path.dirname(__file__)

    dataController = DataController()

    optimizedButton = ObjectProperty(None)
    customButton = ObjectProperty(None)
    OptimizedButton = ObjectProperty(None)
    optimizedTick = ObjectProperty(None)
    configLayout = ObjectProperty(None)
    boxGromacs = ObjectProperty(None)
    versionButton = ObjectProperty(None)
    is_optimized = True

    pathText = ObjectProperty(None)
    caverBox = ObjectProperty(None)
    icstBox = ObjectProperty(None)
    ligandAutoBox = ObjectProperty(None)
    repeatTimesText = ObjectProperty(None)
    nohupBox = ObjectProperty(None)
    configpBox = ObjectProperty(None)
    normalBox = ObjectProperty(None)
    maximumCoresText = ObjectProperty(None)
    gpuAutoBox = ObjectProperty(None)


    def setupView(self):
        dropdown = DropDown()

        #Check gromacs version 
        try:
            command_version = check_output("compgen -ac | grep mdrun", shell=True, executable='/bin/bash').splitlines()
            for x in range(0, len(command_version)):
                print command_version[x]
                try:
                    versions = check_output(str(command_version[x])+" -version", shell=True, executable='/bin/bash').splitlines()
                    if not any("Gromacs version" in s for s in versions):
                        continue
                    version = [s for s in versions if "Gromacs version" in s][0].split(":")[1]
                    btn = Button(text=str(command_version[x]) + version, size_hint_y=None, height=35)
                    btn.bind(on_release=lambda btn: dropdown.select(btn.text))
                    # then add the button inside the dropdown
                    dropdown.add_widget(btn)
                    #Set first gromacs found
                    if x == 0 and self.dataController.getdata('gromacs_version ') == '':
                        self.versionButton.text = str(command_version[x]) + version
                        self.dataController.setdata('gromacs_version ', str(command_version[x] + version))
                    if self.dataController.getdata('gromacs_version ') == str(command_version[x]) + version:
                        self.versionButton.text = str(command_version[x]) + version
                except subprocess.CalledProcessError as e:
                    print e
        except subprocess.CalledProcessError as e:
            print e

        try:
            gmx_version = check_output("compgen -ac | grep gmx", shell=True, executable='/bin/bash').splitlines()
            for x in range(0, len(gmx_version)):
                print gmx_version[x]
                try:
                    versions = check_output(str(gmx_version[x])+" -version", shell=True, executable='/bin/bash').splitlines()
                    if not any("GROMACS version" in s for s in versions):
                        continue
                    version = [s for s in versions if "GROMACS version" in s][0].split(":")[1]
                    numVers = version.split('VERSION')[1].replace(' ','').split('.')
                    # If version >= 5.1
                    if int(numVers[0]) == 5 and int(numVers[1])>0:
                        btn = Button(text=str(gmx_version[x]) + version, size_hint_y=None, height=35)
                        btn.bind(on_release=lambda btn: dropdown.select(btn.text))
                        # then add the button inside the dropdown
                        dropdown.add_widget(btn)

                        #Set first gromacs found
                        if self.dataController.getdata('gromacs_version ') == '':
                            self.versionButton.text = str(gmx_version[x]) + version
                            self.dataController.setdata('gromacs_version ', str(gmx_version[x] + version))
                        if self.dataController.getdata('gromacs_version ') == str(gmx_version[x]) + version:
                            self.versionButton.text = str(gmx_version[x]) + version
                except subprocess.CalledProcessError as e:
                    print e
        except subprocess.CalledProcessError as e:
            print e
        
        self.versionButton.bind(on_release=dropdown.open)
        dropdown.bind(on_select=self.gromacs_version_check)

        #Check number of cores
        command_cores = check_output("nproc", shell=True, executable='/bin/bash').splitlines()
        if(len(command_cores) > 0):
            self.dataController.setdata('maximum_cores ', command_cores[0])
            self.maximumCoresText.text = command_cores[0]

    def __init__(self, *args, **kwargs):
        super(ConfigurationScreen, self).__init__(*args, **kwargs)        

        if ( self.dataController.getdata('config_auto ') == 'True' ):
            self.configLayout.disabled = True
        else: 
            # Disable touch = false
            self.configLayout.disabled = False
            # Set color of button
            self.is_optimized = False
            self.optimizedTick.color = [1,1,1,0]
            self.customTick.color = [1,1,1,1]
            self.optimizedButton.background_color = [0.62, 0.62, 0.62, 1]
            self.customButton.background_color = [0, 0.588, 0.533, 1]

        # Set init value for config
        self.pathText.text = self.dataController.getdata('path ')

        if (self.dataController.getdata('caver') == 'True'):
            self.caverBox.active = True
        else:
            self.caverBox.active = False

        if (self.dataController.getdata('icst') == 'True'):
            self.icstBox.active = True
        else:
            self.icstBox.active = False

        if (self.dataController.getdata('ligand_auto') == 'True'):
            self.ligandAutoBox.active = True
        else:
            self.ligandAutoBox.active = False

        self.repeatTimesText.text = self.dataController.getdata('repeat_times')

        self.nohupBox.active = False
        self.configBox.active = False
        self.normalBox.active = False
        if (self.dataController.getdata('mode') == 'nohup'):
            self.nohupBox.active = True
        elif(self.dataController.getdata('mode') == 'config'):
            self.configBox.active = True
        else:
            self.normalBox.active = True
            # self.dataController.setdata('mode', 'normal')



        self.maximumCoresText.text = self.dataController.getdata('maximum_cores')

        if (self.dataController.getdata('gpu_auto') == 'True'):
            self.gpuAutoBox.active = True
        else:
            self.gpuAutoBox.active = False


        # set listener
        self.pathText.bind(text = self.path_change)
        self.caverBox.bind(active = self.caver_check)
        self.icstBox.bind(active = self.icst_check)
        self.ligandAutoBox.bind(active = self.ligand_auto_check)
        self.repeatTimesText.bind(text = self.repeat_times)
        self.nohupBox.bind(active = self.nohup_check)
        self.configBox.bind(active = self.config_check)
        self.normalBox.bind(active = self.normal_check)
        self.maximumCoresText.bind(text = self.maximum_cores)
        self.gpuAutoBox.bind(active = self.gpu_auto_check)


    def path_change(self, instance, value):
        self.dataController.setdata('path ', value)
        
    def caver_check(self, checkbox, value):
        self.dataController.setdata('caver', str(value))
        #self.dataController.setdata('icst', str(not value))

    def icst_check(self, checkbox, value):
        self.dataController.setdata('icst', str(value))
        #self.dataController.setdata('caver', str(not value))

    def ligand_auto_check(self, checkbox, value):
        self.dataController.setdata('ligand_auto', str(value))

    def repeat_times(self, instance, value):
        self.dataController.setdata('repeat_times ', value)

    def nohup_check(self, checkbox, value):
        if value == True:
            self.dataController.setdata('mode ', 'nohup')
    def config_check(self, checkbox, value):
        if value == True:
            self.dataController.setdata('mode ', 'config')
    def normal_check(self, checkbox, value):
        if value == True:
            self.dataController.setdata('mode ', 'normal')

    def maximum_cores(self, instance, value):
        self.dataController.setdata('maximum_cores ', value)

    def gpu_auto_check(self, checkbox, value):
        self.dataController.setdata('gpu_auto ', str(value))

    def gromacs_version_check(self, instance, value):
        self.dataController.setdata('gromacs_version ', str(value))
        self.versionButton.text = value

    # For 2 button
    def optimizedConfig(self):
        if (self.is_optimized == True):
            pass
        else:
            self.is_optimized = True
            self.optimizedTick.color = [1,1,1,1]
            self.customTick.color = [1,1,1,0]
            self.optimizedButton.background_color = [0, 0.588, 0.533, 1]
            self.customButton.background_color = [0.62, 0.62, 0.62, 1]

            self.configLayout.disabled = True
            self.dataController.setdata('config_auto ', 'True')


    def customConfig(self):
        if (self.is_optimized == True):
            self.is_optimized = False
            self.optimizedTick.color = [1,1,1,0]
            self.customTick.color = [1,1,1,1]
            self.optimizedButton.background_color = [0.62, 0.62, 0.62, 1]
            self.customButton.background_color = [0, 0.588, 0.533, 1]

            self.configLayout.disabled = False
            self.dataController.setdata('config_auto ', 'False')
        else:
            pass

    pass