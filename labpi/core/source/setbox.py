from pylab import *
from prody import *
from os import listdir
import glob
import os
import sys
import Avogadro
import os.path
from subprocess import check_output
from subprocess import call
import math
import getopt

def main(argv):
  #Argument
  inputfile = ''
  outputfile = ''
  distance = ''
  ratio = ''
  try:
    opts, args = getopt.getopt(argv,"hi:o:d:r:",["ifile=","ofile=","distance=","ratio="])
  except getopt.GetoptError:
    print 'test.py -i <inputfile> -o <outputfile> -d <distance> -r <ratio>'
    sys.exit(2)

  for opt, arg in opts:
    if opt == '-h':
      print 'rotate.py -i <inputfile> -o <outputfile> -v <vector> x,y,z'
      sys.exit()
    elif opt in ("-i", "--ifile"):
      inputfile = arg
    elif opt in ("-o", "--ofile"):
      outputfile = arg
    elif opt in ("-d", "--distance "):
      distance = arg
    elif opt in ("-r", "--ratio "):
      ratio = arg
  print 'Input file is ', inputfile
  print 'Output file is ', outputfile
  print 'Distance is ', distance
  print 'Ratio is ', ratio

  #Read file
  protein = Avogadro.MoleculeFile.readMolecule(inputfile)

  #Find max and min falue file
  max = [-1000000,-1000000,-1000000]
  min = [1000000,1000000,1000000]
  for x in range(0, protein.numAtoms):
      atom = protein.atom(x)
      pos_x = float(atom.pos[0])
      pos_y = float(atom.pos[1])
      pos_z = float(atom.pos[2])
 
      if pox_x>max[0]:
        max[0] = pox_x
      if pox_x<min[0]:
        min[0] = pox_x

      if pox_y>max[1]:
        max[1] = pox_y
      if pox_y<min[1]:
        min[1] = pox_y

      if pox_z>max[2]:
        max[2] = pox_z
      if pox_z<min[2]:
        min[2] = pox_z

  Oxyz = [min[0]-1,min[1]-1,min[2]-2]
  d_x = max[0]-min[0]
  d_y = max[1]-min[1]
  d_z = max[2]-min[2]
  proteinCenter = protein.center
  proteinCenter = proteinCenter - Oxyz
  
  call('editconf_mpi -f'+inputfile+' -o'+outputfile +'-box '+str(d_x)+' '+str(d_y)+' '+str(d_z)+ ' -center '+str(proteinCenter[0])+' '+str(proteinCenter[1])+' '+str(proteinCenter[2]), shell=True, executable='/bin/bash') 

if __name__ == "__main__":
   main(sys.argv[1:])


