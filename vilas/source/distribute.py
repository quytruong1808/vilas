import math
import sys, getopt

fp = open('pull_data.csv')
start = 0
array = []
for start,line in enumerate(fp):
  if line.find('Traj') != -1:
    continue
  elif line.find('Average') != -1:
    break
  else:    
    array.append(line)
fp.close()

force_max = 0.0
force_min = 0.0
integral_max = 0.0
integral_min = 0.0

for x in range(0, len(array)):
  x_array = array[x].split(",")
  #init
  if x == 0:
    force_max = float(x_array[1])
    force_min = float(x_array[1])

    integral_max = float(x_array[2])
    integral_min = float(x_array[2])
  #compare
  else:
    if force_max < float(x_array[1]):
      force_max = float(x_array[1])
    if force_min > float(x_array[1]):
      force_min = float(x_array[1])

    if integral_max < float(x_array[2]):
      integral_max = float(x_array[2])
    if integral_min > float(x_array[2]):
      integral_min = float(x_array[2])

#init array
force_distance = [(force_max-force_min)*i/10 for i in range(11)]
integral_distance = [(integral_max-integral_min)*i/10 for i in range(11)]

force_count = [0 for i in range(10)]
integral_count = [0 for i in range(10)]

#count 
for x in range(0, len(array)):
  x_array = array[x].split(",")
  for y in range(10):
    if float(x_array[1]) > force_min + force_distance[y] and float(x_array[1]) < force_min + force_distance[y+1]:
      force_count[y]+=1
    if float(x_array[2]) > integral_min + integral_distance[y] and float(x_array[2]) < integral_min + integral_distance[y+1]:
      integral_count[y]+=1
   
#write data
ff = open('distribute_force.xvg','w')
fi = open('distribute_integral.xvg','w')	
for x in range(10):
  newline = str(force_min + (force_distance[x] + force_distance[x+1])/2) + '\t' + str(force_count[x]) + '\n'
  ff.write(newline)
  newline = str(integral_min + (integral_distance[x] + integral_distance[x+1])/2) + '\t' + str(integral_count[x]) + '\n'
  fi.write(newline)
ff.close()
fi.close()

