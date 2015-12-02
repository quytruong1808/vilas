import math
from subprocess import check_output
import os.path
import sys, getopt

MaxName = []
MaxForce = []
MaxIntergral = []

folders = check_output('ls -d */', shell = True).splitlines()
topfile= open('rank_pull.csv','w')

for i in range(0, len(folders)):
  print folders[i]
  if os.path.isfile(folders[i]+'/pull_data.csv') == False:
    print 'check '+str(i)
    continue

  f = open(folders[i]+'/pull_data.csv', "r")
  contents = f.readlines()
  f.close()

  MaxName.append(folders[i].split('/')[0])
  MaxForce.append(contents[len(contents)-1].split(',')[0])
  MaxIntergral.append(contents[len(contents)-1].split(',')[2])
    
newline = 'Id, Name, Intergral, Force\n'
topfile.write(newline)
for j in range(0,len(MaxIntergral)):
  for k in range(j+1, len(MaxIntergral)):
    if MaxIntergral[j] < MaxIntergral[k]:
      tempValue = MaxIntergral[j]
      MaxIntergral[j] = MaxIntergral[k]
      MaxIntergral[k] = tempValue
      tempValue = MaxForce[j]
      MaxForce[j] = MaxForce[k]
      MaxForce[k] = tempValue
      tempValue = MaxName[j]
      MaxName[j] = MaxName[k]
      MaxName[k] = tempValue
  newline = str(j+1) +','+ str(MaxName[j]) +','+ str(MaxIntergral[j]) + ',' + str(MaxForce[j]) +'\n'
  topfile.write(newline)
topfile.close()

