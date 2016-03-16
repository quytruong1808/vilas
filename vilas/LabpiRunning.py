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
from parsePdb import ParsePdb
from Utils import PdbFile
from Utils import Chain

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
    lastFinish = False

    GroLeft = ''
    GroRight = ''
    GroVersion = ''

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
        # Check gromacs version
        self.checkGromacVersion()

        #Check if folder is exits
        call('mkdir '+self.dataController.getdata('path '), shell=True)
        call('mkdir '+self.dataController.getdata('path ')+'/run', shell=True)
        call('mkdir '+self.dataController.getdata('path ')+'/input', shell=True)
        call('mkdir '+self.dataController.getdata('path ')+'/input/receptor', shell=True)
        call('mkdir '+self.dataController.getdata('path ')+'/input/ligand', shell=True)
        call('mkdir '+self.dataController.getdata('path ')+'/analyse', shell=True)
        
        runfolders = check_output('ls '+self.dataController.getdata('path ')+'/run/', shell = True).splitlines()
        if len(runfolders) > 0:
            popup = RemoveDialog()
            popup.open()
        else:
            call('rm -r '+self.dataController.getdata('path ')+'/run/*', shell=True)
            call('rm -r '+self.dataController.getdata('path ')+'/input/ligand/*', shell=True)
            call('rm -r '+self.dataController.getdata('path ')+'/input/receptor/*', shell=True)
            self.thread = Process(target= self.gromacsRun.main)
            self.thread.start()

        #Check log
        repeat_times = int(self.dataController.getdata('repeat_times '))
        self.progressUnit = 1000/(4.5 + repeat_times)/len(Variable.parsepdb.Ligands)
        self.progressPoint = 0
        self.dataController.setdata('status', '')
        Clock.schedule_interval(self.check_log, 5)
        Clock.schedule_interval(self.spin_progress, 0.05)
        # Clock.schedule_interval(self.pymol_log, 300)

        #close pymol
        self.pymol.cmd.window('hide')

    def spin_progress(self, dt):
        if self.dataController.getdata('status') != 'finished':
            if(self.angle == 360):
                self.angle = 0
            self.angle += 10
            self.progressImage.rot.angle = self.angle
            self.progressImage.rot.origin = self.progressImage.center
            self.progressImage.rot.axis = (0, 0, 1)
        # self.progressImage.canvas.add(Rotate(angle=(self.angle), origin=(self.progressImage.center)))

    def check_log(self, dt):
        if self.dataController.getdata('status') == 'finished':
            if self.lastFinish == False:
                self.lastFinish = True
                popup = FinishDialog()
                popup.setText('Your job is finished. \n \nNow, you can close the interface. ')
                popup.open()
                self.progressText.text = 'ViLAS finished your jobs! now you can close app.'
                self.checkFile.text = str(self.dataController.getdata('status'))

        elif self.dataController.getdata('status') != '':
            # Check run nohup finish app
            if(self.dataController.getdata('mode ') == 'nohup' and self.firstFinish == True):
                self.firstFinish = False
                popup = FinishDialog()
                popup.setText('Your job is running in background. \n \nNow, you can close the interface. ')
                popup.open()

            run_path = str(self.dataController.getdata('path ')) + '/run/' + str(self.dataController.getdata('status'))
            repeat_times = int(self.dataController.getdata('repeat_times '))

            if self.checkPOINT == '':
                self.checkPOINT = str(self.dataController.getdata('status'))
            elif self.checkPOINT != str(self.dataController.getdata('status')): 
                self.checkEM = self.checkNVT = self.checkNPT = self.checkMD = self.checkSMD = False
                self.lastSMD = 0
                self.checkPOINT = str(self.dataController.getdata('status'))


            em_path = run_path + '/em/em.gro' 
            if os.path.isfile(em_path) == True:
                self.emImg.source = self.root_path+'/img/tick_select.png'
                if self.checkEM == False: 
                    self.checkEM = True
                    self.progressPoint += self.progressUnit*0.5
                    self.progressText.text = 'ViLAS is running at NVT step'
            else:
                self.emImg.source = self.root_path+'/img/tick_normal.png'
                self.progressText.text = 'ViLAS is running at Energy minimization step'
            # self.emImg.reload()

            nvt_path = run_path + '/nvt/nvt.gro' 
            if os.path.isfile(nvt_path) == True:
                self.nvtImg.source = self.root_path+'/img/tick_select.png'
                if self.checkNVT == False: 
                    self.checkNVT = True
                    self.progressPoint += self.progressUnit*0.5
                    self.progressText.text = 'ViLAS is running at NPT step'
            else:
                self.nvtImg.source = self.root_path+'/img/tick_normal.png'
            # self.nvtImg.reload()

            npt_path = run_path + '/npt/npt.gro' 
            if os.path.isfile(npt_path) == True:
                self.nptImg.source = self.root_path+'/img/tick_select.png'
                if self.checkNPT == False: 
                    self.checkNPT = True
                    self.progressPoint += self.progressUnit*0.5
                    self.progressText.text = 'ViLAS is running at MD step'
            else:
                self.nptImg.source = self.root_path+'/img/tick_normal.png'
            # self.nptImg.reload()

            md_path = run_path + '/md/md.gro' 
            if os.path.isfile(md_path) == True:
                self.mdImg.source = self.root_path+'/img/tick_select.png'
                if self.checkMD == False: 
                    self.checkMD = True
                    self.progressPoint += self.progressUnit
                    self.progressText.text = 'ViLAS is running at SMD step'
            else:
                self.mdImg.source = self.root_path+'/img/tick_normal.png'
            # self.mdImg.reload()

            # TODO: check percent import signal
            smd_log = 0
            for x in range(0, int(repeat_times)):
                smd_path_x = run_path + '/smd/md_st_'+str(x)+'.gro'
                if os.path.isfile(smd_path_x) == True:
                    smd_log+=1
                    if self.lastSMD < x:
                        self.lastSMD = x
                        self.checkSMD = False

                    if self.checkSMD == False: 
                        self.checkSMD = True
                        self.progressPoint += self.progressUnit
            self.smdLog.text = str(smd_log)+'/'+str(repeat_times)

            smd_path_last = run_path + '/smd/md_st_'+str(repeat_times-1)+'.gro' 
            if os.path.isfile(smd_path_last) == True:
                self.smdImg.source = self.root_path+'/img/tick_select.png'
            else:
                self.smdImg.source = self.root_path+'/img/tick_normal.png'
            # self.smdImg.reload()

            self.progressBar.value = self.progressPoint
            self.checkFile.text = str(self.dataController.getdata('status'))


    def pymol_log(self, dt):
        if self.dataController.getdata('status') == '' or self.dataController.getdata('status') == 'finished':
            return

        run_folder = self.dataController.getdata('status')
        run_path = str(self.dataController.getdata('path ')) + '/run/' + run_folder
        ligand_name = run_folder.split('run_')[1]
        repeat_times = int(self.dataController.getdata('repeat_times '))

        # Check point for pymol
        check_path = ''
        if os.path.isfile(run_path+'/em/em.gro') == False and os.path.isfile(run_path+'/em/em.cpt') == True and os.path.isfile(run_path+'/em/em.tpr') == True:
            check_path = run_path+'/em/em'
        if os.path.isfile(run_path+'/nvt/nvt.gro') == False and os.path.isfile(run_path+'/nvt/nvt.cpt') == True and os.path.isfile(run_path+'/nvt/nvt.tpr') == True:
            check_path = run_path+'/nvt/nvt'
        if os.path.isfile(run_path+'/npt/npt.gro') == False and os.path.isfile(run_path+'/npt/npt.cpt') == True and os.path.isfile(run_path+'/npt/npt.tpr') == True:
            check_path = run_path+'/npt/npt'
        if os.path.isfile(run_path+'/md/md.gro') == False and os.path.isfile(run_path+'/md/md.cpt') == True and os.path.isfile(run_path+'/md/md.tpr') == True:
            check_path = run_path+'/md/md'
        if os.path.isfile(run_path+'/smd/md_st.gro') == False and os.path.isfile(run_path+'/smd/md_st.cpt') == True and os.path.isfile(run_path+'/smd/md_st.tpr') == True:
            check_path = run_path+'/smd/md_st'
        for x in range(0, int(repeat_times)):
            if os.path.isfile(run_path+'/smd/md_st_'+str(x)+'.gro') == False and os.path.isfile(run_path+'/smd/md_st_'+str(x)+'.cpt') == True and os.path.isfile(run_path+'/smd/md_st_'+str(x)+'.tpr') == True:
                check_path = run_path+'/smd/md_st_'+str(x)

        if(check_path != ''):
            call('echo \"non-Water\"|' + self.GroLeft + 'trjconv' + self.GroRight +'-f '+ check_path +'.cpt -s '+ check_path +'.tpr -o '+ check_path +'.pdb', shell=True)
            self.pymol.cmd.reinitialize()
            self.pymol.cmd.load(check_path+'.pdb')

            chains = ParsePdb().listChain(check_path+'.pdb')
            for chain in chains:
                if chain.chain_type == 'protein':
                    self.pymol.cmd.show_as('cartoon', str(chain.chain_view) )
                    self.pymol.cmd.cartoon('automatic', str(chain.chain_view))
                else:
                    self.pymol.cmd.show_as('sticks', 'resname ' + str(chain.chain_view.getResnames()[0]))
            # self.pymol.cmd.set('stick_color', 'red')
            self.pymol.util.cbc()
        pass

    def checkGromacVersion(self):
        gromacs_version = self.dataController.getdata('gromacs_version ')
        version_array = gromacs_version.split(' VERSION ')[1].split('.')
        print version_array
        # If version >= 5
        if int(version_array[0]) == 5:
          # If version >= 5.1
          if int(version_array[1]) > 0:
            self.GroLeft = gromacs_version.split(' VERSION ')[0]
            self.GroRight = ''
          else: 
            # Check gmx
            mdrun_array = gromacs_version.split(' VERSION ')[0].split('mdrun')
            self.GroLeft = 'gmx '
            self.GroRight = mdrun_array[1]

          self.GroVersion = 5
        # If version = 4
        else:
          mdrun_array = gromacs_version.split(' VERSION ')[0].split('mdrun')
          self.GroLeft = mdrun_array[0]
          self.GroRight = mdrun_array[1]
          self.GroVersion = 4

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
        call('rm -r '+self.dataController.getdata('path ')+'/input/ligand/*', shell=True)
        call('rm -r '+self.dataController.getdata('path ')+'/input/receptor/*', shell=True)
        self.thread = Process(target= self.gromacsRun.main)
        self.thread.start()
        pass

    pass

class FinishDialog(Popup):
    dialogText = ObjectProperty(None)

    def setText(self, dialog_text):
        self.dialogText.text = dialog_text

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


        