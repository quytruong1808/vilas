#Kivy libs
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.core.image import Image

class ConfigurationScreen(Screen):
    optimizedButton = ObjectProperty(None)
    customButton = ObjectProperty(None)
    OptimizedButton = ObjectProperty(None)
    optimizedTick = ObjectProperty(None)
    configLayout = ObjectProperty(None)
    is_optimized = True

    def __init__(self, *args, **kwargs):
        super(ConfigurationScreen, self).__init__(*args, **kwargs)
        # self.configLayout.disabled = True

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


    def customConfig(self):
        if (self.is_optimized == True):
            self.is_optimized = False
            self.optimizedTick.color = [1,1,1,0]
            self.customTick.color = [1,1,1,1]
            self.optimizedButton.background_color = [0.62, 0.62, 0.62, 1]
            self.customButton.background_color = [0, 0.588, 0.533, 1]

            self.configLayout.disabled = False
        else:
            pass

    pass