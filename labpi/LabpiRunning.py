#Kivy libs
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.animation import Animation
from kivy.graphics import Rotate
from kivy.uix.image import Image
from kivy.graphics.context_instructions import PopMatrix, PushMatrix

#from python libs
import os
import os.path
import signal
from subprocess import call
from subprocess import check_output
import thread
import threading
import ctypes
import time
from multiprocessing import Process

# import core labpi
from LabpiRun import GromacsRun
from Utils import DataController
from parsePdb import Variable

Builder.load_file(os.path.dirname(__file__)+"/LabpiRunning.kv")

class RunningScreen(Screen):
    root_path = os.path.dirname(__file__)
    dataController = DataController()

    pymol = ObjectProperty(None)
    progressBar = ObjectProperty(None)
    checkFile = ObjectProperty(None)
    emImg = ObjectProperty(None)
    nvtImg = ObjectProperty(None)
    nptImg = ObjectProperty(None)
    mdImg = ObjectProperty(None)
    smdImg = ObjectProperty(None)
    smdLog = ObjectProperty(None)
    progressText = ObjectProperty(None)
    progressLayout = ObjectProperty(None)
    progressImage = ObjectProperty(None)

    progressUnit = 0
    progressPoint = 0

    checkPOINT = ''
    checkEM = False
    checkNVT = False
    checkNPT = False
    checkMD = False
    checkSMD = False
    lastSMD = 0
    angle = 0
    firstFinish = True

    #Create thread to run background
    gromacsRun = GromacsRun()
    thread = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super(RunningScreen, self).__init__(*args, **kwargs)

        # init progress image
        self.progressImage = ProgressImage()
        self.progressLayout.add_widget(self.progressImage)
        pass

    def set_pymol(self, pym):
        self.pymol = pym

    def setupView(self):
        #Check if folder is exits
        call('mkdir '+self.dataController.getdata('path '), shell=True)
        call('mkdir '+self.dataController.getdata('path ')+'/run', shell=True)
        call('mkdir '+self.dataController.getdata('path ')+'/output', shell=True)
        call('mkdir '+self.dataController.getdata('path ')+'/output/receptor', shell=True)
        call('mkdir '+self.dataController.getdata('path ')+'/output/ligand', shell=True)
        
        runfolders = check_output('ls '+self.dataController.getdata('path ')+'/run/', shell = True).splitlines()
        if len(runfolders) > 0:
            popup = RemoveDialog()
            popup.open()
        else:
            self.thread = Process(target= self.gromacsRun.main)
            self.thread.start()

        #Check log
        self.progressUnit = 1000/5.5/len(Variable.parsepdb.Ligands)
        self.progressPoint = 0
        self.dataController.setdata('status', '')
        Clock.schedule_interval(self.check_log, 5)
        Clock.schedule_interval(self.spin_progress, 0.05)
        Clock.schedule_interval(self.pymol_log, 300)

        #close pymol
        thread.start_new_thread( self.pymol.cmd.quit, ())

    def spin_progress(self, dt):
        if(self.angle == 360):
            self.angle = 0
        self.angle += 10
        self.progressImage.rot.angle = self.angle
        self.progressImage.rot.origin = self.progressImage.center
        self.progressImage.rot.axis = (0, 0, 1)
        # self.progressImage.canvas.add(Rotate(angle=(self.angle), origin=(self.progressImage.center)))

    def check_log(self, dt):
        if self.dataController.getdata('status') != '':
            # Check run nohup finish app
            if(self.dataController.getdata('nohup ') == 'True' and self.firstFinish == True):
                self.firstFinish = False
                popup = FinishDialog()
                popup.open()

            run_path = str(self.dataController.getdata('path ')) + '/run/' + str(self.dataController.getdata('status'))
            repeat_times = int(self.dataController.getdata('repeat_times '))

            if self.checkPOINT == '':
                self.checkPOINT = str(self.dataController.getdata('status'))
            elif self.checkPOINT != str(self.dataController.getdata('status')): 
                self.checkEM = checkNVT = checkNPT = checkMD = checkSMD = True
                self.lastSMD = 0
                self.checkPOINT = str(self.dataController.getdata('status'))


            em_path = run_path + '/em.gro' 
            if os.path.isfile(em_path) == True:
                self.emImg.source = self.root_path+'/img/tick_select.png'
                if self.checkEM == False: 
                    self.checkEM = True
                    self.progressPoint += self.progressUnit*0.5
                    self.progressText.text = 'Labpi is running at NVT step'
            else:
                self.emImg.source = self.root_path+'/img/tick_normal.png'
                self.progressText.text = 'Labpi is running at Energy minimization step'
            # self.emImg.reload()

            nvt_path = run_path + '/nvt.gro' 
            if os.path.isfile(nvt_path) == True:
                self.nvtImg.source = self.root_path+'/img/tick_select.png'
                if self.checkNVT == False: 
                    self.checkNVT = True
                    self.progressPoint += self.progressUnit*0.5
                    self.progressText.text = 'Labpi is running at NPT step'
            else:
                self.nvtImg.source = self.root_path+'/img/tick_normal.png'
            # self.nvtImg.reload()

            npt_path = run_path + '/npt.gro' 
            if os.path.isfile(npt_path) == True:
                self.nptImg.source = self.root_path+'/img/tick_select.png'
                if self.checkNPT == False: 
                    self.checkNPT = True
                    self.progressPoint += self.progressUnit*0.5
                    self.progressText.text = 'Labpi is running at MD step'
            else:
                self.nptImg.source = self.root_path+'/img/tick_normal.png'
            # self.nptImg.reload()

            md_path = run_path + '/md.gro' 
            if os.path.isfile(md_path) == True:
                self.mdImg.source = self.root_path+'/img/tick_select.png'
                if self.checkMD == False: 
                    self.checkMD = True
                    self.progressPoint += self.progressUnit
                    self.progressText.text = 'Labpi is running at SMD step'
            else:
                self.mdImg.source = self.root_path+'/img/tick_normal.png'
            # self.mdImg.reload()

            # TODO: check percent import signal
            smd_log = 0
            for x in range(0, int(repeat_times)):
                smd_path_x = run_path + '/md_1_'+str(x)+'.gro'
                if os.path.isfile(smd_path_x) == True:
                    smd_log+=1
                    if self.lastSMD < x:
                        self.lastSMD = x
                        self.checkSMD = False

                    if self.checkSMD == False: 
                        self.checkSMD = True
                        self.progressPoint += self.progressUnit
            self.smdLog.text = str(smd_log)+'/'+str(repeat_times)

            smd_path_last = run_path + '/md_1_'+str(repeat_times-1)+'.gro' 
            if os.path.isfile(smd_path_last) == True:
                self.smdImg.source = self.root_path+'/img/tick_select.png'
            else:
                self.smdImg.source = self.root_path+'/img/tick_normal.png'
            # self.smdImg.reload()

            self.progressBar.value = self.progressPoint
            self.checkFile.text = str(self.dataController.getdata('status'))

    def pymol_log(self, dt):
        pymol_thread = Thread(target = self.pymol_show, args = (chain, chainname, ))
        pymol_thread.start()

