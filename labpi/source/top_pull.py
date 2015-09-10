import math
from subprocess import check_output
import os.path
import sys, getopt

def findName(i, myfile):
  f = open(myfile)
  data = []
  for j, line in enumerate(f):
    #print str(int(str(line)[0:3])) + ' ' + str(i+1)
    if int(str(line)[0:3]) == i:
      return str(line[69:].split('\n')[0])
  f.close()
  

MaxFile = []
MaxValue = []
MaxIndex = []

folders = check_output('ls -d run_*', shell = True).splitlines()
topfile= open('top_pull','w')

for i in range(0, len(folders[i])):
  print folders[i]
  Max_aver = 0.0
  for j in range(1,3):
    if os.path.isfile(folders[i]+'/pullfx_'+str(j)+'.xvg') == False:
      print 'check '+str(i)
      continue
    f = open(folders[i]+'/pullfx_'+str(j)+'.xvg', "r")
    contents = f.readlines()
    f.close()

    Max = 0.0
    for line in range(0, len(contents)):
      valueF = float(contents[line].split('\t')[2])
      if Max<valueF:
        Max = valueF
    Max_aver += Max
  Max_aver/=3
    
  #print folders[i]+' '+str(Max)
  MaxFile.append(folders[i])
  MaxValue.append(Max_aver)
  MaxIndex.append(i+1)

for j in range(0,len(MaxValue)):
  for k in range(j+1, len(MaxValue)):
    if MaxValue[j] < MaxValue[k]:
      tempValue = MaxValue[j]
      MaxValue[j] = MaxValue[k]
      MaxValue[k] = tempValue
      tempFile = MaxFile[j]
      MaxFile[j] = MaxFile[k]
      MaxFile[k] = tempFile
      tempIndex = MaxIndex[j]
      MaxIndex[j] = MaxIndex[k]
      MaxIndex[k] = tempIndex
  ligandName = MaxFile[j]
  newline = str(j+1) +'\t'+ str(MaxIndex[j]) + '\t' + str(MaxValue[j]) + '\t\t' + str(ligandName) +'\n'
  topfile.write(newline)
topfile.close()

