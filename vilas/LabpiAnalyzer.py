# -*- coding: utf-8 -*-

# from GromacsMD import GromacsMD
import numpy as np
import matplotlib.pyplot as plt
# from Utils import DataController
from subprocess import call, Popen, PIPE  # check_output,
# import subprocess
from sys import argv, exit
import getopt
import os
import prody
from shutil import copy
from glob import glob


class GromacsAnalyzer(object):
    pdbFile = ''
    grofile = ''
    trajfile = ''
    mdMdpFile = ''
    tprfile = ''
    start_time = ''
    end_time = ''
    pdbChain1 = ''
    pdbChain2 = ''
    group = ''
    conjugateGroup = ''
    rootAnalyzer = ''
    runfolder = ''
    analyze = ''
    GroLeft = ''
    GroRight = ''

    def __init__(self):
                # pdbFile,
                # grofile,
                # trajfile,
                # mdMdpFile,
                # tprfile,
                # start_time,
                # end_time,
                # pdbChain1,
                # pdbChain2,
                # group,
                # conjugateGroup,
                # rootAnalyzer,
                # runfolder,
                # GroLeft,
                # GroRight):
        pass
        # self.pdbFile = str(pdbFile)
        # self.grofile = str(grofile)
        # self.trajfile = str(trajfile)
        # self.mdMdpFile = str(mdMdpFile)
        # self.tprfile = str(tprfile)
        # self.start_time = str(start_time)
        # self.end_time = str(end_time)
        # self.pdbChain1 = str(pdbChain1)
        # self.pdbChain2 = str(pdbChain2)
        # self.group = str(group)
        # self.conjugateGroup = str(conjugateGroup)
        # self.rootAnalyzer = rootAnalyzer
        # self.runfolder = str(runfolder)
        # self.GroLeft = GroLeft
        # self.GroRight = GroRight
        # pass

    def copyScript(self, rootAnalyzer, runfolder):
        filelist = glob(rootAnalyzer + '/analyzer/*')
        print filelist
        for i in filelist:
            copy(i, str(runfolder))
        # call('cp analyzer/* ' + str(runfolder) + '/')

    def Resid(self, pdbFile, pdbChain1, pdbChain2, ligandName, runfolder):
        """
        Return a list of residue in `Receptor` which distance from `Ligand` is less or equal 5 angstroms.
        """
        # print "wthelelelelle"
        print self.runfolder
        os.chdir(runfolder)
        # acpype = glob('*.acpype')
        if pdbChain2 != '':
            a = prody.parsePDB(str(pdbFile)).select('('+pdbChain1+')' + ' and within 5 of chain ' + pdbChain2)
            residList = np.array(list(sorted(set(a.getResnums()))), dtype='str')
            residlist = " ".join(residList)
            # for i in range(1, len(residList)):
            # residlist += ' ' + str(residList[i])
            with open('cutoff-resid-5angstroms', 'w') as residfile:
                residfile.write(residlist)
            return residList, str(runfolder + '/cutoff-resid-5angstroms')
        elif ligandName != '':
            receptor = prody.parsePDB(str(pdbFile))
            Ligand = []
            # for i in range(len(acpype)):
            # Ligand.append(str(acpype[i].strip('.acpype')))
            # print "is it a bug here??"
            # print Ligand
            # ligand = []
            # for i in range(len(Ligand)):
            Ligand.append(prody.parsePDB(str(ligandName) + '.acpype/' + str(ligandName) + '_NEW.pdb'))
            # print ligand
            protein = receptor
            # print "this is protein before add ligand[i]"
            # print protein
            haha = []
            for i in range(len(Ligand)):
                protein += Ligand[i]
                haha = np.array(list(sorted(set(Ligand[i].getResnames()))), dtype='str')
            # print "this is protein after add ligand[i]"
            # print protein
            # print haha
            # print type(haha)
            ligands = ' or resname '.join(haha)
            hoho = protein.select('('+pdbChain1+')' + ' and within 5 of resname ' + ligands)
            residList = list(sorted(set(hoho.getResnums())))
            residList = np.array(residList, dtype='str')
            residlist = " ".join(residList)
            # print residlist
            # for i in range(1, len(residList)):
            # residlist += ' ' + str(residList[i])
            with open('cutoff-resid-5angstroms', 'w') as residfile:
                residfile.write(residlist)
            return residList, str(runfolder + '/cutoff-resid-5angstroms')

    def make_ndx(self, resid, grofile, runfolder):
        """
        Make index.ndx file contains residues seperately
        """
        os.chdir(runfolder)
        if os.path.isfile('index.ndx'):
            makeIndex = self.GroLeft + 'make_ndx' + self.GroRight + ' -f ' + grofile + ' -n '+runfolder+'/index.ndx -o '+runfolder+'/index.ndx'
            Popen(makeIndex, stdin=PIPE, shell=True).communicate('r ' + resid + '\nq\n')
            return 0
        else:
            makeIndex = self.GroLeft + 'make_ndx' + self.GroRight + ' -f ' + grofile + ' -o index.ndx'
            Popen(makeIndex, stdin=PIPE, shell=True).communicate('r ' + resid + '\nq\n')
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
        os.chdir(runfolder)
        print "Created folder %s" % resid
        Popen('mkdir ' + resid, stdin=PIPE, shell=True).communicate()
        os.chdir(str(runfolder) + '/' + str(resid))
        call("pwd", shell=True)
        self.mdp_generator(resid, conjugateGroup, mdMdpFile, runfolder)
        # copy('md_md.mdp', str(resid) + '/' + str(resid) + '.mdp')
        os.chdir(runfolder)

    def g_energy(self, resid, group, runfolder):
        os.chdir(runfolder + '/' + resid)
        if self.GroLeft == 'gmx ':
            genergy = self.GroLeft + 'energy' + self.GroRight + ' -f ener.edr -s ' + resid + '.tpr -o energy' + resid + '.xvg'
        else:
            genergy = self.GroLeft + 'g_energy' + self.GroRight + ' -f ener.edr -s ' + resid + '.tpr -o energy' + resid + '.xvg'
        Popen(genergy, stdin=PIPE,
              shell=True).communicate('LJ-14\nCoulomb-14\nLJ-(SR)\nCoulomb-(SR)\nCoul.-recip.\nPotential\nKinetic-En.\nTotal-Energy\nCoul-SR:r_'+resid+'-'+group+'\nLJ-SR:r_'+resid+'-'+group+'\nCoul-14:r_'+resid+'-'+group+'\nLJ-14:r_'+resid+'-'+group+'\n0\n')
        # 4 5 6 8 9 10 11 12 50 51 52 53
        os.chdir(runfolder)

    def mdrun(self, resid, trajfile, runfolder):
        os.chdir(runfolder + '/' + resid)
        grompp = self.GroLeft + 'grompp' + self.GroRight + ' -f ' + '../' + resid + '.mdp' + ' -c ' + self.grofile + ' -p ../../topol.top -n ../index.ndx' + ' -o ' + resid + '.tpr -maxwarn 20'
        print grompp
        call(grompp, shell=True)
        mdrun = self.GroLeft + 'mdrun' + self.GroRight + ' -s ' + resid + '.tpr -rerun ' + str(trajfile)
        call(mdrun, shell=True)
        print "Deleting new md_noPBC.xtc file in the folder %s created" % resid
        if not os.getcwd() == runfolder:
            trjFile = ' '.join(glob('*.trr'))
            trjFile += ' ' + ' '.join(glob('*.xtc'))
            Popen(['rm', trjFile])
            os.chdir(runfolder)
        print "Finish reruning the md simulation"

    def g_hbond(self, group1, group2, start_time, end_time, tprfile, trajfile, runfolder):
        """Calculate hbond between group1 and group2, time unit: ps"""
        os.chdir(runfolder)
        if self.GroLeft == 'gmx ':
            ghbond = self.GroLeft + 'hbond' + self.GroRight + ' -n index.ndx -s ' + tprfile + ' -f ' + trajfile + ' -num hbond.xvg -hbn hbond.ndx -hbm hbond.xpm -b ' + start_time + ' -e ' + end_time
        else:
            ghbond = self.GroLeft + 'g_hbond' + self.GroRight + ' -n index.ndx -s ' + tprfile + ' -f ' + trajfile + ' -num hbond.xvg -hbn hbond.ndx -hbm hbond.xpm -b ' + start_time + ' -e ' + end_time
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

    def plotHbond(self, runfolder, analyze):
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
            # Popen('mkdir plot_potential', stdin=PIPE, shell=True).communicate()
            os.makedirs(runfolder + '/plot_potential')

        f = open(str(resid) + '/energy'+str(resid)+'.xvg', 'r')
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
        print runfolder + '/plot_potential/' + str(resid) + '.dat'
        f = open(runfolder + '/plot_potential/' + str(resid) + '.dat', 'w')
        contents = "".join(contents)
        f.write(contents)
        f.close()

    def read_potential_dat(self, resid, runfolder):
        """
        Read residue.dat file using numpy. Return mean value of potential
        and standard deviation of potential of the residue.
        """
        os.chdir(str(runfolder) + '/plot_potential')
        data = np.genfromtxt(resid + '.dat', dtype=float, delimiter='  ', names=True)
        LJSRmean = data['LJSR'].mean()
        LJSRdeviation = data['LJSR'].std()
        CoulombSRmean = data['CoulombSR'].mean()
        CoulombSRdeviation = data['CoulombSR'].std()
        return float(LJSRmean), float(LJSRdeviation), float(CoulombSRmean), float(CoulombSRdeviation)

    def R_mean(self, residFile, runfolder):
        os.chdir(str(runfolder) + '/plot_potential')
        if residFile != '':
            residue = 'residues <- read.table("' + str(residFile) + '",header=F)'
        else:
            residue = self.resid

        # modify plot_potential.r file
        f = open(runfolder + '/../plot_potential.r', 'r')
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
        copy(runfolder + '/../plot_potential.r', runfolder + '/plot_potential')
        copy(residFile, runfolder + '/plot_potential')
        # # call R script
        # call('R CMD BATCH plot_potential.r', shell=True)

        # Call read_potential_dat to calculate each residue's mean & deviation
        f = open('mean.dat', 'w')
        f.write('residue  meanLJ  sdLJ  meanCoulomb  sdCoulomb  meanPotential  sdPotential\n')
        for i in range(len(self.resid.split())):
            a, b, c, d = self.read_potential_dat(i, runfolder)
            f.write(i + '  ' + str(a) + '  ' + str(b) + '  ' + str(c) + '  ' + str(d) + '  ' + str(a + c) + '  ' + str(b + d) + '\n')
        f.close()

    def plotPotential(self, residFile, runfolder, analyze):
        os.chdir(runfolder + '/plot_potential')

        data = np.genfromtxt('mean.dat', dtype=float, delimiter='  ', names=True)
        plt.figure()
        plt.errorbar(x=data['residue'], y=data['meanPotential'], yerr=data['sdPotential'])
        plt.title("Potential between each residue and ligand")
        plt.ylabel("Potential (kJ/mol)")
        plt.xlabel("residue ID")

        plt.figure()
        plt.errorbar(x=data['residue'], y=data['meanCoulomb'], yerr=data['sdCoulomb'])
        plt.title("Coulomb potential between each residue and ligand")
        plt.ylabel("Potential (kJ/mol)")
        plt.xlabel("residue ID")

        plt.figure()
        plt.errorbar(x=data['residue'], y=data['meanLJ'], yerr=data['sdLJ'])
        plt.title("Van der Waal potential between each residue and ligand")
        plt.ylabel("Potential (kJ/mol)")
        plt.xlabel("residue ID")

        plt.show()

    def main(self, argv):
        try:
            opts, args = getopt.getopt(argv, "hh:i:", ["pro=", "gro=", "trj=", "mdp=", "tpr=", "start=", "end=", "rechain=", "lichain=", "receptor=", "ligand=", "root=", "run=", "analyze=", "gleft=", "gright="])
        except getopt.GetoptError:
            print 'input error for LabpiAnalyzer'
            exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print """ Attribute:
                pdbFile: filename of the .pdb file
                grofile: filename of .grofile
                trajfile: filename of trajectory file. Eg: .xtc file, .trr file
                mdMdpFile: filename of .mdp file used for MD simulation
                tprfile: filename of .tpr file
                start_time: time to start calculate hbond
                end_time: time to end calculate hbond
                pdbChain1: chain name of receptor in pdb file
                pdbChain2: chain name of ligand in pdb file
                group: group of molecules to calculate hbond forms between itself and conjugate group
                conjugateGroup: conjugate group of the one mentioned above
                rootAnalyzer: path of LabpiAnalyzer.py
                runfolder: absolute path of folder contains all .gro, traj.trr, .xtc, .ndx, .mdp,... file
                GroLeft: prefix of gromacs packages
                GroRight: suffix of gromacs packages """
                exit()
            elif opt in ("--pro"):
                self.pdbFile = arg
            elif opt in ("--gro"):
                self.grofile = arg
            elif opt in ("--trj"):
                self.trajfile = arg
            elif opt in ("--mdp"):
                self.mdMdpFile = arg
            elif opt in ("--tpr"):
                self.tprfile = arg
            elif opt in ("--start"):
                self.start_time = arg
            elif opt in ("--end"):
                self.end_time = arg
            elif opt in ("--rechain"):
                self.pdbChain1 = arg
            elif opt in ("--lichain"):
                self.pdbChain2 = arg
            elif opt in ("--receptor"):
                self.group = arg
            elif opt in ("--ligand"):
                self.conjugateGroup = arg
            elif opt in ("--root"):
                self.rootAnalyzer = arg
            elif opt in ("--run"):
                self.runfolder = arg
            elif opt in ("--analyze"):
                self.analyze = arg
            elif opt in ("--gleft"):
                self.GroLeft = arg
            elif opt in ("--gright"):
                self.GroRight = arg
            elif opt in ("-i"):
                if arg.replace(' ', '') == 'True' or arg.replace(' ', '') == 'true':
                    self.resid, self.residFile = self.Resid(self.pdbFile, self.pdbChain1, self.pdbChain2, self.conjugateGroup, self.runfolder)
                    residList = self.resid

                    self.copyScript(self.rootAnalyzer, self.runfolder)
                    os.chdir(self.runfolder)

                elif arg.replace(' ', '') == 'False' or arg.replace(' ', '') == 'false':
                    call('rm -rf '+self.runfolder+'/residues/*', shell=True)
                    call('cp '+self.runfolder+'/index.ndx '+self.runfolder+'/residues/', shell=True)

                    with open('cutoff-resid-5angstroms', 'r') as line:
                        contents = line.readlines()
                        if len(contents) > 0:
                            residList = list(contents[0].replace('\n', ' ').split(' '))
                    self.resid = residList

                    for i in range(len(residList)):
                        self.make_ndx(str(residList[i]), self.grofile, self.runfolder + '/residues')

                    if not os.path.isdir(self.runfolder + '/residues'):
                        os.makedirs(self.runfolder + '/residues')
                    # rerun
                    for i in range(len(residList)):
                        self.mkdir(str(residList[i]), self.conjugateGroup, self.mdMdpFile, self.runfolder + '/residues')
                        self.mdrun(str(residList[i]), self.trajfile, self.runfolder + '/residues')

                    # Calculate potential & plot
                    os.makedirs(self.analyze)
                    for i in range(len(residList)):
                        self.g_energy(str(residList[i]), str(self.conjugateGroup), self.runfolder + '/residues')
                    for i in range(len(residList)):
                        self.change_Header(str(residList[i]), self.runfolder + '/residues')

                    self.R_mean(self.runfolder+'/cutoff-resid-5angstroms', self.runfolder + '/residues')
                    self.plotPotential(self.runfolder+'/cutoff-resid-5angstroms', self.runfolder + '/residues', self.analyze)

                    # Calculate Hydrogen bond & plot
                    self.g_hbond(str(self.group), str(self.conjugateGroup), self.start_time, self.end_time, self.tprfile, self.trajfile, self.runfolder + '/residues')
                    self.plotHbond(str(self.runfolder) + '/residues', self.analyze)
                    filelist = glob(self.runfolder + '/residues' + '/*.png') + glob(self.runfolder + '/*/*.xvg')
                    print filelist
                    for i in filelist:
                        copy(i, str(self.analyze))

                    call('rm -rf '+self.runfolder+'/residues/\#*', shell=True)

if __name__ == "__main__":
    A = GromacsAnalyzer()
    A.main(argv[1:])