class ProgressImage(Image):
    root_path = os.path.dirname(__file__)

    def __init__(self, **kwargs):
        super(ProgressImage, self).__init__(**kwargs)
        # self.x = x -- not necessary, x is a property and will be handled by super()
        self.source = self.root_path +'/img/spin.png'
        self.size_hint = (None, None)
        self.size = (60, 60)

        with self.canvas.before:
            PushMatrix()
            self.rot = Rotate()
            self.rot.angle = 0
            self.rot.origin = self.center
            self.rot.axis = (0, 0, 1)
        with self.canvas.after:
            PopMatrix()


class RemoveDialog(Popup):

    gromacsRun = GromacsRun()
    thread = ObjectProperty(None)
    dataController = DataController()

    def cancel(self):
        self.dismiss()
        self.thread = Process(target= self.gromacsRun.main)
        self.thread.start()
        pass
    def remove(self):
        self.dismiss()
        call('rm -r '+self.dataController.getdata('path ')+'/run/*', shell=True)
        self.thread = Process(target= self.gromacsRun.main)
        self.thread.start()
        pass

    pass

class FinishDialog(Popup):

    gromacsRun = GromacsRun()
    thread = ObjectProperty(None)
    dataController = DataController()

    def cancel(self):
        self.dismiss()
        pass
    # def remove(self):
    #     self.dismiss()
    #     App().stop() 
    #     # App.get_running_app().stop()
    #     pass

    pass


        