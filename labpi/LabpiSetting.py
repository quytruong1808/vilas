from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

import os

from Utils import DataController

Builder.load_file(os.path.dirname(__file__)+"/LabpiSetting.kv")

class SettingScreen(Screen):
    root_path = os.path.dirname(__file__)
    dataController = DataController()

    nvtNsteps =  ObjectProperty(None)
    nvtNst =  ObjectProperty(None)
    nptNsteps =  ObjectProperty(None)
    nptNst =  ObjectProperty(None)
    mdNsteps =  ObjectProperty(None)
    mdNst =  ObjectProperty(None)
    smdNsteps =  ObjectProperty(None)
    smdNst =  ObjectProperty(None)
    smdVel =  ObjectProperty(None)
    smdK =  ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(SettingScreen, self).__init__(*args, **kwargs)

        self.nvtNsteps.text = self.dataController.getdata('nvt-nsteps ')
        self.nvtNst.text = self.dataController.getdata('nvt-nst ')
        self.nptNsteps.text = self.dataController.getdata('npt-nsteps ')
        self.nptNst.text = self.dataController.getdata('npt-nst ')
        self.mdNsteps.text = self.dataController.getdata('md-nsteps ')
        self.mdNst.text = self.dataController.getdata('md-nst ')
        self.smdNsteps.text = self.dataController.getdata('smd-nsteps ')
        self.smdNst.text = self.dataController.getdata('smd-nst ')
        self.smdVel.text = self.dataController.getdata('smd-vel ')
        self.smdK.text = self.dataController.getdata('smd-k ')

        self.nvtNsteps.bind(text=self.on_nvt_nsteps)
        self.nvtNst.bind(text=self.on_nvt_nst)
        self.nptNsteps.bind(text=self.on_npt_nsteps)
        self.nptNst.bind(text=self.on_npt_nst)
        self.mdNsteps.bind(text=self.on_md_nsteps)
        self.mdNst.bind(text=self.on_md_nst)
        self.smdNsteps.bind(text=self.on_smd_nsteps)
        self.smdNst.bind(text=self.on_smd_nst)
        self.smdVel.bind(text=self.on_smd_vel)
        self.smdK.bind(text=self.on_smd_k)
	pass

    def on_nvt_nsteps(self, instance, value):
        self.dataController.setdata('nvt-nsteps ', value)

    def on_nvt_nst(self, instance, value):
        self.dataController.setdata('nvt-nst ', value)

    def on_npt_nsteps(self, instance, value):
        self.dataController.setdata('npt-nsteps ', value)

    def on_npt_nst(self, instance, value):
        self.dataController.setdata('npt-nst ', value)

    def on_md_nsteps(self, instance, value):
        self.dataController.setdata('md-nsteps ', value)

    def on_md_nst(self, instance, value):
        self.dataController.setdata('md-nst ', value)

    def on_smd_nsteps(self, instance, value):
        self.dataController.setdata('smd-nsteps ', value)

    def on_smd_nst(self, instance, value):
        self.dataController.setdata('smd-nst ', value)

    def on_smd_vel(self, instance, value):
        self.dataController.setdata('smd-vel ', value)

    def on_smd_k(self, instance, value):
        self.dataController.setdata('smd-k ', value)