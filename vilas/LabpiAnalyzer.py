# -*- coding: utf-8 -*-

# from GromacsMD import GromacsMD
import numpy as np
# from Utils import DataController
from subprocess import call, Popen, PIPE  # check_output,
# import subprocess
# from sys import argv, exit
# import getopt
import os
import prody
from shutil import copy
from glob import glob


class GromacsAnalyzer(object):
    """
    Attribute:
        residFile: filename of the file contains list of residue to be analyzed
        grofile: filename of .grofile
        trajfile: filename of trajectory file. Eg: .xtc file, .trr file
        tprfile: filename of .tpr file
        start_time: time to start calculate hbond
        end_time: time to end calculate hbond
        group: group of molecules to calculate hbond forms between itself and conjugate group
        conjugateGroup: conjugate group of the one mentioned above
        runfolder: absolute path of folder contains all .gro, traj.trr, .xtc, .ndx, .mdp,... file
    """
    def __init__(self,
                 pdbFile,
                 grofile,
                 trajfile,
                 mdMdpFile,
                 tprfile,
                 start_time,
                 end_time,
                 pdbChain1,
                 pdbChain2,
                 group,
                 conjugateGroup,
                 rootAnalyzer,
                 runfolder):
        self.pdbFile = str(pdbFile)
        self.grofile = str(grofile)
        self.trajfile = str(trajfile)
        self.mdMdpFile = str(mdMdpFile)
        self.tprfile = str(tprfile)
        self.start_time = str(start_time)
        self.end_time = str(end_time)
        self.pdbChain1 = str(pdbChain1)
        self.pdbChain2 = str(pdbChain2)
        self.group = str(group)
        self.conjugateGroup = str(conjugateGroup)
        self.rootAnalyzer = rootAnalyzer
        self.runfolder = str(runfolder)
        self.resid, self.residFile = self.Resid(self.pdbFile, self.pdbChain1, self.pdbChain2, self.runfolder)
        pass

    def copyScript(self, rootAnalyzer, runfolder):
        filelist = glob(rootAnalyzer + '/analyzer/*')
        print filelist
        for i in filelist:
            copy(i, str(runfolder))
        # call('cp analyzer/* ' + str(runfolder) + '/')

    def Resid(self, pdbFile, pdbChain1, pdbChain2, runfolder):
        """
        Return a list of residue in `group` which distance from `conjugateGroup` is less or equal 5 angstroms.
        """
        os.chdir(runfolder)
        a = prody.parsePDB(str(pdbFile)).select('chain ' + pdbChain1 + ' and within 5 of chain ' + pdbChain2)
        # print a
        residList = list(sorted(set(a.getResnums())))
        # print "This is a list of residues: %s" % residList
        # print "This is type of it: %s" % type(residList)
        residlist = str(residList[0])
        for i in range(1, len(residList)):
            residlist += ' ' + str(residList[i])
        # residlist = " ".join(residList)
        # print "This is a list of residues: %s" % residlist
        # print "This is type of it: %s" % type(residlist)
        with open('cutoff-resid-5angstroms', 'w') as residfile:
            residfile.write(residlist)
        # for i in a:
        # if str(i) != residList[-1]:
        # residList.append(i)
        # print residList
        return residList, str(runfolder + '/cutoff-resid-5angstroms')

    def make_ndx(self, resid, grofile, runfolder):
        """
        Make index.ndx file contains residues seperately
        """
        os.chdir(runfolder)
        if os.path.isfile('index.ndx'):
            Popen('make_ndx -f ' + grofile + ' -n index.ndx -o index.ndx',
                  stdin=PIPE,
                  shell=True).communicate('r ' + resid + '\nq\n')
            return 0
        else:
            Popen('make_ndx -f ' + grofile + ' -o index.ndx',
                  stdin=PIPE,
                  shell=True).communicate('r ' + resid + '\nq\n')
            return 0
        print "Add residue " + resid + " to index file."

    def mdp_generator(self, resid, group_to_calculate, mdMdpFile, runfolder):
        """
        Create mdp file within specified groups to calculate energy
        """
        os.chdir(runfolder)
        # copy('md_md.mdp', str(resid) + '.mdp')
        # with open(resid + '.mdp', 'w') as edit:
        # if str(edit.read()) == 'energygrps      = Protein\n':
        # edit.write('energygrps =\tr_' + str(resid) + '\t'+str(group_to_calculate)+'\n')
        with open(mdMdpFile, 'r') as oldMdp, open(str(resid) + '.mdp', 'w') as newMdp:
            for line in oldMdp:
                # print type(line.strip('\n').split())
                # print line.strip('\n').split()
                a = line.strip('\n').split()
                # print a
                if not a:
                    pass
                elif a[0] == 'energygrps':
                    # print 'Found "energygrps" line!!!'
                    newMdp.write('energygrps =\tr_' + str(resid) + '\t'+str(group_to_calculate) + '\n')
                else:
                    newMdp.write(line)
        print "Created %s.mdp" % resid

    def mkdir(self, resid, conjugateGroup, mdMdpFile, runfolder):
        """Create folder that will contain all data file for energy calculation.
        Then jump back to the root folder."""
        print "Created folder %s" % resid
        Popen('mkdir ' + resid, stdin=PIPE, shell=True).communicate()
        os.chdir(str(runfolder) + '/' + str(resid))
        call("pwd", shell=True)
        self.mdp_generator(resid, conjugateGroup, mdMdpFile, runfolder)
        # copy('md_md.mdp', str(resid) + '/' + str(resid) + '.mdp')
        os.chdir(runfolder)

    def g_energy(self, resid, group, runfolder):
        os.chdir(runfolder + '/' + resid)
        Popen(['g_energy', '-f ener.edr', '-s ' + resid + '.tpr',
               '-o energy' + resid + '.xvg'], stdin=PIPE,
              shell=True).communicate('LJ-14\nCoulomb-14\nLJ-(SR)\nCoulomb-(SR)\nCoul.-recip.\nPotential\nKinetic-En.\nTotal-Energy\nCoul-SR:r_'+resid+'-'+group+'\nLJ-SR:r_'+resid+'-'+group+'\nCoul-14:r_'+resid+'-'+group+'\nLJ-14:r_'+resid+'-'+group+'\n0\n')
        # 4 5 6 8 9 10 11 12 50 51 52 53
        os.chdir(runfolder)

    def mdrun(self, resid, trajfile, runfolder):
        os.chdir(runfolder + '/' + resid)
        call('grompp' + ' -f ' + '../' + resid + '.mdp'
             + ' -c ' + self.grofile + ' -p ../topol.top -n ../index.ndx'
             + ' -o ' + resid + '.tpr -maxwarn 20', shell=True)
        call('mdrun -s ' + resid + '.tpr -rerun ' + str(trajfile),
             shell=True)
        print "Deleting new md_noPBC.xtc file in the folder %s created" % resid
        if not os.getcwd() == runfolder:
            Popen('rm *.trr *.xtc', stdin=PIPE, shell=True).communicate()
            os.chdir(runfolder)
        print "Finish reruning the md simulation"

    def g_hbond(self, group1, group2, start_time, end_time, tprfile, trajfile, runfolder):
        """Calculate hbond between group1 and group2, time unit: ps"""
        os.chdir(runfolder)
        ghbond = 'g_hbond -n index.ndx -s ' + tprfile + ' -f ' + trajfile + ' -num hbond.xvg -hbn hbond.ndx -hbm hbond.xpm -b ' + start_time + ' -e ' + end_time
        a = Popen(ghbond, shell=True, stdin=PIPE)
        a.communicate(group1 + '\n' + group2 + '\n')[0]
        readhbondmap = 'python readHBmap.py -hbn hbond.ndx -hbm hbond.xpm -t 10'
        Popen(readhbondmap, shell=True)

    def getXvgLegend(self, xvgfile, runfolder):
        os.chdir(runfolder)
        # print "file name is: " + xvgfile
        f = open(xvgfile)
        contents = []
        for i, line in enumerate(f):
            if line.find('@') == 0:
                # print line
                contents.append(line)
            else:
                continue
        f.close()
        # print contents
        resids = []
        for i in range(len(contents)):
            if contents[i].find('legend "') != -1:
                # print contents[i]
                resids.append(contents[i].split('"')[1])
        # print resids
        return resids

    def genTranposeFile(self, xvgfile, runfolder):
        os.chdir(runfolder)
        f = open('occupancy.xvg', 'r')
        start, contents = 0, []
        for start, line in enumerate(f):
            if (line.find('@') != -1) or (line.find('#') != -1):
                continue
            else:
                contents.append(line)
        f.close()
        contents.remove('\n')
        for i in range(len(contents)):
            contents[i] = contents[i].split()
        print contents
        tranpose = np.transpose(contents)
        frames = tranpose[0]
        print frames
        tranpose = np.delete(tranpose, 0, axis=0)
        print tranpose
        f = open('tranpose.csv', 'w')
        for i in range(0, len(tranpose)):
            for j in range(0, len(tranpose[i])):
                f.write(tranpose[i][j] + '\t')
                if j == (len(tranpose[i]) - 1):
                    f.write('\n')
        f.close()

    def plotHbond(self, runfolder):
        os.chdir(runfolder)
        f = open('hbond.plot', 'r')
        contents = f.readlines()
        f.close()

        # Change ytics, i.e. change name of residue to be displayed
        blah = ''
        list_of_occupant = self.getXvgLegend('occupancy.xvg', runfolder)
        for i in range(len(list_of_occupant)):
            if i == len(list_of_occupant) - 1:
                blah += '"' + str(list_of_occupant[i]) + '" ' + str(i)
            else:
                blah += '"' + str(list_of_occupant[i]) + '" ' + str(i) + ','
        ytics = 'set ytics (' + blah + ') border in scale 0,0 mirror norotate  offset character 0, 0, 0 autojustify\n'
        for i in range(len(contents)):
            if contents[i].find('set ytics') == 0:
                contents[i] = ytics
        print 'modified hbond.plot file'

        # Change yrange, i.e. change amount of residue to be displayed
        yrange = 'set yrange[-0.5:' + str(len(list_of_occupant) - 1) + '.5] noreverse nowriteback\n'
        for i in range(len(contents)):
            if contents[i].find('set yrange') == 0:
                contents[i] = yrange

        # Check contents and write to file
        print contents
        f = open('test_hbond.plot', 'w')
        contents = "".join(contents)
        print contents
        f.write(contents)
        f.close()

        # Generate tranpose.csv file & execute GNUplot
        self.genTranposeFile('occupancy.xvg', runfolder)
        call('gnuplot test_hbond.plot', shell=True)

    def change_Header(self, resid, runfolder):
        """
        Change headers of energy.xvg file then write to .dat file in plot_potential folder
        """
        os.chdir(runfolder)

        # make plot_potential folder
        if not os.path.isdir(runfolder + '/plot_potential'):
            Popen('mkdir plot_potential', stdin=PIPE, shell=True).communicate()
            os.makedirs(runfolder + '/plot_potential')

        f = open(str(resid) + '/energy.xvg', 'r')
        contents = f.readlines()
        f.close()
        header = '  time  LJ14  Coulomb14  LJSR  CoulombSR  CoulombReciprocal  Potential  KineticEnergy  TotalEnergy  CoulSRresRNA  LJSRresRNA  Coul14resRNA  LJ14resRNA\n'
        a = []
        for i in range(len(contents)):
            if contents[i].find('@') == 0 or contents[i].find('#') == 0:
                a.append(i)
        contents[a[0]] = header
        for i in range(1, len(a)):
            if contents[i].find('@') == 0 or contents[i].find('#') == 0:
                contents[a[i]] = ''
        print runfolder + '/' + str(resid) + '.dat'
        f = open(runfolder + '/plot_potential/' + str(resid) + '.dat', 'w')
        contents = "".join(contents)
        f.write(contents)
        f.close()

    def R_mean(self, residFile, runfolder):
        os.chdir(str(runfolder) + '/plot_potential')
        residue = 'residues <- read.table("' + str(residFile) + '",header=F)'

        # modify plot_potential.r file
        f = open(runfolder + '/plot_potential.r', 'r')
        contents = f.readlines()
        f.close()
        for i in range(len(contents)):
            if contents[i].find('cutoff') == 0:
                contents[i] = residue
        # print contents
        f = open('plot_potential.plot', 'w')
        contents = "".join(contents)
        # print contents
        f.write(contents)
        f.close()

        # copy plot_potential.r and cutoff-resid-5angstroms file to
        # plot_potential folder
        copy(runfolder + '/plot_potential.r', runfolder + 'plot_potential')
        copy(residFile, runfolder + 'plot_potential')
        # call R script
        call('R CMD BATCH plot_potential.r', shell=True)

    def plotPotential(self, residFile, runfolder):
        os.chdir(runfolder)
        resid = self.resid

        # read potential.plot file
        f = open('potential.plot', 'r')
        contents = f.readlines()
        f.close()

        # Change xrange, i.e. change name of residue to be displayed
        xran = 'set xrange[' + str(int(resid[0]) - 1) + ':' + str(int(resid[-1]) + 1) + ']\n'
        for i in range(len(contents)):
            if contents[i].find('set xrange') == 0:
                contents[i] = xran
        print 'modified hbond.plot file'

        # Check contents and write to file
        # print contents
        f = open('potential.plot', 'w')
        contents = "".join(contents)
        # print contents
        f.write(contents)
        f.close()

        # call gnuplot
        Popen(['gnuplot', 'potential.plot'])

    def main(self):
        self.copyScript(self.rootAnalyzer, self.runfolder)
        os.chdir(self.runfolder)
        residList = self.resid

        for i in range(len(residList)):
            self.make_ndx(str(residList[i]), self.grofile, self.runfolder)
        call('rm \\#*', shell=True)

        # rerun
        for i in range(len(residList)):
            self.mkdir(str(residList[i]), self.conjugateGroup, self.mdMdpFile, self.runfolder)
            self.mdrun(str(residList[i]), self.trajfile, self.runfolder)

        # Calculate potential & plot
        for i in range(len(residList)):
            self.g_energy(str(residList[i]), str(self.conjugateGroup), self.runfolder)
        for i in range(len(residList)):
            self.change_Header(str(residList[i]), self.runfolder)
        self.R_mean(self.residFile, self.runfolder)
        self.plotPotential(self.residFile, self.runfolder)

        # Calculate Hydrogen bond & plot
        self.g_hbond(str(self.group), str(self.conjugateGroup), self.start_time, self.end_time, self.tprfile, self.trajfile, self.runfolder)
        self.plotHbond(str(self.runfolder))


