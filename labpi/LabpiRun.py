# from pylab import *

from numpy import *
from prody import *
from os import listdir
import glob
import os
import sys
import Avogadro
import os.path
from subprocess import check_output
from subprocess import call
import subprocess

# import source
from parsePdb import Variable
from Utils import PdbFile
from Utils import DataController
from Utils import CheckPoint


AminoAcid = ["ALA", "ARG", "ASN", "ASP", "CYS", "GLU", "GLN", "GLY", "HIS", "ILE", "LEU", "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL", "SEC", "PYL", "ASX", "GLX", "XLE", "XAA"]
ChainNames = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','P','Q','R','S','T','U','V','Y','Z']
ForceField = 'amber99sb'
GroLeft  = ''
GroRight = ''
GroOption = ''
GroVersion = ''
AvogadroAuto = ''
run_caver = ''
run_nohup = ''
repeat_times = '0'
Method = '1'
main_path = ''
root_path = ''

ReceptorNumAtom = 0
ReceptorResidues = []
ReceptorCenter = []
ReceptorFile = []
LigandFile = []



class GromacsRun(object):
  global root_path
  root_path = os.path.dirname(__file__)
  dataController = DataController()

  #**********************************************************************#
  #***************************** Prepare Fuction ************************#
  #**********************************************************************#

  def ParsePDBInput(self):
    #Init variable
    global ReceptorCenter, ReceptorFile, ReceptorNumAtom, ReceptorResidues
    Receptors = Variable.parsepdb.Receptors

    ResidueNumber = 0
    lastResidueId = 0
    listCenter = [0,0,0] 

    #Init root path
    global main_path
    main_path = self.dataController.getdata('path ')
    call('rm ' + main_path +'/output/receptor/*', shell=True)

    #Parse PDB and save to variable
    print len(Receptors)
    for receptor in Receptors:
      filename = os.path.basename(receptor.file_path)
      filename = os.path.splitext(filename)[0]
      for chain in receptor.chains:
        if chain.is_selected == False:
          continue

        if chain.chain_type == 'protein': 
          protein = chain.chain_view
          
          fileName = main_path + '/output/receptor/receptor_' + filename + "_" + str(protein) 
          writePDB( fileName.replace(" ", ""), protein)
          
          #If receptor is in group for pulling
          if chain.is_group == True:
            ResidueStart = int(chain.resindices[0])
            RedidueEnd = int(chain.resindices[1])
            for resId in range(ResidueStart,RedidueEnd+1):
              listCenter += calcCenter(protein[resId])

            ReceptorNumAtom += protein.numAtoms()
            ResidueNumber += RedidueEnd - ResidueStart + 1

            #format ReceptorResidues
            resBegin = protein.getResnums()[0]
            ReceptorResidues.append(str(ResidueStart-resBegin + lastResidueId)+':'+str(RedidueEnd - resBegin + lastResidueId))
            
            lastResidueId += protein.numResidues()
            ReceptorFile.append(fileName.replace(" ", ""))

        else:
          ligand = chain.chain_view
          fileName = main_path + '/output/receptor/ligand_' +  filename + "_" + str(ligand.getResnames()[0])
          writePDB(fileName.replace(" ", ""), ligand)

    ReceptorCenter = listCenter/ResidueNumber




  #Check version of gromacs 
  #Check_out to read, call to call :))
  #Chon version gromacs tuong ung
  def setupOptions(self):
    # Get version of gromacs
    global GroLeft, GroRight, GroVersion
    gromacs_version = self.dataController.getdata('gromacs_version ')
    version_array = gromacs_version.split(' VERSION ')[1].split('.')
    mdrun_array = gromacs_version.split(' VERSION ')[0].split('mdrun')

    if int(version_array[0]) == 5:
      GroLeft = 'gmx '
      GroVersion = 5
    else:
      GroLeft = mdrun_array[0]
      GroVersion = 4
    GroRight = mdrun_array[1]

    # Set number of core or gpu
    global GroOption 
    check_gpu = check_output(gromacs_version.split(' VERSION ')[0]+" -version", shell=True, executable='/bin/bash').splitlines()
    if( [s for s in check_gpu if "GPU support:" in s][0].split(":")[1].replace(' ','') == 'enable'):
      GroOption = '-gpu_id 0'
    else:
      GroOption = ''

    # Caver tools
    global run_caver
    if self.dataController.getdata('caver ') == 'True':
      run_caver = 'y'
      call('tar xfz '+root_path+'/caver.tar.gz -C '+self.dataController.getdata('path '), shell=True)
    else:
      run_caver = 'n'

    #Repeat times 
    global repeat_times
    repeat_times = int(self.dataController.getdata('repeat_times '))

    #Run nohup
    global run_nohup
    if self.dataController.getdata('nohup ') == 'True':
      run_nohup = 'y'
    else:
      run_nohup = 'n'

    #Check add hydro by hand or auto
    global AvogadroAuto
    if self.dataController.getdata('ligand_auto ') == 'True':
      AvogadroAuto = 'true'
    else:
      AvogadroAuto = 'false'  

  #**********************************************************************#
  #************************* Ligand Fuction *****************************#
  #**********************************************************************#
  def AddHydrogen(self, ligandFile):
    ligand = Avogadro.MoleculeFile.readMolecule(ligandFile)
    ligandName = ligand.residues[0].name
    if AvogadroAuto == 'true':  
      ligand.removeHydrogens()
      ligand.addHydrogens()
      Avogadro.MoleculeFile.writeMolecule(ligand, ligandFile)
    elif AvogadroAuto == 'false':
      call('avogadro ' + ligandFile, shell=True)

    #Change name of residue
    call('antechamber -fi pdb -fo pdb -i ' +ligandFile+' -o ' +ligandFile+ ' -rn '+ligandName, shell=True, executable='/bin/bash')


  def CountCharge(self, ligandFile):
    ligand = Avogadro.MoleculeFile.readMolecule(ligandFile)
    sumCharge = 0
    for atom in ligand.atoms:
      sumCharge += atom.partialCharge

    return int(round(sumCharge, 0))
    
  def SetParameter(self, ligandNamePDB, charge, patchOutput):
    #check how to add net charge auto or by hand
    if AvogadroAuto == 'true': 
      call('cp '+root_path+'/source/acpype.py '+ patchOutput +'; cd '+ patchOutput+ '; python2.7 acpype.py -i '+ ligandNamePDB +' -n '+ str(charge) +'; rm acpype.py', shell=True, executable='/bin/bash');
    elif AvogadroAuto == 'false':  
      charge = raw_input("Enter net charge: ")
      call('cp '+root_path+'/source/acpype.py '+ patchOutput +'; cd '+ patchOutput+ '; python2.7 acpype.py -i '+ ligandNamePDB +' -n '+ str(charge) +'; rm acpype.py', shell=True, executable='/bin/bash');

  #**********************************************************************#
  #*************************** Prepare File *****************************#
  #**********************************************************************#

  def PrepareLigand(self):
    call('mkdir '+main_path+'/output/ligand/', shell=True)
    call('rm '+main_path+'/output/ligand/*', shell=True)
    
    ligands = Variable.parsepdb.Ligands
    index = 0
    for ligand in ligands:
      index+=1
      #Check name of ligands
      filename = os.path.basename(ligand.file_path)
      filename = filename.split('.pdb')[0]
      #Copy file from input to output
      ligand_name = os.path.basename(ligand.file_path)
      if(len(filename)>3 or filename[0].isdigit() == True):
        ligand_name = ("A%02d" % (index))+'.pdb'
        
      call('cp '+ligand.file_path +' '+ main_path+'/output/ligand/'+ ligand_name, shell=True)
      lg = parsePDB(main_path+'/output/ligand/'+ ligand_name)
      

      #Check if this pdb is protein => add 'protein_' before this to identify
      if (not lg.select('protein') is None) or (not lg.select('resname A U G T C') is None):
        self.CallCommand(main_path+'/output/ligand', 'mv '+ligand_name+' protein_'+ligand_name)
        continue

      #Add hydrogen to ligand
      AddHydrogen(main_path+'/output/ligand/'+ligand_name)

      #Count charge of ligand
      charge = self.CountCharge(main_path+'/output/ligand/'+ligand_name)

      #Set parameter (ff) for ligand
      self.SetParameter(main_path+'/output/ligand/'+ligand_name, charge, main_path+'/output/ligand')

  def PrepareLigandReceptor(self):
    ligands = ''
    try:
      ligands = check_output('cd '+main_path+'/output/receptor; ls ligand_*.pdb', shell = True).splitlines()
    except subprocess.CalledProcessError as e:

      for x in range(0,len(ligands)):
        #Add hydrogen to ligand
        AddHydrogen(main_path+'/output/receptor/'+ligands[x])

        #Count charge of ligand
        charge = self.CountCharge(main_path+'/output/receptor/'+ligands[x])

        #Set parameter (ff) for ligand
        self.SetParameter(ligands[x], charge, main_path+'/output/receptor')

  def PrepareCluster(self):
    global ReceptorChain
    ligands = check_output('cd '+main_path+'/output/ligand; ls *.pdb', shell = True).splitlines()
    #cp file vo run
    for x in range(0,len(ligands)):
      ligandName = ligands[x].split('.')[0]
      isProtein = False
      if 'protein_' in ligandName:
        isProtein = True
        ligandName = ligandName.split('_')[1]
        call('mkdir '+main_path+'/run/run_' + ligandName, shell = True)
        call('mkdir '+main_path+'/run/run_' + ligandName+'/mdp', shell = True)
        call('cp '+main_path+'/output/ligand/'+ligands[x]+' '+main_path+'/run/run_' + ligandName+'/'+ligandName+'.pdb', shell = True)
        call('cp -r '+root_path+'/config/* '+main_path+'/run/run_'+ligandName+'/mdp', shell = True)
      else:      
        call('mkdir '+main_path+'/run/run_' + ligandName, shell = True)
        call('mkdir '+main_path+'/run/run_' + ligandName+'/mdp', shell = True)
        call('cp -r '+main_path+'/output/ligand/'+ligandName+'.acpype '+main_path+'/run/run_'+ligandName, shell = True)
        call('cp -r '+root_path+'/config/* '+main_path+'/run/run_'+ligandName+'/mdp', shell = True)

      call('cp '+root_path+'/source/parse_pull.py '+main_path+'/run/run_'+ligandName, shell=True)
      call('cp '+root_path+'/source/MmPbSaStat.py '+main_path+'/run/run_'+ligandName, shell=True)
      call('cp -r '+main_path+'/output/receptor/*.acpype '+main_path+'/run/run_'+ligandName, shell = True)

      #Luu tung chain vao array de cong dong lai
      chains = []
      totalResidue = 0
      print ReceptorFile
      for numR in range(0, len(ReceptorFile)):
        chains.append(parsePDB(ReceptorFile[numR]+'.pdb'))
        ReceptorChain = ChainNames[numR]
        chainName = []
        for z in range(0, chains[numR].numAtoms()): 
          chainName.append(ChainNames[numR])
        chains[numR].setChids(chainName)
        #Find total residue to know where is starting of ligand (type protein)
        totalResidue += chains[numR].numResidues()

      #If ligand is protein => add it to pdb file 
      if isProtein == True:
        chains.append(parsePDB(main_path+'/output/ligand/'+ligands[x]))
        chainName = []
        for z in range(0, chains[numR+1].numAtoms()): 
          chainName.append(ChainNames[numR+1])
        chains[numR+1].setChids(chainName)
    
        file = open(main_path+'/run/run_' + ligandName+ '/ligand_residues.txt', 'w')
        file.close
        self.addLine(str(totalResidue)+'-'+str(totalResidue-1 + chains[numR+1].numResidues()),main_path+'/run/run_' + ligandName+ '/ligand_residues.txt')
      else: 
        call('rm '+main_path+'/run/run_' + ligandName + '/ligand_residues.txt', shell=True)

      #Check if /receptor has other protein or not
      try:
        proteins = check_output('cd '+main_path+'/output/receptor; ls protein*', shell = True).splitlines()
        for y in range(len(chains), len(proteins)+len(chains)):
          chains.append(parsePDB(main_path+'/output/receptor/'+proteins[y-len(chains)]))
          chainName = []
          for z in range(0, chains[y].numAtoms()): 
            chainName.append(ChainNames[y])
          chains[y].setChids(chainName)
      except subprocess.CalledProcessError as e:
        print 'ok'
      
      #Cong don protein lai thanh 1 file
      sumProtein = chains[0]
      for y in range(1, len(chains)):  
        if y > 0:
          sumProtein += chains[y]
   
      call('rm '+main_path+'/run/run_'+ligandName+'/protein.pdb', shell=True)
      call('rm '+main_path+'/run/run_'+ligandName+'/system.pdb', shell=True)
      if 'protein_' in ligandName:
        writePDB(main_path+'/run/run_'+ligandName.split('_')[1]+'/protein.pdb',sumProtein)
      else:
        writePDB(main_path+'/run/run_'+ligandName+'/protein.pdb',sumProtein)

  def EditMdpFile(self):
    runfolders = check_output('ls '+main_path+'/run/', shell = True).splitlines()
    for x in range(0,len(runfolders)):
      mdpFolder = main_path+'/run/'+runfolders[x]+'/mdp'

      nsteps = int(self.dataController.getdata('nvt-nsteps '))/0.002
      nstout = self.dataController.getdata('nvt-nst ')
      self.replaceLine('nsteps', 'nsteps     = '+str(nsteps)+'\n', mdpFolder+'/nvt.mdp')
      self.replaceLine('nstxout', 'nstxout     = '+str(nstout)+'\n', mdpFolder+'/nvt.mdp')
      self.replaceLine('nstvout', 'nstvout     = '+str(nstout)+'\n', mdpFolder+'/nvt.mdp')
      self.replaceLine('nstenergy', 'nstenergy     = '+str(nstout)+'\n', mdpFolder+'/nvt.mdp')
      self.replaceLine('nstlog', 'nstlog     = '+str(nstout)+'\n', mdpFolder+'/nvt.mdp')

      nsteps = int(self.dataController.getdata('npt-nsteps '))/0.002
      nstout = self.dataController.getdata('npt-nst ')
      self.replaceLine('nsteps', 'nsteps     = '+str(nsteps)+'\n', mdpFolder+'/npt.mdp')
      self.replaceLine('nstxout', 'nstxout     = '+str(nstout)+'\n', mdpFolder+'/npt.mdp')
      self.replaceLine('nstvout', 'nstvout     = '+str(nstout)+'\n', mdpFolder+'/npt.mdp')
      self.replaceLine('nstenergy', 'nstenergy     = '+str(nstout)+'\n', mdpFolder+'/npt.mdp')
      self.replaceLine('nstlog', 'nstlog     = '+str(nstout)+'\n', mdpFolder+'/npt.mdp')

      nsteps = int(self.dataController.getdata('md-nsteps '))/0.002
      nstout = self.dataController.getdata('md-nst ')
      self.replaceLine('nsteps', 'nsteps     = '+str(nsteps)+'\n', mdpFolder+'/md.mdp')
      self.replaceLine('nstxout', 'nstxout     = '+str(nstout)+'\n', mdpFolder+'/md.mdp')
      self.replaceLine('nstvout', 'nstvout     = '+str(nstout)+'\n', mdpFolder+'/md.mdp')
      self.replaceLine('nstxtcout', 'nstxtcout     = '+str(nstout)+'\n', mdpFolder+'/md.mdp')
      self.replaceLine('nstenergy', 'nstenergy     = '+str(nstout)+'\n', mdpFolder+'/md.mdp')
      self.replaceLine('nstlog', 'nstlog     = '+str(nstout)+'\n', mdpFolder+'/md.mdp')

      nsteps = int(self.dataController.getdata('smd-nsteps '))/0.002
      nstout = self.dataController.getdata('smd-nst ')
      vel_pull = self.dataController.getdata('smd-vel ')
      k_pull = self.dataController.getdata('smd-k ')
      if(GroVersion >= 5):
        mdp_pull_file = '/md_pull_5.mdp'
        self.replaceLine('pull-coord1-rate', 'pull-coord1-rate      = '+str(vel_pull)+'\n', mdpFolder+mdp_pull_file)
        self.replaceLine('pull-coord1-k', 'pull-coord1-k         = '+str(k_pull)+'\n', mdpFolder+mdp_pull_file)
      else:
        mdp_pull_file = '/md_pull.mdp'
        self.replaceLine('pull_rate1', 'pull_rate1      = '+str(vel_pull)+'\n', mdpFolder+mdp_pull_file)
        self.replaceLine('pull_k1', 'pull_k1         = '+str(k_pull)+'\n', mdpFolder+mdp_pull_file)

      self.replaceLine('nsteps', 'nsteps     = '+str(nsteps)+'\n', mdpFolder+mdp_pull_file)
      self.replaceLine('nstxout', 'nstxout     = '+str(nstout)+'\n', mdpFolder+mdp_pull_file)
      self.replaceLine('nstvout', 'nstvout     = '+str(nstout)+'\n', mdpFolder+mdp_pull_file)
      self.replaceLine('nstxtcout', 'nstxtcout     = '+str(nstout)+'\n', mdpFolder+mdp_pull_file)
      self.replaceLine('nstenergy', 'nstenergy     = '+str(nstout)+'\n', mdpFolder+mdp_pull_file)
      self.replaceLine('nstlog', 'nstlog     = '+str(nstout)+'\n', mdpFolder+mdp_pull_file)
      

  #**********************************************************************#
  #************************* Calc Fuction ****************************#
  #**********************************************************************#
  def RepresentsInt(self, s):
      try: 
          int(s)
          return True
      except ValueError:
          return False

  def setbox(self, patch, inputfile,outputfile, nRR, distance,ratio,ligandZ):
    print patch
    print inputfile
    print outputfile
    print nRR
    print distance
    print ratio
    print ligandZ
    #Read file
    system = Avogadro.MoleculeFile.readMolecule(patch+inputfile)
    
    #Find max and min falue System
    max = [-1000000.0,-1000000.0,-1000000.0]
    min = [1000000.0,1000000.0,1000000.0]
    proteinMax = -1000000
    systemCenter = [0,0,0]
    for x in range(0, system.numAtoms):
        atom = system.atom(x)
        pos_x = float(atom.pos[0])
        pos_y = float(atom.pos[1])
        pos_z = float(atom.pos[2])
        systemCenter += atom.pos
   
        if pos_x>max[0]:
          max[0] = pos_x
        if pos_x<min[0]:
          min[0] = pos_x

        if pos_y>max[1]:
          max[1] = pos_y
        if pos_y<min[1]:
          min[1] = pos_y

        if pos_z>max[2]:
          max[2] = pos_z
          if atom.residueId < nRR:
            proteinMax = pos_z
        if pos_z<min[2]: 
          min[2] = pos_z

    #Change distance
    distance *= 1.8

    #Check distance between ligand and maxZ protein
    dz = float(ligandZ) + float(distance) - float(proteinMax/10)
    if float(dz) < 0.0: 
      distance = '0'
    else:
      distance = str(dz)

    self.Log('distance',str(distance))
    self.Log('ligandZ',str(ligandZ))
    self.Log('proteinMax',str(proteinMax/10))

    #distance between protein and box
    Oxyz = [min[0]-14,min[1]-14,min[2]-14]
    d_x = (max[0]-min[0])/10 + 2.8
    d_y = (max[1]-min[1])/10 + 2.8
    d_z = (max[2]-min[2])/10 + 2.8 + float(distance) 
    systemCenter /= system.numAtoms
    systemCenter = (systemCenter - Oxyz)/10 
    systemCenter[2] += (1/(float(ratio)+1))*float(distance)

    self.Log('dz',str(d_z))
    self.Log('systemCenter', str(systemCenter[2]))
    self.Log('ratio',str(ratio))
      
    call('cd '+patch+';'+GroLeft+'editconf'+GroRight+' -f '+inputfile+' -o '+outputfile +' -box '+str(d_x)+' '+str(d_y)+' '+str(d_z)+ ' -center '+str(systemCenter[0])+' '+str(systemCenter[1])+' '+str(systemCenter[2]), shell=True, executable='/bin/bash') 


  def ParseIndex(self, indexFile):
    f = open(indexFile, "r")
    contents = f.readlines()
    f.close()

    groups = []
    for i in range(0, len(contents)):
      line = contents[i]
      if line[0:2] == '[ ':
        print line
        j = 0
        for k in range(0, len(groups)):
          if groups[j] == line.split('\n')[0]:
            contents[i] = '[ new_'+ contents[i][2:]
            break
          j+=1
        print str(len(groups)) + ' ' + str(j)
        if j >= len(groups):
          groups.append(line.split('\n')[0])
    print groups

    f = open(indexFile, "w")
    contents = "".join(contents)
    f.write(contents)
    f.close()

  def IndexHaveRNA(self, indexFile):
    if self.searchLine('RNA', indexFile) == '':
      return False
    else: 
      return True

  def IndexHaveDNA(self, indexFile):
    if self.searchLine('DNA', indexFile) == '':
      return False
    else: 
      return True

  def getMaxCoord(self, axe, obj, vectorPull):
    max = -1000000
    posAtom = 0
    for x in range(0,len(obj.getCoords())):
      if max < obj.getCoords()[x][axe]:
        max = self.rotatePoint(obj.getCoords()[x], vectorPull)[axe]
        posAtom = x

    return self.rotatePoint(obj.getCoords()[posAtom], vectorPull)

  def setupCaver(self, ligandCenter, filepdb):
    call('rm -r '+main_path+'/caver/input/*', shell=True)
    call('cp '+str(filepdb)+' '+main_path+'/caver/input', shell=True)
    coord_ligand = str(ligandCenter[0]) + ' ' + str(ligandCenter[1]) + ' ' + str(ligandCenter[2]) + '\n'
    self.replaceLine('starting_point_coordinates','starting_point_coordinates '+coord_ligand,main_path+'/caver/config.txt')
    call('cd '+main_path+'/caver; sh caver.sh', shell=True)

    outputFile = []
    try:
      outputFile = check_output('cd '+main_path+'/caver/out/data/clusters; ls *.pdb', shell = True).splitlines()
    except subprocess.CalledProcessError as e:
      return None
    tunel = parsePDB(main_path+'/caver/out/data/clusters/'+outputFile[0])
    tunelVector = tunel.getCoords()[tunel.numAtoms()-1] - tunel.getCoords()[tunel.numAtoms()-2]
    return tunelVector


  #**********************************************************************#
  #************************** System Fuction ****************************#
  #**********************************************************************#

  def CallCommand(self, patch, command):
    call('cd '+patch+'; '+command, shell = True, executable='/bin/bash')

  def substring(self, mystr, mylist): 
    return [i for i, val in enumerate(mylist) if mystr in val]

  def replaceLine(self, search, replace, myfile):
    f = open(myfile, "r")
    contents = f.readlines()
    f.close()

    contents[self.substring(search,contents)[0]] = replace

    f = open(myfile, "w")
    contents = "".join(contents)
    f.write(contents)
    f.close()

  def insertLine(self, search, position, insert, myfile):
    f = open(myfile, "r")
    contents = f.readlines()
    f.close()

    if len(self.substring(search,contents)) > 0:
      contents.insert(self.substring(search,contents)[0]+position, insert)
      f = open(myfile, "w")
      contents = "".join(contents)
      f.write(contents)
      f.close()
    else:
      self.addLine(insert, myfile)  

  def searchLine(self, search, myfile):
    f = open(myfile, "r")
    contents = f.readlines()
    f.close()
    if len(self.substring(search,contents)) > 0:
      return contents[self.substring(search,contents)[0]]
    else:
      return ''

  def addLine(self, line, myfile):
    with open(myfile, "a") as mf:
      mf.write(line)

  def Log(self, tag, comment):
    self.addLine(tag+ ' ' +comment+'\n', 'log.txt')


  #**********************************************************************#
  #************************* Rotation Fuction ****************************#
  #**********************************************************************#
  def rotatePoint(self, point, pullvec):
    pullr = math.sqrt(float(pullvec[0])**2 + float(pullvec[1])**2 + float(pullvec[2])**2) 
    pullphi = self.angle(float(pullvec[0]), float(pullvec[1]))
    pullxy = math.sqrt(float(pullvec[0])**2 + float(pullvec[1])**2)
    pulltheta = self.angle(float(pullvec[2]), float(pullxy) )
    self.rotateZ(point, pullphi)
    self.rotateY(point, pulltheta)
    return point

  #Fuction
  def angle(self, x, y):
    if x == 0.0:
      if y > 0.0:
        alpha = math.pi/2
      else:
        alpha = -math.pi/2
    elif x > 0.0: 
      alpha = math.atan(y/x)
    else: 
      if y > 0.0: 
        alpha = math.pi + math.atan(y/x)
      else:
        alpha = -math.pi + math.atan(y/x)
    return alpha

  def rotateZ(self, point, phi):
    point_r_xy = math.sqrt(point[0]**2 + point[1]**2) 
    point_phi = self.angle(point[0], point[1])

    point[0] = point_r_xy*math.cos(point_phi - phi)
    point[1] = point_r_xy*math.sin(point_phi - phi)
    return point

  def rotateY(self, point, theta):
    point_r_xz = math.sqrt(point[0]**2 + point[2]**2) 
    point_theta = self.angle(point[2], point[0])
     
    point[0] = point_r_xz*math.sin(point_theta - theta)
    point[2] = point_r_xz*math.cos(point_theta - theta)
    return point
  #***********************************************************************************#


  #**********************************************************************#
  #************************* Gromacs Fuction ****************************#
  #**********************************************************************#
  def SetupSystem(self):
    global GroLeft, GroRight
    runfolders = check_output('ls '+main_path+'/run/', shell = True).splitlines()
    for x in range(0,len(runfolders)):

      topolfile = main_path+'/run/'+runfolders[x]+'/topol.top'
      ligandCurrent = runfolders[x].split('_')[1] #A01
      try:
        ligandFolders = check_output('cd '+main_path+'/run/'+runfolders[x]+'; ls -d *.acpype', shell = True).splitlines()
      except subprocess.CalledProcessError as e:
        ligandFolders = []
      proteinfiles = check_output('cd '+main_path+'/run/'+runfolders[x]+'; ls protein*', shell = True).splitlines()

      #*****************************************************************************************************#
      #Add force field to protein
      #for y in range(0, len(proteinfiles)):
      #proteinname = proteinfiles[0].split(".")[0]
      self.CallCommand(main_path+'/run/'+runfolders[x],GroLeft+'pdb2gmx'+GroRight+' -ff '+ForceField+' -f protein.pdb -o protein.gro -water spce -missing -ignh')

      #if ligand is protein
      # if os.path.isfile('run/'+runfolders[x]+'/'+ligandCurrent+'.pdb') is True:
      #   self.CallCommand('run/'+runfolders[x],GroLeft+'pdb2gmx'+GroRight+' -ff '+ForceField+' -f '+ligandCurrent+'.pdb -o '+ligandCurrent+'.gro -water spce')

      #*****************************************************************************************************#
      #Merge *.gro file
      #Read file protein.gro
      proteingro = open(main_path+'/run/'+runfolders[x]+'/protein.gro', 'r')
      proteinData = proteingro.readlines()
      proteingro.close()
      
      for y in range(0, len(ligandFolders)):
        #Read file *.gro
        ligandName = ligandFolders[y].split('.')[0]
        gro = open(main_path+'/run/'+runfolders[x]+'/'+ligandFolders[y]+'/'+ligandName+'_GMX.gro', 'r')
        ligandData = gro.readlines()
        gro.close()

        #Change number of atoms and add atoms to bottom of protein.gro
        proteinData[1] = str(int(proteinData[1]) + int(ligandData[1])) + '\n'
        for line in ligandData[2:len(ligandData)-1]:
          proteinData.insert(len(proteinData)-1, line)

      #save to system.gro
      f = open(main_path+'/run/'+runfolders[x]+'/system.gro', "w")
      for item in proteinData:
        f.write(item)
      f.close()

      #*****************************************************************************************************#
      #Add atomtype and 
      atomtypes = []
      for y in range(0, len(ligandFolders)):
        #Read file *.itp
        ligandName = ligandFolders[y].split('.')[0]
        itp = open(main_path+'/run/'+runfolders[x]+'/'+ligandFolders[y]+'/'+ligandName+'_GMX.itp', 'r')
        itpline = itp.readlines()
        atomtypes.extend( itpline[self.substring('[ atomtypes ]',itpline)[0]: self.substring('[ moleculetype ]',itpline)[0]] )
     
        #save other part to ligand_topology.itp
        atomtopologys = []
        atomtopologys = itpline[self.substring('[ moleculetype ]',itpline)[0]:]
        itp.close()
   
        f = open(main_path+'/run/'+runfolders[x]+'/'+ligandName+'.itp', "w")
        for item in atomtopologys:
          f.write(item)
        f.close()

        #add ligand_topology.itp to topol.top
        if y == 0: self.insertLine('; Include water topology', -1, '\n; Include ligand topology \n', topolfile)
        self.insertLine('; Include water topology', -1, '#include "'+ligandName+'.itp" \n', topolfile)

        #add molecular to bottom of topol.top
        self.addLine(ligandName+'                 1\n', topolfile)

      #save atomtypes to ligand_atomtypes.itp
      f = open(main_path+'/run/'+runfolders[x]+'/ligand_atomtypes.itp', "w")
      for item in atomtypes:
        f.write(item)
      f.close()
   
      #add ligand_atomtypes.itp to topol.top
      self.insertLine('; Include forcefield parameters', 2, '#include "ligand_atomtypes.itp" \n', topolfile)

      #*****************************************************************************************************#
      #setup Box
      if os.path.isfile(main_path+'/run/'+runfolders[x]+'/'+ligandCurrent+'.acpype/'+ligandCurrent+'.pdb') is True:
        ligand = parsePDB(main_path+'/run/'+runfolders[x]+'/'+ligandCurrent+'.acpype/'+ligandCurrent+'.pdb')
      else:
        ligand = parsePDB(main_path+'/run/'+runfolders[x]+'/'+ligandCurrent+'.pdb')
      ligandCenter = calcCenter(ligand)

      #check if user want to use caver
      if run_caver == 'y':
        vectorPull = self.setupCaver(ligandCenter, main_path+'/run/'+runfolders[x]+'/protein.pdb')
        if vectorPull is None:
          vectorPull = ligandCenter - ReceptorCenter
      else:
        vectorPull = ligandCenter - ReceptorCenter
      self.Log('ligandCenter',str(ligandCenter))
      self.Log('ReceptorCenter',str(ReceptorCenter))

      call('cp '+root_path+'/source/rotate.py '+main_path+'/run/'+runfolders[x]+'/', shell = True)
      self.CallCommand(main_path+'/run/'+runfolders[x]+'/', 'python2.7 rotate.py -i system.gro -o rotate_system.gro -v '+str(vectorPull[0])+','+str(vectorPull[1])+','+str(vectorPull[2]))
      
      #*****************************************************************************************************#
      #set Boxsize
      #read distance 
      pullspeed = float(self.searchLine('pull_rate1', main_path+'/run/'+runfolders[x]+'/mdp/md_pull.mdp').split("=")[1].split(';')[0])
      pulltime = float(self.searchLine('nsteps', main_path+'/run/'+runfolders[x]+'/mdp/md_pull.mdp').split("=")[1].split(';')[0])*float(self.searchLine('dt', main_path+'/run/'+runfolders[x]+'/mdp/md_pull.mdp').split("=")[1].split(';')[0])
      distance = pullspeed*pulltime

      #Calc ratio of receptor/ligand
      if os.path.isfile(main_path+'/run/'+runfolders[x]+'/'+ligandCurrent+'.acpype/'+ligandCurrent+'.pdb') is True:
        ligand = parsePDB(main_path+'/run/'+runfolders[x]+'/'+ligandCurrent+'.acpype/'+ligandCurrent+'.pdb')
      else:
        ligand = parsePDB(main_path+'/run/'+runfolders[x]+'/'+ligandCurrent+'.pdb')
      ligandNumAtom = ligand.numAtoms()

      self.Log('number atom', str(ReceptorNumAtom) + ' ' + str(ligandNumAtom))
      ratio = float(float(ReceptorNumAtom)/float(ligandNumAtom))
      ligandMax = self.getMaxCoord(2, ligand, vectorPull)
      receptor = Avogadro.MoleculeFile.readMolecule(main_path+'/run/'+runfolders[x]+'/protein.gro')
      self.setbox(main_path+'/run/'+runfolders[x]+'/', 'rotate_system.gro', 'newbox.gro', receptor.numResidues, distance, ratio, ligandMax[2]/10)
      
      #Add solv
      if GroVersion >=5:
        self.CallCommand(main_path+'/run/'+runfolders[x],GroLeft+'solvate'+GroRight+' -cp newbox.gro -cs spc216.gro -p topol.top -o solv.gro')
      else:
        self.CallCommand(main_path+'/run/'+runfolders[x],GroLeft+'genbox'+GroRight+' -cp newbox.gro -cs spc216.gro -p topol.top -o solv.gro')
      
  def runGromacs(self):
    runfolders = check_output('ls '+main_path+'/run/', shell = True).splitlines()
    for x in range(0,len(runfolders)):
      # Check point to show log
      CheckPoint.point = runfolders[x]

      run_path = main_path+'/run/'+runfolders[x]
      #Add ions to solv 
      #self.CallCommand('run/'+runfolders[x], 'cp solv.gro solv_ions.gro')
      self.CallCommand(run_path, GroLeft+'grompp'+GroRight+' -maxwarn 10 -f mdp/ions.mdp -c solv.gro -p topol.top -o ions.tpr')
      self.CallCommand(run_path, 'echo -e \"SOL\"|' +GroLeft+'genion'+GroRight+' -s ions.tpr -o solv_ions.gro -p topol.top -pname NA -nname CL -neutral -conc 0.1')

      #Create index file for first time => check double name
      self.CallCommand(run_path, 'echo -e \"q\\n\" | '+ GroLeft+'make_ndx'+GroRight+' -f solv_ions.gro -o index.ndx') 
      self.ParseIndex(run_path+'/index.ndx')

      #*****************************************************************************************************#
      #Chang file mdp
      try:
        ligandFolders = check_output('cd '+run_path+'; ls -d *.acpype', shell = True).splitlines()
      except subprocess.CalledProcessError as e:
        ligandFolders = []

      replace_1 = 'energygrps      = Protein' 
      replace_2 = 'tc-grps         = Protein' 
      replace_3 = 'tau_t           = 0.1 0.1'
      replace_4 = 'ref_t           = 300 300'
      for y in range(0, len(ligandFolders)):
        #Lay resname cua ligand, ex: FAD, A01
        ligandName = ligandFolders[y].split('.')[0]
        ligand = Avogadro.MoleculeFile.readMolecule(run_path+'/'+ligandFolders[y]+'/'+ligandName+'.pdb')
        resname = ligand.residues[0].name
        replace_1 += ' '+resname
        replace_2 += '_'+resname

      #Check index have RNA or not 
      if self.IndexHaveRNA(run_path+'/index.ndx') == True:
        replace_1 += ' RNA'
        replace_2 += ' RNA'
        replace_3 += ' 0.1'
        replace_4 += ' 300'     
      elif self.IndexHaveDNA(run_path+'/index.ndx') == True:
        replace_1 += ' DNA'
        replace_2 += ' DNA'
        replace_3 += ' 0.1'
        replace_4 += ' 300'     

      replace_1 += '\n'
      replace_2 += ' Water_and_ions\n'
      replace_3 += '\n'
      replace_4 += '\n'
       
      self.replaceLine('energygrps', replace_1, run_path+'/mdp/minim.mdp')
      self.replaceLine('energygrps', replace_1, run_path+'/mdp/nvt.mdp')
      self.replaceLine('energygrps', replace_1, run_path+'/mdp/npt.mdp')
      self.replaceLine('energygrps', replace_1, run_path+'/mdp/md.mdp')
      self.replaceLine('energygrps', replace_1, run_path+'/mdp/md_pull.mdp')
      self.replaceLine('energygrps', replace_1, run_path+'/mdp/md_pull_5.mdp')
      self.replaceLine('energygrps', replace_1, run_path+'/mdp/md_md.mdp')

      self.replaceLine('tc-grps', replace_2, run_path+'/mdp/nvt.mdp')
      self.replaceLine('tc-grps', replace_2, run_path+'/mdp/npt.mdp')
      self.replaceLine('tc-grps', replace_2, run_path+'/mdp/md.mdp')
      self.replaceLine('tc-grps', replace_2, run_path+'/mdp/md_pull.mdp') 
      self.replaceLine('tc-grps', replace_2, run_path+'/mdp/md_pull_5.mdp') 
      self.replaceLine('tc-grps', replace_2, run_path+'/mdp/md_md.mdp') 

      self.replaceLine('tau_t', replace_3, run_path+'/mdp/nvt.mdp')
      self.replaceLine('tau_t', replace_3, run_path+'/mdp/npt.mdp')
      self.replaceLine('tau_t', replace_3, run_path+'/mdp/md.mdp')
      self.replaceLine('tau_t', replace_3, run_path+'/mdp/md_pull.mdp') 
      self.replaceLine('tau_t', replace_3, run_path+'/mdp/md_pull_5.mdp') 
      self.replaceLine('tau_t', replace_3, run_path+'/mdp/md_md.mdp') 

      self.replaceLine('ref_t', replace_4, run_path+'/mdp/nvt.mdp')
      self.replaceLine('ref_t', replace_4, run_path+'/mdp/npt.mdp')
      self.replaceLine('ref_t', replace_4, run_path+'/mdp/md.mdp')
      self.replaceLine('ref_t', replace_4, run_path+'/mdp/md_pull.mdp') 
      self.replaceLine('ref_t', replace_4, run_path+'/mdp/md_pull_5.mdp') 
      self.replaceLine('ref_t', replace_4, run_path+'/mdp/md_md.mdp') 

      #Find group, merge group, create group to index file
      #*********************************************************************************
      #create group receptor
      mergeGroup = ''
      nameOfGroup = ''
      nameOfLigand = ''
      if int(Method) == 1 or int(Method) == 2:
        system = Avogadro.MoleculeFile.readMolecule(run_path+'/newbox.gro')

        for y in range(0,len(ReceptorResidues)):
          receptorResidue = ReceptorResidues[y]
          ResStart = receptorResidue.split(':')[0]
          ResEnd = receptorResidue.split(':')[1]

          print receptorResidue

          AtomStart = system.residues[int(ResStart)].atoms[0]+1
          AtomEnd = system.residues[int(ResEnd)].atoms[len(system.residues[int(ResEnd)].atoms)-1]+1
          if(y != 0):
           mergeGroup += ' | '
           nameOfGroup += '_'
          mergeGroup += 'a '+str(AtomStart)+'-'+str(AtomEnd)
          nameOfGroup += 'a_'+str(AtomStart)+'-'+str(AtomEnd)
        mergeGroup += '\\n'

        #Check if ligand is protein => add index
        if os.path.isfile(run_path+'/ligand_residues.txt') is True: 
          f = open(run_path+'/ligand_residues.txt', "r")
          contents = f.readlines()
          f.close()
          print contents[0]
          print system.numResidues
          AtomStart = system.residues[int(contents[0].split('-')[0])].atoms[0]+1
          AtomEnd = system.residues[int(contents[0].split('-')[1])].atoms[len(system.residues[int(contents[0].split('-')[1])].atoms)-1]+1
          mergeGroup += 'a '+ str(AtomStart)+'-'+str(AtomEnd) +'\\n'
          nameOfLigand = 'a_'+ str(AtomStart)+'-'+str(AtomEnd)


      #Add group to index and Create posre
      topolfile = run_path+'/topol.top'
      indexfile = run_path+'/index.ndx'
      try:
        ligandFolders = check_output('cd '+run_path+'; ls -d *.acpype', shell = True).splitlines()
      except subprocess.CalledProcessError as e:
        ligandFolders = []
      ligandCurrent = runfolders[x].split('_')[1] #A01

      #ex: Protein_A01_FDA group
      mergeGroup += '\\"protein\\"'
      for y in range(0, len(ligandFolders)):
        ligandName = ligandFolders[y].split('.')[0]
        ligand = Avogadro.MoleculeFile.readMolecule(run_path+'/'+ligandFolders[y]+'/'+ligandName+'.pdb')
        resname = ligand.residues[0].name
        self.CallCommand(run_path, 'echo -e \"'+resname+'\\n\" | '+GroLeft+'genrestr'+GroRight+' -f '+ligandName+'.acpype/'+ligandName+'_GMX.gro -o posre_'+ligandName+'.itp -fc 1000 1000 1000')
        self.insertLine(ligandName+'.itp', 1, '#ifdef POSRES \n#include "posre_'+ligandName+'.itp" \n#endif \n', topolfile)

        mergeGroup += ' | \\"' + resname +'\\"'
      self.CallCommand(run_path, 'echo -e \"'+mergeGroup +'\\nq\\n\" | '+ GroLeft+'make_ndx'+GroRight+' -f solv_ions.gro -n index.ndx') 
      print 'echo -e \"'+mergeGroup +'\\nq\\n\" | '+ GroLeft+'make_ndx'+GroRight+' -f solv_ions.gro -n index.ndx'
      #Change water to water_and_ions in index.ndx
      #replaceLine('[ Water ]', '[ Water_and_ions ]\n', indexfile)

      #change name of group
      if int(Method) == 1 or int(Method) == 2:
        self.replaceLine(nameOfGroup, '[ Receptor ]\n', indexfile)
      if os.path.isfile(run_path+'/ligand_residues.txt') is True: 
        self.replaceLine(nameOfLigand, '[ '+ligandCurrent+' ]\n', indexfile)
      #*********************************************************************************

      groCmd = ''
      #Run em
      if os.path.isfile(run_path+'/em.gro') is False: 
        groCmd += GroLeft+'grompp'+GroRight+' -maxwarn 20 -f mdp/minim.mdp -c solv_ions.gro -p topol.top -o em.tpr \n'
        groCmd += GroLeft+'mdrun'+GroRight+' '+GroOption+' -v -deffnm em \n'
      
      #Run nvt
      if os.path.isfile(run_path+'/nvt.gro') is False: 
        groCmd += GroLeft+'grompp'+GroRight+' -maxwarn 20 -f mdp/nvt.mdp -c em.gro -p topol.top -n index.ndx -o nvt.tpr \n'
        groCmd += GroLeft+'mdrun'+GroRight+ ' '+GroOption+ ' -deffnm nvt -v \n'

      #Run npt
      if os.path.isfile(run_path+'/npt.gro') is False: 
        groCmd += GroLeft+'grompp'+GroRight+' -maxwarn 20 -f mdp/npt.mdp -c nvt.gro -t nvt.cpt -p topol.top -n index.ndx -o npt.tpr \n'
        groCmd += GroLeft+'mdrun'+GroRight+ ' '+GroOption+ ' -deffnm npt -v \n'

      #Run md
      if os.path.isfile(run_path+'/md.gro') is False:
        groCmd += GroLeft+'grompp'+GroRight+ ' -maxwarn 20 -f mdp/md.mdp -c npt.gro -t npt.cpt -p topol.top -n index.ndx -o md.tpr \n'
        groCmd += GroLeft+'mdrun'+GroRight+ ' '+GroOption+ ' -deffnm md -v \n'
      
      if int(Method) == 1:
        if (int(repeat_times) == 1 or int(repeat_times) == 0 ):
          if(GroVersion >= 5):
            self.replaceLine('pull-group2-name', 'pull-group2-name     = '+ligandCurrent+'\n', run_path+'/mdp/md_pull_5.mdp')
            groCmd += GroLeft+'grompp'+GroRight+ ' -maxwarn 20 -f mdp/md_pull_5.mdp -c md.gro -t md.cpt -p topol.top -n index.ndx -o md_1.tpr \n'
          else:
            self.replaceLine('pull_group1', 'pull_group1     = '+ligandCurrent+'\n', run_path+'/mdp/md_pull.mdp')
            groCmd += GroLeft+'grompp'+GroRight+ ' -maxwarn 20 -f mdp/md_pull.mdp -c md.gro -t md.cpt -p topol.top -n index.ndx -o md_1.tpr \n'
          
          groCmd += GroLeft+'mdrun'+GroRight+ ' '+GroOption+ ' -px pullx.xvg -pf pullf.xvg -deffnm md_1 -v \n'
        else:
          # Repeat the steered for times
          if(GroVersion >= 5):
            self.CallCommand(run_path, 'cp mdp/md_pull_5.mdp mdp/md_pull_repeat.mdp')
            self.replaceLine('continuation', 'continuation  = no   ; Restarting after NPT\n', run_path+'/mdp/md_pull_repeat.mdp')
            self.replaceLine('gen_vel','gen_vel   = yes\ngen_temp = 300\ngen_seed = -1\n', run_path+'/mdp/md_pull_repeat.mdp')
            self.replaceLine('pull-group2-name', 'pull-group2-name     = '+ligandCurrent+'\n', run_path+'/mdp/md_pull_repeat.mdp')
          else:
            self.CallCommand(run_path, 'cp mdp/md_pull.mdp mdp/md_pull_repeat.mdp')
            self.replaceLine('continuation', 'continuation  = no   ; Restarting after NPT\n', run_path+'/mdp/md_pull_repeat.mdp')
            self.replaceLine('gen_vel','gen_vel   = yes\ngen_temp = 300\ngen_seed = -1\n', run_path+'/mdp/md_pull_repeat.mdp')
            self.replaceLine('pull_group1', 'pull_group1     = '+ligandCurrent+'\n', run_path+'/mdp/md_pull_repeat.mdp')
          
          for k in range(0,int(repeat_times)):
            if os.path.isfile(run_path+'/md_1_'+str(k)+'.gro') is False:
              groCmd += GroLeft+'grompp'+GroRight+ ' -maxwarn 20 -f mdp/md_pull_repeat.mdp -c md.gro -t md.cpt -p topol.top -n index.ndx -o md_1_'+str(k)+'.tpr \n'
              groCmd += GroLeft+'mdrun'+GroRight+ ' '+GroOption+ ' -px pullx_'+str(k)+'.xvg -pf pullf_'+str(k)+'.xvg -deffnm md_1_'+str(k)+' -v \n'
              groCmd += 'python2.7 parse_pull.py -x pullx_'+str(k)+'.xvg -f pullf_'+str(k)+'.xvg -o pullfx_'+str(k)+'.xvg\n'
        
      # elif int(Method) == 2:
      #   if os.path.isfile(run_path+'/md_2.gro') is False:
      #     groCmd += GroLeft+'grompp'+GroRight+ ' -maxwarn 20 -f mdp/md_md.mdp -c md.gro -t md.cpt -p topol.top -n index.ndx -o md_2.tpr \n'
      #     groCmd += GroLeft+'mdrun'+GroRight+ ' '+GroOption+ ' -deffnm md_2 -v \n'

      #   groCmd += 'export OMP_NUM_THREADS=4\n'
      #   groCmd += 'echo -e \"Receptor\\n'+ligandCurrent+'\\n\" | g_mmpbsa -f md_2.trr -b 100 -dt 20 -s md_2.tpr -n index.ndx -pdie 2 -decomp \n'
      #   groCmd += 'echo -e \"Receptor\\n'+ligandCurrent+'\\n\" | g_mmpbsa -f md_2.trr -b 100 -dt 20 -s md_2.tpr -n index.ndx -i mdp/polar.mdp -nomme -pbsa -decomp \n'
      #   groCmd += 'echo -e \"Receptor\\n'+ligandCurrent+'\\n\" | g_mmpbsa -f md_2.trr -b 100 -dt 20 -s md_2.tpr -n index.ndx -i mdp/apolar_sasa.mdp -nomme -pbsa -decomp -apol sasa.xvg -apcon sasa_contrib.dat \n'
      #   groCmd += 'python2.7 MmPbSaStat.py -m energy_MM.xvg -p polar.xvg -a sasa.xvg \n'

      self.CallCommand(run_path, groCmd)

  #**********************************************************************#
  #**************************** Main Fuction ****************************#                                                                                                                  
  #**********************************************************************#

  def main(self):
    self.ParsePDBInput()
    self.setupOptions()   
    # if run_nohup == 'y':
    #   call('nohup python2.7 labpi.py &', shell=True)              
    # else:
    self.PrepareLigand()
    self.PrepareLigandReceptor()
    self.PrepareCluster()
    self.EditMdpFile()
    self.SetupSystem()
    self.runGromacs()














