#Kivy libs
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.core.image import Image
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from source.Utils import DataController

from subprocess import check_output

class ConfigurationScreen(Screen):
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
    ligandAutoBox = ObjectProperty(None)
    repeatTimesText = ObjectProperty(None)
    nohupBox = ObjectProperty(None)
    maximumCoresText = ObjectProperty(None)
    gpuAutoBox = ObjectProperty(None)


    def __init__(self, *args, **kwargs):
        super(ConfigurationScreen, self).__init__(*args, **kwargs)
        #Check root path
        if self.dataController.getdata('path ') == '':
            username = check_output('echo $USER',shell=True).split('\n')[0]
            root_path = '/home/'+username+'/Documents/labpi-result'
            self.dataController.setdata('path ', root_path)
        
        #Check gromacs version 
        command_version = check_output("compgen -ac | grep mdrun", shell=True, executable='/bin/bash').splitlines()
        dropdown = DropDown()
        for x in range(0, len(command_version)):
            versions = check_output(str(command_version[x])+" -version", shell=True, executable='/bin/bash').splitlines()
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
        self.versionButton.bind(on_release=dropdown.open)
        dropdown.bind(on_select=self.gromacs_version_check)


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

        if (self.dataController.getdata('ligand_auto') == 'True'):
            self.ligandAutoBox.active = True
        else:
            self.ligandAutoBox.active = False

        self.repeatTimesText.text = self.dataController.getdata('repeat_times')

        if (self.dataController.getdata('nohup') == 'True'):
            self.nohupBox.active = True
        else:
            self.nohupBox.active = False

        self.maximumCoresText.text = self.dataController.getdata('maximum_cores')

        if (self.dataController.getdata('gpu_auto') == 'True'):
            self.gpuAutoBox.active = True
        else:
            self.gpuAutoBox.active = False


        # set listener
        self.pathText.bind(text = self.path_change)
        self.caverBox.bind(active = self.caver_check)
        self.ligandAutoBox.bind(active = self.ligand_auto_check)
        self.repeatTimesText.bind(text = self.repeat_times)
        self.nohupBox.bind(active = self.nohup_check)
        self.maximumCoresText.bind(text = self.maximum_cores)
        self.gpuAutoBox.bind(active = self.gpu_auto_check)


    def path_change(self, instance, value):
        self.dataController.setdata('path ', value)
        
    def caver_check(self, checkbox, value):
        self.dataController.setdata('caver', str(value))

    def ligand_auto_check(self, checkbox, value):
        self.dataController.setdata('ligand_auto', str(value))

    def repeat_times(self, instance, value):
        self.dataController.setdata('repeat_times ', value)

    def nohup_check(self, checkbox, value):
        self.dataController.setdata('nohup ', str(value))

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