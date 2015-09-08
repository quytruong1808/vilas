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
from source.parsePdb import Variable
from source.Utils import PdbFile
from source.Utils import DataController


AminoAcid = ["ALA", "ARG", "ASN", "ASP", "CYS", "GLU", "GLN", "GLY", "HIS", "ILE", "LEU", "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL", "SEC", "PYL", "ASX", "GLX", "XLE", "XAA"]
ChainNames = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','P','Q','R','S','T','U','V','Y','Z']
ForceField = 'amber99sb'
GroLeft  = ''
GroRight = ''
GroOption = ''
GroVersion = '0'
AvogadroAuto = ''
run_caver = ''
run_nohup = ''
repeat_times = '0'
Method = ''

ReceptorCenter = []
ReceptorFile = []
LigandFile = []



class GromacsRun(object):
  dataController = DataController()

  #**********************************************************************#
  #***************************** Prepare Fuction ************************#
  #**********************************************************************#

  def ParsePDBInput():
    Receptors = Variable.parsepdb.Receptors
    Ligands = Variable.parsepdb.Ligands

    #Export receptor to seperate pdb file
    root_path = self.dataController.getdata('path ')
    call('rm ' + root_path +'/output/receptor/*', shell=True)

    global ReceptorCenter, ReceptorFile, ReceptorNumAtom, ReceptorResidues
    
    ResidueNumber = 0
    lastResidueId = 0
    listCenter = [0,0,0] 

    for receptor in Receptors:
      filename = os.path.basename(receptor.path)
      for chain in receptor.chains:

        if chain.chain_type == 'protein': 
          protein = chain.chain_view
          
          fileName = root_path + '/output/receptor/receptor_' + filename + "_" + str(protein) 
          writePDB( fileName.replace(" ", ""), protein)
          
          if chain.is_group == True:
            #If parameter residues is enable
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
          fileName = root_path + '/output/receptor/ligand_' +  filename + "_" + str(ligand.getResnames()[0])
          writePDB(fileName.replace(" ", ""), ligand)

    ReceptorCenter = listCenter/ResidueNumber




  #Check version of gromacs 
  #Check_out to read, call to call :))
  #Chon version gromacs tuong ung
  def ChooseVersionGromacs():
    print '\n******************************************************'
    print "Which version do you want to use? "
    commands_1 = check_output("compgen -ac | grep mdrun", shell=True, executable='/bin/bash').splitlines()
    if len(commands_1) > 1:
      for x in range(0, len(commands_1)):
        print "{0:2d} => {1:15s}".format(x,str(commands_1[x]))

      if searchLine(TAG_GROMACS, 'parameter.txt') == '':
        index = raw_input("Enter version: ")
        insertLine(TAG_GROMACS, 0, TAG_GROMACS +' = ' +index+'\n', 'parameter.txt')
      else:
        index = searchLine(TAG_GROMACS, 'parameter.txt').split(' = ')[1].replace(' ', '').split('\n')[0]

      print "You choosed: " + str(commands_1[int(index)])
    else: 
      index = 0
    version_array = str(commands_1[int(index)]).split('mdrun')
    global GroLeft, GroRight
    GroLeft = version_array[0]
    GroRight = version_array[1]

    commands_2 = check_output(str(commands_1[int(index)]) + " -version", shell=True, executable='/bin/bash').splitlines()
    for x in range(0, len(commands_2)):
      if 'VERSION ' in commands_2[x]:
        global GroVersion
        GroVersion = commands_2[x].split('VERSION ')[1]
        break

    print '\n******************************************************'
    print "Option for openMP, openMPI or GPU? enter for default\nex: -ntomp 4 -gpu_id 0"
    global GroOption 

    if searchLine(TAG_OPTION, 'parameter.txt') == '':
      GroOption = raw_input("Enter option: ")
      insertLine(TAG_OPTION, 0, TAG_OPTION +' = ' +GroOption+'\n', 'parameter.txt')
    else:
      GroOption = searchLine(TAG_OPTION, 'parameter.txt').split(' = ')[1].split('\n')[0]

  def OptionalProgram():
    print '\n******************************************************'
    print "Do you want to find vector pull with caver ?\n"
    global run_caver
    while (run_caver != 'y' and run_caver != 'n'):
      if searchLine(TAG_CAVER, 'parameter.txt') == '':
        run_caver = raw_input("Enter (y/n): ")
        if run_caver == 'y' or run_caver == 'n':
          insertLine(TAG_CAVER, 0, TAG_CAVER +' = ' +run_caver.replace(' ','')+'\n', 'parameter.txt')
      else:
        run_caver = searchLine(TAG_CAVER, 'parameter.txt').split(' = ')[1].split('\n')[0]

    if int(Method) == 1:
      print '\n******************************************************'
      print "How many times do you want to repeat ?\n"
      global repeat_times
      while (RepresentsInt(repeat_times) == False or repeat_times == '0'):
        if searchLine(TAG_REPEAT, 'parameter.txt') == '':
          repeat_times = raw_input("Times (1,2,3): ")
          if(RepresentsInt(repeat_times) == True):
            insertLine(TAG_REPEAT, 0, TAG_REPEAT +' = ' +repeat_times.replace(' ','')+'\n', 'parameter.txt')
        else:
          repeat_times = searchLine(TAG_REPEAT, 'parameter.txt').split(' = ')[1].split('\n')[0]

    print '\n******************************************************'
    print "Do you want to run with 'nohup' ?\n"
    global run_nohup
    while (run_nohup != 'y' and run_nohup != 'n'):
      if searchLine(TAG_NOHUP, 'parameter.txt') == '':
        run_nohup = raw_input("Enter (y/n): ")
        if run_nohup == 'y':
          insertLine(TAG_NOHUP, 0, TAG_NOHUP +' = ' +run_nohup.replace(' ','')+'\n', 'parameter.txt')
      else:
        run_nohup = searchLine(TAG_NOHUP, 'parameter.txt').split(' = ')[1].split('\n')[0]
        #If nohup == yes => just run nohup for this time, next time ask user again for run nohup
        if run_nohup == 'y':
          run_nohup = 'n'
          replaceLine(TAG_NOHUP, '', 'parameter.txt')




  #**********************************************************************#
  #************************* Ligand Fuction *****************************#
  #**********************************************************************#
  def AddHydrogen(ligandFile):
    #Check add hydro by hand or auto
    global AvogadroAuto
    again = 'true'
    while(again == 'true'):
      again = 'false'
      if AvogadroAuto == '':
        print "\n"
        print "Do you want to add hydrogen automatically or manually"
        print " 0 => automatic"
        print " 1 => manual"

        if searchLine(TAG_AUTO, 'parameter.txt') == '':
          index = raw_input("Enter method: ")
          insertLine(TAG_AUTO, 0, TAG_AUTO +' = ' +index+'\n', 'parameter.txt')
        else:
          index = searchLine(TAG_AUTO, 'parameter.txt').split(' = ')[1].replace(' ', '')

        method = int(index)  
        if method == 0: 
          AvogadroAuto = 'true'
        elif method == 1:
          AvogadroAuto = 'false'
        else:
          again = 'true'      

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


  def CountCharge(ligandFile):
    ligand = Avogadro.MoleculeFile.readMolecule(ligandFile)
    sumCharge = 0
    for atom in ligand.atoms:
      sumCharge += atom.partialCharge

    return int(round(sumCharge, 0))
    
  def SetParameter(ligandNamePDB, charge, patchOutput):
    #check how to add net charge auto or by hand
    if AvogadroAuto == 'true': 
      call('cp source/acpype.py '+ patchOutput +'; cd '+ patchOutput+ '; python2.7 acpype.py -i '+ ligandNamePDB +' -n '+ str(charge) +'; rm acpype.py', shell=True, executable='/bin/bash');
    elif AvogadroAuto == 'false':  
      charge = raw_input("Enter net charge: ")
      call('cp source/acpype.py '+ patchOutput +'; cd '+ patchOutput+ '; python2.7 acpype.py -i '+ ligandNamePDB +' -n '+ str(charge) +'; rm acpype.py', shell=True, executable='/bin/bash');

  #**********************************************************************#
  #*************************** Prepare File *****************************#
  #**********************************************************************#

  def PrepareLignad():
    ligands = check_output('cd input/ligand; ls *.pdb', shell = True).splitlines()
    call('mkdir output/ligand/', shell=True)
    call('rm output/ligand/*', shell=True)
    for x in range(0,len(ligands)):

      #Copy file from input to output
      call('cp input/ligand/'+ligands[x]+' output/ligand', shell=True)

      #Check if this pdb is protein => add 'protein_' before this to identify
      ligand = parsePDB('output/ligand/'+ligands[x])
      if (not ligand.select('protein') is None) or (not ligand.select('resname A U G T C') is None):
        CallCommand('output/ligand', 'mv '+ligands[x]+' protein_'+ligands[x])
        continue

      #Add hydrogen to ligand
      AddHydrogen('output/ligand/'+ligands[x])

      #Count charge of ligand
      charge = CountCharge('output/ligand/'+ligands[x])

      #Set parameter (ff) for ligand
      SetParameter(ligands[x], charge, 'output/ligand')

  def PrepareLigandReceptor():
    ligands = ''
    try:
      ligands = check_output('cd output/receptor; ls ligand_*.pdb', shell = True).splitlines()
    except subprocess.CalledProcessError as e:

      for x in range(0,len(ligands)):
        #Add hydrogen to ligand
        AddHydrogen('output/receptor/'+ligands[x])

        #Count charge of ligand
        charge = CountCharge('output/receptor/'+ligands[x])

        #Set parameter (ff) for ligand
        SetParameter(ligands[x], charge, 'output/receptor')

  def PrepareCluster():
    global ReceptorChain
    ligands = check_output('cd output/ligand; ls *.pdb', shell = True).splitlines()
    #cp file vo run
    for x in range(0,len(ligands)):
      ligandName = ligands[x].split('.')[0]
      isProtein = False
      if 'protein_' in ligandName:
        isProtein = True
        ligandName = ligandName.split('_')[1]
        call('mkdir run/run_' + ligandName, shell = True)
        call('mkdir run/run_' + ligandName+'/mdp', shell = True)
        call('cp output/ligand/'+ligands[x]+' run/run_' + ligandName+'/'+ligandName+'.pdb', shell = True)
        call('cp -r config/* run/run_'+ligandName+'/mdp', shell = True)
      else:      
        call('mkdir run/run_' + ligandName, shell = True)
        call('mkdir run/run_' + ligandName+'/mdp', shell = True)
        call('cp -r output/ligand/'+ligandName+'.acpype run/run_'+ligandName, shell = True)
        call('cp -r config/* run/run_'+ligandName+'/mdp', shell = True)

      call('cp source/parse_pull.py run/run_'+ligandName, shell=True)
      call('cp source/MmPbSaStat.py run/run_'+ligandName, shell=True)
      call('cp -r output/receptor/*.acpype run/run_'+ligandName, shell = True)

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
        chains.append(parsePDB('output/ligand/'+ligands[x]))
        chainName = []
        for z in range(0, chains[numR+1].numAtoms()): 
          chainName.append(ChainNames[numR+1])
        chains[numR+1].setChids(chainName)
    
        file = open('run/run_' + ligandName+ '/ligand_residues.txt', 'w')
        file.close
        addLine(str(totalResidue)+'-'+str(totalResidue-1 + chains[numR+1].numResidues()),'run/run_' + ligandName+ '/ligand_residues.txt')
      else: 
        call('rm run/run_' + ligandName + '/ligand_residues.txt', shell=True)

      #Check if /receptor has other protein or not
      try:
        proteins = check_output('cd output/receptor; ls protein*', shell = True).splitlines()
        for y in range(len(chains), len(proteins)+len(chains)):
          chains.append(parsePDB('output/receptor/'+proteins[y-len(chains)]))
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
   
      call('rm run/run_'+ligandName+'/protein.pdb', shell=True)
      call('rm run/run_'+ligandName+'/system.pdb', shell=True)
      if 'protein_' in ligandName:
        writePDB('run/run_'+ligandName.split('_')[1]+'/protein.pdb',sumProtein)
      else:
        writePDB('run/run_'+ligandName+'/protein.pdb',sumProtein)


  #**********************************************************************#
  #************************* Calc Fuction ****************************#
  #**********************************************************************#
  def RepresentsInt(s):
      try: 
          int(s)
          return True
      except ValueError:
          return False

  def setbox(patch, inputfile,outputfile, nRR, distance,ratio,ligandZ):
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

    Log('distance',str(distance))
    Log('ligandZ',str(ligandZ))
    Log('proteinMax',str(proteinMax/10))

    #distance between protein and box
    Oxyz = [min[0]-14,min[1]-14,min[2]-14]
    d_x = (max[0]-min[0])/10 + 2.8
    d_y = (max[1]-min[1])/10 + 2.8
    d_z = (max[2]-min[2])/10 + 2.8 + float(distance) 
    systemCenter /= system.numAtoms
    systemCenter = (systemCenter - Oxyz)/10 
    systemCenter[2] += (1/(float(ratio)+1))*float(distance)

    Log('dz',str(d_z))
    Log('systemCenter', str(systemCenter[2]))
    Log('ratio',str(ratio))
      
    print 'editconf_mpi -f '+inputfile+' -o '+patch+outputfile +' -box '+str(d_x)+' '+str(d_y)+' '+str(d_z)+ ' -center '+str(systemCenter[0])+' '+str(systemCenter[1])+' '+str(systemCenter[2])
    call('cd '+patch+';'+GroLeft+'editconf'+GroRight+' -f '+inputfile+' -o '+outputfile +' -box '+str(d_x)+' '+str(d_y)+' '+str(d_z)+ ' -center '+str(systemCenter[0])+' '+str(systemCenter[1])+' '+str(systemCenter[2]), shell=True, executable='/bin/bash') 


  def ParseIndex(indexFile):
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

  def IndexHaveRNA(indexFile):
    if searchLine('RNA', indexFile) == '':
      return False
    else: 
      return True

  def IndexHaveDNA(indexFile):
    if searchLine('DNA', indexFile) == '':
      return False
    else: 
      return True

  def getMaxCoord(axe, obj, vectorPull):
    max = -1000000
    posAtom = 0
    for x in range(0,len(obj.getCoords())):
      if max < obj.getCoords()[x][axe]:
        max = rotatePoint(obj.getCoords()[x], vectorPull)[axe]
        posAtom = x

    return rotatePoint(obj.getCoords()[posAtom], vectorPull)

  def setupCaver(ligandCenter, filepdb):
    call('rm -r caver/input/*', shell=True)
    call('cp '+str(filepdb)+' caver/input', shell=True)
    coord_ligand = str(ligandCenter[0]) + ' ' + str(ligandCenter[1]) + ' ' + str(ligandCenter[2]) + '\n'
    replaceLine('starting_point_coordinates','starting_point_coordinates '+coord_ligand,'caver/config.txt')
    call('cd caver; sh caver.sh', shell=True)

    outputFile = []
    try:
      outputFile = check_output('cd caver/out/data/clusters; ls *.pdb', shell = True).splitlines()
    except subprocess.CalledProcessError as e:
      return None
    tunel = parsePDB('caver/out/data/clusters/'+outputFile[0])
    tunelVector = tunel.getCoords()[tunel.numAtoms()-1] - tunel.getCoords()[tunel.numAtoms()-2]
    return tunelVector


  #**********************************************************************#
  #************************** System Fuction ****************************#
  #**********************************************************************#

  def CallCommand(patch, command):
    call('cd '+patch+'; '+command, shell = True, executable='/bin/bash')

  def substring(mystr, mylist): 
    return [i for i, val in enumerate(mylist) if mystr in val]

  def replaceLine(search, replace, myfile):
    f = open(myfile, "r")
    contents = f.readlines()
    f.close()

    contents[substring(search,contents)[0]] = replace

    f = open(myfile, "w")
    contents = "".join(contents)
    f.write(contents)
    f.close()

  def insertLine(search, position, insert, myfile):
    f = open(myfile, "r")
    contents = f.readlines()
    f.close()

    if len(substring(search,contents)) > 0:
      contents.insert(substring(search,contents)[0]+position, insert)
      f = open(myfile, "w")
      contents = "".join(contents)
      f.write(contents)
      f.close()
    else:
      addLine(insert, myfile)  

  def searchLine(search, myfile):
    f = open(myfile, "r")
    contents = f.readlines()
    f.close()
    if len(substring(search,contents)) > 0:
      return contents[substring(search,contents)[0]]
    else:
      return ''

  def addLine(line, myfile):
    with open(myfile, "a") as mf:
      mf.write(line)

  def Log(tag, comment):
    addLine(tag+ ' ' +comment+'\n', 'log.txt')


  #**********************************************************************#
  #************************* Rotation Fuction ****************************#
  #**********************************************************************#
  def rotatePoint(point, pullvec):
    pullr = math.sqrt(float(pullvec[0])**2 + float(pullvec[1])**2 + float(pullvec[2])**2) 
    pullphi = angle(float(pullvec[0]), float(pullvec[1]))
    pullxy = math.sqrt(float(pullvec[0])**2 + float(pullvec[1])**2)
    pulltheta = angle(float(pullvec[2]), float(pullxy) )
    rotateZ(point, pullphi)
    rotateY(point, pulltheta)
    return point

  #Fuction
  def angle(x, y):
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

  def rotateZ(point, phi):
    point_r_xy = math.sqrt(point[0]**2 + point[1]**2) 
    point_phi = angle(point[0], point[1])

    point[0] = point_r_xy*math.cos(point_phi - phi)
    point[1] = point_r_xy*math.sin(point_phi - phi)
    return point

  def rotateY(point, theta):
    point_r_xz = math.sqrt(point[0]**2 + point[2]**2) 
    point_theta = angle(point[2], point[0])
     
    point[0] = point_r_xz*math.sin(point_theta - theta)
    point[2] = point_r_xz*math.cos(point_theta - theta)
    return point
  #***********************************************************************************#


  #**********************************************************************#
  #************************* Gromacs Fuction ****************************#
  #**********************************************************************#
  def SetupSystem():
    global GroLeft, GroRight
    runfolders = check_output('ls run/', shell = True).splitlines()
    for x in range(0,len(runfolders)):

      topolfile = 'run/'+runfolders[x]+'/topol.top'
      ligandCurrent = runfolders[x].split('_')[1] #A01
      try:
        ligandFolders = check_output('cd run/'+runfolders[x]+'; ls -d *.acpype', shell = True).splitlines()
      except subprocess.CalledProcessError as e:
        ligandFolders = []
      proteinfiles = check_output('cd run/'+runfolders[x]+'; ls protein*', shell = True).splitlines()

      #*****************************************************************************************************#
      #Add force field to protein
      #for y in range(0, len(proteinfiles)):
      #proteinname = proteinfiles[0].split(".")[0]
      CallCommand('run/'+runfolders[x],GroLeft+'pdb2gmx'+GroRight+' -ff '+ForceField+' -f protein.pdb -o protein.gro -water spce -missing -ignh')

      #if ligand is protein
      # if os.path.isfile('run/'+runfolders[x]+'/'+ligandCurrent+'.pdb') is True:
      #   CallCommand('run/'+runfolders[x],GroLeft+'pdb2gmx'+GroRight+' -ff '+ForceField+' -f '+ligandCurrent+'.pdb -o '+ligandCurrent+'.gro -water spce')

      #*****************************************************************************************************#
      #Merge *.gro file
      #Read file protein.gro
      proteingro = open('run/'+runfolders[x]+'/protein.gro', 'r')
      proteinData = proteingro.readlines()
      proteingro.close()
      
      for y in range(0, len(ligandFolders)):
        #Read file *.gro
        ligandName = ligandFolders[y].split('.')[0]
        gro = open('run/'+runfolders[x]+'/'+ligandFolders[y]+'/'+ligandName+'_GMX.gro', 'r')
        ligandData = gro.readlines()
        gro.close()

        #Change number of atoms and add atoms to bottom of protein.gro
        proteinData[1] = str(int(proteinData[1]) + int(ligandData[1])) + '\n'
        for line in ligandData[2:len(ligandData)-1]:
          proteinData.insert(len(proteinData)-1, line)

      #save to system.gro
      f = open('run/'+runfolders[x]+'/system.gro', "w")
      for item in proteinData:
        f.write(item)
      f.close()

      #*****************************************************************************************************#
      #Add atomtype and 
      atomtypes = []
      for y in range(0, len(ligandFolders)):
        #Read file *.itp
        ligandName = ligandFolders[y].split('.')[0]
        itp = open('run/'+runfolders[x]+'/'+ligandFolders[y]+'/'+ligandName+'_GMX.itp', 'r')
        itpline = itp.readlines()
        atomtypes.extend( itpline[substring('[ atomtypes ]',itpline)[0]: substring('[ moleculetype ]',itpline)[0]] )
     
        #save other part to ligand_topology.itp
        atomtopologys = []
        atomtopologys = itpline[substring('[ moleculetype ]',itpline)[0]:]
        itp.close()
   
        f = open('run/'+runfolders[x]+'/'+ligandName+'.itp', "w")
        for item in atomtopologys:
          f.write(item)
        f.close()

        #add ligand_topology.itp to topol.top
        if y == 0: insertLine('; Include water topology', -1, '\n; Include ligand topology \n', topolfile)
        insertLine('; Include water topology', -1, '#include "'+ligandName+'.itp" \n', topolfile)

        #add molecular to bottom of topol.top
        addLine(ligandName+'                 1\n', topolfile)

      #save atomtypes to ligand_atomtypes.itp
      f = open('run/'+runfolders[x]+'/ligand_atomtypes.itp', "w")
      for item in atomtypes:
        f.write(item)
      f.close()
   
      #add ligand_atomtypes.itp to topol.top
      insertLine('; Include forcefield parameters', 2, '#include "ligand_atomtypes.itp" \n', topolfile)

      #*****************************************************************************************************#
      #setup Box
      if os.path.isfile('run/'+runfolders[x]+'/'+ligandCurrent+'.acpype/'+ligandCurrent+'.pdb') is True:
        ligand = parsePDB('run/'+runfolders[x]+'/'+ligandCurrent+'.acpype/'+ligandCurrent+'.pdb')
      else:
        ligand = parsePDB('run/'+runfolders[x]+'/'+ligandCurrent+'.pdb')
      ligandCenter = calcCenter(ligand)

      #check if user want to use caver
      if run_caver == 'y':
        vectorPull = setupCaver(ligandCenter, 'run/'+runfolders[x]+'/protein.pdb')
        if vectorPull is None:
          vectorPull = ligandCenter - ReceptorCenter
      else:
        vectorPull = ligandCenter - ReceptorCenter
      Log('ligandCenter',str(ligandCenter))
      Log('ReceptorCenter',str(ReceptorCenter))

      call('cp source/rotate.py run/'+runfolders[x]+'/', shell = True)
      CallCommand('run/'+runfolders[x]+'/', 'python2.7 rotate.py -i system.gro -o rotate_system.gro -v '+str(vectorPull[0])+','+str(vectorPull[1])+','+str(vectorPull[2]))
      
      #*****************************************************************************************************#
      #set Boxsize
      #read distance 
      pullspeed = float(searchLine('pull_rate1', 'run/'+runfolders[x]+'/mdp/md_pull.mdp').split("=")[1].split(';')[0])
      pulltime = float(searchLine('nsteps', 'run/'+runfolders[x]+'/mdp/md_pull.mdp').split("=")[1].split(';')[0])*float(searchLine('dt', 'run/'+runfolders[x]+'/mdp/md_pull.mdp').split("=")[1].split(';')[0])
      distance = pullspeed*pulltime

      #Calc ratio of receptor/ligand
      if os.path.isfile('run/'+runfolders[x]+'/'+ligandCurrent+'.acpype/'+ligandCurrent+'.pdb') is True:
        ligand = parsePDB('run/'+runfolders[x]+'/'+ligandCurrent+'.acpype/'+ligandCurrent+'.pdb')
      else:
        ligand = parsePDB('run/'+runfolders[x]+'/'+ligandCurrent+'.pdb')
      ligandNumAtom = ligand.numAtoms()

      Log('number atom', str(ReceptorNumAtom) + ' ' + str(ligandNumAtom))
      ratio = float(float(ReceptorNumAtom)/float(ligandNumAtom))
      ligandMax = getMaxCoord(2, ligand, vectorPull)
      receptor = Avogadro.MoleculeFile.readMolecule('run/'+runfolders[x]+'/protein.gro')
      setbox('run/'+runfolders[x]+'/', 'rotate_system.gro', 'newbox.gro', receptor.numResidues, distance, ratio, ligandMax[2]/10)
      
      #Add solv
      CallCommand('run/'+runfolders[x],GroLeft+'genbox'+GroRight+' -cp newbox.gro -cs spc216.gro -p topol.top -o solv.gro')

  def runGromacs():
    runfolders = check_output('ls run/', shell = True).splitlines()
    for x in range(0,len(runfolders)):
      #Add ions to solv 
      #CallCommand('run/'+runfolders[x], 'cp solv.gro solv_ions.gro')
      CallCommand('run/'+runfolders[x], GroLeft+'grompp'+GroRight+' -maxwarn 10 -f mdp/ions.mdp -c solv.gro -p topol.top -o ions.tpr')
      CallCommand('run/'+runfolders[x], 'echo -e \"SOL\"|' +GroLeft+'genion'+GroRight+' -s ions.tpr -o solv_ions.gro -p topol.top -pname NA -nname CL -neutral -conc 0.1')

      #Create index file for first time => check double name
      CallCommand('run/'+runfolders[x], 'echo -e \"q\\n\" | '+ GroLeft+'make_ndx'+GroRight+' -f solv_ions.gro -o index.ndx') 
      ParseIndex('run/'+runfolders[x]+'/index.ndx')

      #*****************************************************************************************************#
      #Chang file mdp
      try:
        ligandFolders = check_output('cd run/'+runfolders[x]+'; ls -d *.acpype', shell = True).splitlines()
      except subprocess.CalledProcessError as e:
        ligandFolders = []

      replace_1 = 'energygrps      = Protein' 
      replace_2 = 'tc-grps         = Protein' 
      replace_3 = 'tau_t           = 0.1 0.1'
      replace_4 = 'ref_t           = 300 300'
      for y in range(0, len(ligandFolders)):
        #Lay resname cua ligand, ex: FAD, A01
        ligandName = ligandFolders[y].split('.')[0]
        ligand = Avogadro.MoleculeFile.readMolecule('run/'+runfolders[x]+'/'+ligandFolders[y]+'/'+ligandName+'.pdb')
        resname = ligand.residues[0].name
        replace_1 += ' '+resname
        replace_2 += '_'+resname

      #Check index have RNA or not 
      if IndexHaveRNA('run/'+runfolders[x]+'/index.ndx') == True:
        replace_1 += ' RNA'
        replace_2 += ' RNA'
        replace_3 += ' 0.1'
        replace_4 += ' 300'     
      elif IndexHaveDNA('run/'+runfolders[x]+'/index.ndx') == True:
        replace_1 += ' DNA'
        replace_2 += ' DNA'
        replace_3 += ' 0.1'
        replace_4 += ' 300'     

      replace_1 += '\n'
      replace_2 += ' Water_and_ions\n'
      replace_3 += '\n'
      replace_4 += '\n'
       
      replaceLine('energygrps', replace_1, 'run/'+runfolders[x]+'/mdp/minim.mdp')
      replaceLine('energygrps', replace_1, 'run/'+runfolders[x]+'/mdp/nvt.mdp')
      replaceLine('energygrps', replace_1, 'run/'+runfolders[x]+'/mdp/npt.mdp')
      replaceLine('energygrps', replace_1, 'run/'+runfolders[x]+'/mdp/md.mdp')
      replaceLine('energygrps', replace_1, 'run/'+runfolders[x]+'/mdp/md_pull.mdp')
      replaceLine('energygrps', replace_1, 'run/'+runfolders[x]+'/mdp/md_md.mdp')

      replaceLine('tc-grps', replace_2, 'run/'+runfolders[x]+'/mdp/nvt.mdp')
      replaceLine('tc-grps', replace_2, 'run/'+runfolders[x]+'/mdp/npt.mdp')
      replaceLine('tc-grps', replace_2, 'run/'+runfolders[x]+'/mdp/md.mdp')
      replaceLine('tc-grps', replace_2, 'run/'+runfolders[x]+'/mdp/md_pull.mdp') 
      replaceLine('tc-grps', replace_2, 'run/'+runfolders[x]+'/mdp/md_md.mdp') 

      replaceLine('tau_t', replace_3, 'run/'+runfolders[x]+'/mdp/nvt.mdp')
      replaceLine('tau_t', replace_3, 'run/'+runfolders[x]+'/mdp/npt.mdp')
      replaceLine('tau_t', replace_3, 'run/'+runfolders[x]+'/mdp/md.mdp')
      replaceLine('tau_t', replace_3, 'run/'+runfolders[x]+'/mdp/md_pull.mdp') 
      replaceLine('tau_t', replace_3, 'run/'+runfolders[x]+'/mdp/md_md.mdp') 

      replaceLine('ref_t', replace_4, 'run/'+runfolders[x]+'/mdp/nvt.mdp')
      replaceLine('ref_t', replace_4, 'run/'+runfolders[x]+'/mdp/npt.mdp')
      replaceLine('ref_t', replace_4, 'run/'+runfolders[x]+'/mdp/md.mdp')
      replaceLine('ref_t', replace_4, 'run/'+runfolders[x]+'/mdp/md_pull.mdp') 
      replaceLine('ref_t', replace_4, 'run/'+runfolders[x]+'/mdp/md_md.mdp') 

      #Find group, merge group, create group to index file
      #*********************************************************************************
      #create group receptor
      mergeGroup = ''
      nameOfGroup = ''
      nameOfLigand = ''
      if int(Method) == 1 or int(Method) == 2:
        system = Avogadro.MoleculeFile.readMolecule('run/'+runfolders[x]+'/newbox.gro')

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
        if os.path.isfile('run/'+runfolders[x]+'/ligand_residues.txt') is True: 
          f = open('run/'+runfolders[x]+'/ligand_residues.txt', "r")
          contents = f.readlines()
          f.close()
          print contents[0]
          print system.numResidues
          AtomStart = system.residues[int(contents[0].split('-')[0])].atoms[0]+1
          AtomEnd = system.residues[int(contents[0].split('-')[1])].atoms[len(system.residues[int(contents[0].split('-')[1])].atoms)-1]+1
          mergeGroup += 'a '+ str(AtomStart)+'-'+str(AtomEnd) +'\\n'
          nameOfLigand = 'a_'+ str(AtomStart)+'-'+str(AtomEnd)


      #Add group to index and Create posre
      topolfile = 'run/'+runfolders[x]+'/topol.top'
      indexfile = 'run/'+runfolders[x]+'/index.ndx'
      try:
        ligandFolders = check_output('cd run/'+runfolders[x]+'; ls -d *.acpype', shell = True).splitlines()
      except subprocess.CalledProcessError as e:
        ligandFolders = []
      ligandCurrent = runfolders[x].split('_')[1] #A01

      #ex: Protein_A01_FDA group
      mergeGroup += '\\"protein\\"'
      for y in range(0, len(ligandFolders)):
        ligandName = ligandFolders[y].split('.')[0]
        ligand = Avogadro.MoleculeFile.readMolecule('run/'+runfolders[x]+'/'+ligandFolders[y]+'/'+ligandName+'.pdb')
        resname = ligand.residues[0].name
        CallCommand('run/'+runfolders[x], 'echo -e \"'+resname+'\\n\" | '+GroLeft+'genrestr'+GroRight+' -f '+ligandName+'.acpype/'+ligandName+'_GMX.gro -o posre_'+ligandName+'.itp -fc 1000 1000 1000')
        insertLine(ligandName+'.itp', 1, '#ifdef POSRES \n#include "posre_'+ligandName+'.itp" \n#endif \n', topolfile)

        mergeGroup += ' | \\"' + resname +'\\"'
      print 'echo -e \"'+mergeGroup +'\\nq\\n\" | '+ GroLeft+'make_ndx'+GroRight+' -f solv.gro -o index.ndx'
      CallCommand('run/'+runfolders[x], 'echo -e \"'+mergeGroup +'\\nq\\n\" | '+ GroLeft+'make_ndx'+GroRight+' -f solv_ions.gro -n index.ndx') 
      #Change water to water_and_ions in index.ndx
      #replaceLine('[ Water ]', '[ Water_and_ions ]\n', indexfile)

      #change name of group
      if int(Method) == 1 or int(Method) == 2:
        replaceLine(nameOfGroup, '[ Receptor ]\n', indexfile)
      if os.path.isfile('run/'+runfolders[x]+'/ligand_residues.txt') is True: 
        replaceLine(nameOfLigand, '[ '+ligandCurrent+' ]\n', indexfile)
      #*********************************************************************************

      groCmd = ''
      #Run em
      if os.path.isfile('run/'+runfolders[x]+'/em.gro') is False: 
        groCmd += GroLeft+'grompp'+GroRight+' -maxwarn 20 -f mdp/minim.mdp -c solv_ions.gro -p topol.top -o em.tpr \n'
        groCmd += GroLeft+'mdrun'+GroRight+' '+GroOption+' -v -deffnm em \n'
      
      #Run nvt
      if os.path.isfile('run/'+runfolders[x]+'/nvt.gro') is False: 
        groCmd += GroLeft+'grompp'+GroRight+' -maxwarn 20 -f mdp/nvt.mdp -c em.gro -p topol.top -n index.ndx -o nvt.tpr \n'
        groCmd += GroLeft+'mdrun'+GroRight+ ' '+GroOption+ ' -deffnm nvt -v \n'

      #Run npt
      if os.path.isfile('run/'+runfolders[x]+'/npt.gro') is False: 
        groCmd += GroLeft+'grompp'+GroRight+' -maxwarn 20 -f mdp/npt.mdp -c nvt.gro -t nvt.cpt -p topol.top -n index.ndx -o npt.tpr \n'
        groCmd += GroLeft+'mdrun'+GroRight+ ' '+GroOption+ ' -deffnm npt -v \n'

      #Run md
      if os.path.isfile('run/'+runfolders[x]+'/md.gro') is False:
        groCmd += GroLeft+'grompp'+GroRight+ ' -maxwarn 20 -f mdp/md.mdp -c npt.gro -t npt.cpt -p topol.top -n index.ndx -o md.tpr \n'
        groCmd += GroLeft+'mdrun'+GroRight+ ' '+GroOption+ ' -deffnm md -v \n'
      
      if int(Method) == 1:
        if (int(repeat_times) == 1 or int(repeat_times) == 0 ):
          replaceLine('pull_group1', 'pull_group1     = '+ligandCurrent+'\n', 'run/'+runfolders[x]+'/mdp/md_pull.mdp')
          groCmd += GroLeft+'grompp'+GroRight+ ' -maxwarn 20 -f mdp/md_pull.mdp -c md.gro -t md.cpt -p topol.top -n index.ndx -o md_1.tpr \n'
          groCmd += GroLeft+'mdrun'+GroRight+ ' '+GroOption+ ' -px pullx.xvg -pf pullf.xvg -deffnm md_1 -v \n'
        else:
          # Repeat the steered for times
          CallCommand('run/'+runfolders[x], 'cp mdp/md_pull.mdp mdp/md_pull_repeat.mdp')
          replaceLine('continuation', 'continuation  = no   ; Restarting after NPT\n', 'run/'+runfolders[x]+'/mdp/md_pull_repeat.mdp')
          replaceLine('gen_vel','gen_vel   = yes\ngen_temp = 300\ngen_seed = -1\n', 'run/'+runfolders[x]+'/mdp/md_pull_repeat.mdp')
          replaceLine('pull_group1', 'pull_group1     = '+ligandCurrent+'\n', 'run/'+runfolders[x]+'/mdp/md_pull_repeat.mdp')
          
          for k in range(0,int(repeat_times)):
            groCmd += GroLeft+'grompp'+GroRight+ ' -maxwarn 20 -f mdp/md_pull_repeat.mdp -c md.gro -t md.cpt -p topol.top -n index.ndx -o md_1_'+str(k)+'.tpr \n'
            groCmd += GroLeft+'mdrun'+GroRight+ ' '+GroOption+ ' -px pullx_'+str(k)+'.xvg -pf pullf_'+str(k)+'.xvg -deffnm md_1_'+str(k)+' -v \n'
            groCmd += 'python2.7 parse_pull.py -x pullx_'+str(k)+'.xvg -f pullf_'+str(k)+'.xvg -o pullfx_'+str(k)+'.xvg\n'
        
      elif int(Method) == 2:
        if os.path.isfile('run/'+runfolders[x]+'/md_2.gro') is False:
          groCmd += GroLeft+'grompp'+GroRight+ ' -maxwarn 20 -f mdp/md_md.mdp -c md.gro -t md.cpt -p topol.top -n index.ndx -o md_2.tpr \n'
          groCmd += GroLeft+'mdrun'+GroRight+ ' '+GroOption+ ' -deffnm md_2 -v \n'

        groCmd += 'export OMP_NUM_THREADS=4\n'
        groCmd += 'echo -e \"Receptor\\n'+ligandCurrent+'\\n\" | g_mmpbsa -f md_2.trr -b 100 -dt 20 -s md_2.tpr -n index.ndx -pdie 2 -decomp \n'
        groCmd += 'echo -e \"Receptor\\n'+ligandCurrent+'\\n\" | g_mmpbsa -f md_2.trr -b 100 -dt 20 -s md_2.tpr -n index.ndx -i mdp/polar.mdp -nomme -pbsa -decomp \n'
        groCmd += 'echo -e \"Receptor\\n'+ligandCurrent+'\\n\" | g_mmpbsa -f md_2.trr -b 100 -dt 20 -s md_2.tpr -n index.ndx -i mdp/apolar_sasa.mdp -nomme -pbsa -decomp -apol sasa.xvg -apcon sasa_contrib.dat \n'
        groCmd += 'python2.7 MmPbSaStat.py -m energy_MM.xvg -p polar.xvg -a sasa.xvg \n'

      CallCommand('run/'+runfolders[x], groCmd)

  #**********************************************************************#
  #**************************** Main Fuction ****************************#                                                                                                                  
  #**********************************************************************#

  def main():
    ParsePDBInput()
    ChooseVersionGromacs()                                                                                    
    OptionalProgram()      
    if run_nohup == 'y':
      call('nohup python2.7 labpi.py &', shell=True)              
    else:
      PrepareLignad()
      PrepareLigandReceptor()
      PrepareCluster()
      SetupSystem()
      runGromacs()















