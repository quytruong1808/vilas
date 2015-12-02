import os.path
from subprocess import check_output
from subprocess import call
import subprocess
from os import listdir
import glob
import os
import sys

def substring(mystr, mylist): 
  return [i for i, val in enumerate(mylist) if mystr in val]

def searchLine(search, myfile):
	f = open(myfile, "r")
	contents = f.readlines()
	f.close()
	if len(substring(search,contents)) > 0:
		return substring(search,contents)[0]
	else:
		return 0

def lineByindex(index, myfile):
	f = open(myfile, "r")
	contents = f.readlines()
	f.close()
	return contents[index]

def findName(i, myfile):
  f = open(myfile)
  data = []
  for j, line in enumerate(f):
    #print str(int(str(line)[0:3])) + ' ' + str(i+1)
    if int(str(line)[0:3]) == i:
      return str(line[69:].split('\n')[0])
  f.close()

def findDocking(i, myfile):
  f = open(myfile)
  data = []
  for j, line in enumerate(f):
    #print str(int(str(line)[0:3])) + ' ' + str(i+1)
    if int(str(line)[0:3]) == i:
      return float(line[23:30])
  f.close()

def findSteer(i, myfile):
  f = open(myfile)
  data = []
  for j, line in enumerate(f):
    #print str(int(str(line)[0:3])) + ' ' + str(i+1)
    if int(str(line).split('\t')[1]) == i:
      return float(str(line).split('\t')[2])
  f.close()



MaxValue = []
MaxIndex = []
topfile= open('top_mmpbsa.csv','w')
folders = check_output('ls -d 2UXN_*', shell = True).splitlines()

for i in range(0, len(folders)):
  if os.path.isfile(folders[i]+'/summary_energy.dat') == False:
    continue
  result = searchLine('Binding energy', folders[i]+'/summary_energy.dat')

  MaxValue.append(float(lineByindex(result, folders[i]+'/summary_energy.dat')[29:43]))
  MaxIndex.append(i+1)

for j in range(0,len(MaxValue)):
  for k in range(j+1, len(MaxValue)):
    if MaxValue[j] > MaxValue[k]:
      tempValue = MaxValue[j]
      MaxValue[j] = MaxValue[k]
      MaxValue[k] = tempValue
      tempIndex = MaxIndex[j]
      MaxIndex[j] = MaxIndex[k]
      MaxIndex[k] = tempIndex
  ligandName = findName(MaxIndex[j], 'result')
  ligandDocking = findDocking(MaxIndex[j], 'result')
  ligandSteer = findSteer(MaxIndex[j], 'top_pull')
  newline = str(j+1) +';' + str(ligandDocking) + ';' + str(ligandSteer) + ';' + str(MaxValue[j]) + ';' + str(ligandName) +'\n'
  topfile.write(newline)
topfile.close()