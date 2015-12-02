import math
import sys, getopt

xFile = ''
fFile = ''
oFile = ''

def main(argv):
  global xFile, fFile, oFile
  try:
    opts, args = getopt.getopt(argv,"x:f:o:",["xfile=","ffile=","ofile="])
  except getopt.GetoptError:
    print 'parse_pull.py -x <coord file> -f <force file> -o <output file>'
    sys.exit(2)

  for opt, arg in opts:
    if opt == '-h':
      print 'parse_pull.py -x <coord file> -f <force file> -o <output file>'
      sys.exit()
    elif opt in ("-x", "--xfile"):
      xFile = arg
    elif opt in ("-f", "--ffile"):
      fFile = arg
    elif opt in ("-o", "--ofile"):
      oFile = arg


if __name__ == "__main__":
   main(sys.argv[1:])

#Doc data tu file vao bien array
fp = open(xFile)
start_1 = 0
array_1 = []
for start_1, line in enumerate(fp):
  if line.find('@') != -1:
    continue
  elif line.find('#') != -1:
    continue
  else:    
    array_1.append(line)
fp.close()

#Doc data tu file vao bien array
fp = open(fFile)
start_2 = 0
array_2 = []
for start_2, line in enumerate(fp):
  if line.find('@') != -1:
    continue
  elif line.find('#') != -1:
    continue
  else:    
    array_2.append(line)
fp.close()

#Tinh toan va ghi ra file
f = open(oFile,'w')
first_x = 0.0
for x in range(0, len(array_1)):
  x_array = array_1[x].split("\t")
  f_array = array_2[x].split("\t")
  #x_variable = math.sqrt(float(x_array[4])**2 + float(x_array[5])**2 + float(x_array[6])**2) 
  x_variable = float(x_array[len(x_array)-1])
  if x == 0:
    first_x = x_variable
  newline = x_array[0] + '\t' + str(x_variable - first_x) + '\t' + f_array[1]
  f.write(newline)
f.close()