"""
# Test script section
import numpy as np
from LabpiAnalyzer import *
residFile = 'cutoff-resid-14angstroms'
grofile =
trajfile =
tprfile =
start_time =
end_time =
group =
conjugateGroup =
runfolder = '/home/quyngan/CPL/Ngan/Ngan_MD/no_fix_comm/4L25/md'
GA = GromacsAnalyzer(residFile, runfolder)
residList = GA.Resid('cutoff-resid-14angstroms', '/home/quyngan/CPL/Ngan/Ngan_MD/no_fix_comm/3L25/md')

# for i in range(len(residList)):
    # GA.make_ndx(str(residList[i]), 'npt.gro', '/home/quyngan/CPL/Ngan/Ngan_MD/no_fix_comm/3L25/md')
# call('rm \\#*', shell=True)

# for i in range(len(residList)):
    # GA.mkdir(str(residList[i]), 'RNA', '/home/quyngan/CPL/Ngan/Ngan_MD/no_fix_comm/3L25/md')
    # GA.mdrun(str(residList[i]), '/home/quyngan/CPL/Ngan/Ngan_MD/no_fix_comm/3L25/md', 'md_noPBC.xtc')

for i in range(len(residList)):
    GA.g_energy(str(residList[i]), 'RNA', '/home/quyngan/CPL/Ngan/Ngan_MD/no_fix_comm/3L25/md')

for i in range(len(residList)):
    GA.change_Header(str(residList[i]), '/home/quyngan/CPL/Ngan/Ngan_MD/no_fix_comm/3L25/md')

GA.R_mean('cutoff-resid-14angstroms', '/home/quyngan/CPL/Ngan/Ngan_MD/no_fix_comm/3L25/md')
GA.plotPotential('cutoff-resid-14angstroms', '/home/quyngan/CPL/Ngan/Ngan_MD/no_fix_comm/3L25/md')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Set argv ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
# script, first_argv = argv
# working_path = os.path.dirname(os.path.abspath(__file__))
# print type(working_path)
# print working_path
# os.chdir(working_path)

    # def __init__(self):
        # try:
            # opts, args = getopt.getopt(argv,
                                       # "x:s:f:l:",
                                       # ["trajfile=",
                                        # "tprfile=",
                                        # "grofile=",
                                        # "residuelist="])
        # except getopt.GetoptError:
            # print 'LabpiAnalyzer.py -x <trajfile> -s <tprfile> -f <grofile> -l <residuelist>'
            # exit(2)
        # for opt, arg in opts:
            # if opt == '-h' or opt == '--help':
                # print """"""
    # def Resid(self, residFile, runfolder):
        # Read file containing ID number of residues. Return list of residues.
        # The file must be in format:
        # resid1 resid2 resid3 ...
        # For example:
        # 1 69 123 124 125 146 332
        # ...
        # os.chdir(runfolder)
        # o = open(residFile, 'r')
        # resid = o.read().split()
        # o.close()
        # return resid
                # exit()
            # elif opt in ("-x", "--trajfile"):
                # trajfile = arg
            # elif opt in ("-s", "--tprfile"):
                # tprfile = arg
            # elif opt in ("-f", "--grofile"):
                # grofile = arg
            # elif opt in ("-o", "--residuelist"):
                # residfile = arg
        # # main_path = self.dataController.getdata('path ')
        # main_path = os.path.dirname(os.path.abspath(__file__))
        # self.runfolders = check_output('ls '+main_path+'/run/', shell=True).splitlines()

        # self.residfile = residfile
        # self.grofile = grofile
        # self.tprfile = tprfile
        # self.trajfile = trajfile
        # return 0
"""
