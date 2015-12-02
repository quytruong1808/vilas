#!/usr/bin/python
import math
import sys, getopt

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


def main(argv):
  #Argument
  inputfile = ''
  outputfile = ''
  vector = ''
  try:
    opts, args = getopt.getopt(argv,"hi:o:v:",["ifile=","ofile="])
  except getopt.GetoptError:
    print 'test.py -i <inputfile> -o <outputfile>'
    sys.exit(2)

  for opt, arg in opts:
    if opt == '-h':
      print 'rotate.py -i <inputfile> -o <outputfile> -v <vector> x,y,z'
      sys.exit()
    elif opt in ("-i", "--ifile"):
      inputfile = arg
    elif opt in ("-o", "--ofile"):
      outputfile = arg
    elif opt in ("-v", "--vector"):
      vector = arg
  print 'Input file is ', inputfile
  print 'Output file is ', outputfile

  #Doc data tu file vao bien array
  gro = open(inputfile)
  olddata = []
  for i, line in enumerate(gro):
    olddata.append(line)
  gro.close()
  
  #pullvec = [-1.478, -6.833, 2.243]
  pullvec = vector.split(',')
  pullr = math.sqrt(float(pullvec[0])**2 + float(pullvec[1])**2 + float(pullvec[2])**2) 
  pullphi = angle(float(pullvec[0]), float(pullvec[1]))
  pullxy = math.sqrt(float(pullvec[0])**2 + float(pullvec[1])**2)
  pulltheta = angle(float(pullvec[2]), float(pullxy) )
  
  #Tinh toan va ghi ra file
  f = open(outputfile,'w')
  for x in range(0, len(olddata)):
    if x > 1 and x < len(olddata) - 1:
  
      res_number = olddata[x][0:5]
      res_name = olddata[x][5:10]
      atom_name = olddata[x][10:15]
      atom_number = olddata[x][15:20]
      pos_x = float(olddata[x][20:28])
      pos_y = float(olddata[x][28:36])
      pos_z = float(olddata[x][36:44])
  
      point = [pos_x, pos_y, pos_z]
      rotateZ(point, pullphi)
      rotateY(point, pulltheta)
 
      newline = "{0:5s}{1:5s}{2:5s}{3:5s}{4:8.3f}{5:8.3f}{6:8.3f}".format(res_number, res_name, atom_name, atom_number, point[0], point[1], point[2])
      f.write(newline + "\n")
    else:
      f.write(olddata[x])
  f.close()
  return


if __name__ == "__main__":
   main(sys.argv[1:])




