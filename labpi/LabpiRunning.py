#Kivy libs
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.popup import Popup

#from python libs
import os
import os.path
import signal
from subprocess import call
from subprocess import check_output
import threading
import ctypes
import time
from multiprocessing import Process

# import core labpi
from LabpiRun import GromacsRun
from Utils import DataController
from Utils import CheckPoint
from parsePdb import Variable

Builder.load_file(os.path.dirname(__file__)+"/LabpiRunning.kv")

class RunningScreen(Screen):
    root_path = os.path.dirname(__file__)
    dataController = DataController()

    progressBar = ObjectProperty(None)
    checkFile = ObjectProperty(None)
    emImg = ObjectProperty(None)
    nvtImg = ObjectProperty(None)
    nptImg = ObjectProperty(None)
    mdImg = ObjectProperty(None)
    smdImg = ObjectProperty(None)
    smdLog = ObjectProperty(None)

    progressUnit = 0
    progressPoint = 0

    checkPOINT = ''
    checkEM = False
    checkNVT = False
    checkNPT = False
    checkMD = False
    checkSMD = False
    lastSMD = 0

    #Create thread to run background
    gromacsRun = GromacsRun()
    thread = ObjectProperty(None)

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
        Clock.schedule_interval(self.check_log, 5)


    def check_log(self, dt):
        print 'check '+CheckPoint.point
        if CheckPoint.point != '':
            run_path = str(self.dataController.getdata('path ')) + '/run/' + str(CheckPoint.point)
            repeat_times = int(self.dataController.getdata('repeat_times '))

            if self.checkPOINT == '':
                self.checkPOINT = str(CheckPoint.point)
            elif self.checkPOINT != str(CheckPoint.point): 
                self.checkEM = checkNVT = checkNPT = checkMD = checkSMD = True
                self.lastSMD = 0
                self.checkPOINT = str(CheckPoint.point)


            em_path = run_path + '/em.gro' 
            if os.path.isfile(em_path) == True:
                self.emImg.source = self.root_path+'/img/tick_select.png'
                if self.checkEM == False: 
                    self.checkEM = True
                    self.progressPoint += self.progressUnit*0.5
            else:
                self.emImg.source = self.root_path+'/img/tick_normal.png'
            # self.emImg.reload()

            nvt_path = run_path + '/nvt.gro' 
            if os.path.isfile(nvt_path) == True:
                self.nvtImg.source = self.root_path+'/img/tick_select.png'
                if self.checkNVT == False: 
                    self.checkNVT = True
                    self.progressPoint += self.progressUnit*0.5
            else:
                self.nvtImg.source = self.root_path+'/img/tick_normal.png'
            # self.nvtImg.reload()

            npt_path = run_path + '/npt.gro' 
            if os.path.isfile(npt_path) == True:
                self.nptImg.source = self.root_path+'/img/tick_select.png'
                if self.checkNPT == False: 
                    self.checkNPT = True
                    self.progressPoint += self.progressUnit*0.5
            else:
                self.nptImg.source = self.root_path+'/img/tick_normal.png'
            # self.nptImg.reload()

            md_path = run_path + '/md.gro' 
            if os.path.isfile(md_path) == True:
                self.mdImg.source = self.root_path+'/img/tick_select.png'
                if self.checkMD == False: 
                    self.checkMD = True
                    self.progressPoint += self.progressUnit
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
            self.checkFile.text = str(CheckPoint.point)


        
    # def stopApp(self):
        # if(self.dataController.getdata('nohup ') == 'True'):
        #     self.thread.stop()
        # else:
        #self.thread.terminate()
        # pid = self.thread.pid
        # os.kill(pid, signal.SIGKILL) #or signal.SIGKILL 
        # print pid
        # print self.thread.is_alive()
        # time.sleep(1)
        # App().stop() 
        # App.get_running_app().stop()




# class GromacsThread(threading.Thread):

#     def stop(self):
#         self.__stop = True

#     def _bootstrap(self):
#         if threading._trace_hook is not None:
#             raise ValueError('Cannot run thread with tracing!')
#         self.__stop = False
#         sys.settrace(self.__trace)
#         super()._bootstrap()

#     def __trace(self, frame, event, arg):
#         if self.__stop:
#             raise StopThread()
#         return self.__trace


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