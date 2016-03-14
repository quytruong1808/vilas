import matplotlib.pyplot as plt
from os import listdir
import getopt
import glob
import os
import sys

def plot(inputfile, outputfile):
    figsize = (9,6)
    fontsize = 16
    figft = plt.figure(figsize=figsize)
    figft.suptitle('RMSD - Backbone',fontsize=fontsize)

    with open(inputfile) as f:
        data = f.read()

    x = []
    y = []
    fp = open(inputfile)
    for start_1, line in enumerate(fp):
        if line.find('@') != -1:
            continue
        elif line.find('#') != -1:
            continue
        else:    
            x.append(float(line.split(' ')[3]))
            y.append(float(line.split(' ')[7]))
    fp.close()

    axf = figft.add_subplot(1,1,1)
    axf.grid(True)
    axf.set_title("RMSD - Backbone")    
    axf.set_xlabel('Time (ns)')
    axf.set_ylabel('RMSD (nm)')
    axf.plot(x,y, c='r', label='rmsd')

    # Save file
    figft.tight_layout(pad=1.5)
    figft.savefig(outputfile, dpi=125)

def main(argv):
    #Argument
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print 'mathplot.py -i <inputfile> -o <outputfile>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
          print 'rotate.py -i <inputfile> -o <outputfile>'
          sys.exit()
        elif opt in ("-i", "--ifile"):
          inputfile = arg
        elif opt in ("-o", "--ofile"):
          outputfile = arg
    print 'Input file is ', inputfile
    print 'Output file is ', outputfile

    plot(inputfile, outputfile)



if __name__ == "__main__":
    main(sys.argv[1:])


