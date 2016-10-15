#!/usr/bin/env python
#-*- coding: utf-8 -*-

# import numpy as np
# import matplotlib.pyplot as plt

# # example data
# x = np.arange(0.1, 4, 0.5)
# y = np.exp(-x)

# # example variable error bar values
# yerr = 0.1 + 0.2*np.sqrt(x)
# xerr = 0.1 + yerr

# # First illustrate basic pyplot interface, using defaults where possible.
# plt.figure()
# plt.errorbar(x, y, xerr=0.2, yerr=0.4)
# plt.title("Simplest errorbars, 0.2 in x, 0.4 in y")

# # Now switch to a more OO interface to exercise more features.
# fig, axs = plt.subplots(nrows=2, ncols=2, sharex=True)
# ax = axs[0, 0]
# ax.errorbar(x, y, yerr=yerr, fmt='o')
# ax.set_title('Vert. symmetric')

# # With 4 subplots, reduce the number of axis ticks to avoid crowding.
# ax.locator_params(nbins=4)

# ax = axs[0, 1]
# ax.errorbar(x, y, xerr=xerr, fmt='o')
# ax.set_title('Hor. symmetric')

# ax = axs[1, 0]
# ax.errorbar(x, y, yerr=[yerr, 2*yerr], xerr=[xerr, 2*xerr], fmt='--o')
# ax.set_title('H, V asymmetric')

# ax = axs[1, 1]
# ax.set_yscale('log')
# # Here we have to be careful to keep all y values positive:
# ylower = np.maximum(1e-2, y - yerr)
# yerr_lower = y - ylower

# ax.errorbar(x, y, yerr=[yerr_lower, 2*yerr], xerr=xerr,
            # fmt='o', ecolor='g', capthick=2)
# ax.set_title('Mixed sym., log y')

# fig.suptitle('Variable errorbars')

# plt.show()

################# This is part of testing regular expresion builtin module #####
# import re
# import glob
# import os
# from subprocess import call, Popen, PIPE

# def makeListOfResult():
    # # Get the root directory of the project
    # pwd = os.getcwd()
    # files = glob.glob('log/*')

    # # Pre-compile regex
    # regex = re.compile(r"  1      *")
    # ligands = []
    # for i in files:
        # # Open all log files and get 1st results
        # with open(i) as f:
            # for line in f:
                # if regex.search(line):
                    # idRank = regex.search(line)
                    # ligands.append([os.path.split(i)[-1].split('_')[0], float(line.split()[1])])
    # ligands.sort(key = lambda x: x[1])
    # f = open('result.txt', 'w')
    # for i in range(len(ligands)):
        # f.write(str(ligands[i][0]) + "  " + str(ligands[i][1]) + "\n")
    # f.close()
    # # print ligands

# def pickLigands(n):
    # while k <= n:
        # l


# open('result.txt', 'r')
# result = f.readlines()
# f.close()
# os.makedirs(os.path.dirname(os.path.realpath(__file__)) + '/ligand')

############ This part is for seaborn module testing ###########################
import os
import numpy as np
# import matplotlib.pyplot as plt
import pandas
import seaborn as sns; sns.set()

os.chdir('/media/quyngan/CoMoBioPhys/crc/10323441/run/run_A01')
def getXvgLegend(xvgfile, runfolder):
    os.chdir(runfolder)
    print "file name is: " + xvgfile
    f = open(xvgfile)
    contents = []
    for i, line in enumerate(f):
        if line.find('@') == 0:
            # print line
            contents.append(line)
        else:
            continue
    f.close()
    # print contents
    resids = []
    for i in range(len(contents)):
        if contents[i].find('legend "') != -1:
            # print contents[i]
            resids.append(contents[i].split('"')[1])
    # print resids
    return resids

def genTranposeFile(xvgfile, runfolder):
    os.chdir(runfolder)
    f = open(xvgfile, 'r')
    start, contents = 0, []
    for start, line in enumerate(f):
        if (line.find('@') != -1) or (line.find('#') != -1):
            continue
        elif len(line.strip()) == 0:
            continue
        else:
            contents.append(map(float, line.split()[1:]))
    f.close()
    # contents.remove('\n')
    # contents = [x for x in contents if x != '\n']
    # for i in range(len(contents)):
        # contents[i] = contents[i].split()
    # print contents
    tranpose = np.transpose(contents)
    # frames = tranpose[0]
    # print frames
    tranpose = np.delete(tranpose, 0, axis=0)
    # print "%r" % tranpose
    # print "%r" % len(tranpose[0])

    # get list of occupant residue
    list_of_occupant = getXvgLegend(xvgfile, runfolder)

    f = open('tranpose.csv', 'w')
    for i in range(0, tranpose.shape[0]):
        f.write(list_of_occupant[i])
        for j in range(0, len(tranpose[i])):
            f.write(',' + str(tranpose[i][j]))
            if j == (len(tranpose[i]) - 1):
                f.write('\n')
    f.close()
    return tranpose

def plotHbond(runfolder, xvgfile):
    """modify hbond.plot and call gnuplot to export image. Input needs:runfolder, xvgfile.
    You must put hbond.plot file in the runfolder. You can modify test_hbond.plot after
    this function run to change the output of gnuplot."""
    os.chdir(runfolder)
    f = open('hbond.plot', 'r')
    contents = f.readlines()
    f.close()

    # Gen tranpose.csv file
    tranpose = genTranposeFile(xvgfile, runfolder)
    # Change ytics, i.e. change name of residue to be displayed
    # blah = ''
    # list_of_occupant = getXvgLegend(xvgfile, runfolder)
    # for i in range(len(list_of_occupant)):
        # if i == len(list_of_occupant) - 1:
            # blah += '"' + str(list_of_occupant[i]) + '" ' + str(i)
        # else:
            # blah += '"' + str(list_of_occupant[i]) + '" ' + str(i) + ','
    # ytics = 'set ytics (' + blah + ') border in scale 0,0 mirror norotate  offset character 0, 0, 0 autojustify\n'
    # for i in range(len(contents)):
        # if contents[i].find('set ytics') == 0:
            # contents[i] = ytics
    # print 'modified hbond.plot file'

    # # Change yrange, i.e. change amount of residue to be displayed
    # yrange = 'set yrange[-0.5:' + str(len(list_of_occupant) - 1) + '.5] noreverse nowriteback\n'
    # for i in range(len(contents)):
        # if contents[i].find('set yrange') == 0:
            # contents[i] = yrange

    # # Change xrange, i.e. change amount of frame to be displayed
    # x_range = 'set xrange[-0.5:' + str(len(tranpose[0]) - 1) + '.5] noreverse nowriteback\n'
    # for i in range(len(contents)):
        # if contents[i].find('set xrange') == 0:
            # contents[i] = x_range

    # # Change output image file name
    # output_image = "set output 'hbond" + str(conjugateGroup) + ".png'"
    # for i in range(len(contents)):
        # if contents[i].find('set output') == 0:
            # contents[i] = output_image

    # Check contents and write to file
    # print contents
    f = open('test_hbond.plot', 'w')
    contents = "".join(contents)
    # print contents
    f.write(contents)
    f.close()

    # execute GNUplot
    # call('gnuplot test_hbond.plot', shell=True)
    # use pandas, seaborn to plot
    dataframe = pandas.read_csv(xvgfile)
    ax = sns.heatmap(dataframe)
    ax.figure.savefig('output_call.png')

f = open('occupancy.xvg', 'r')
contents = []
for start, line in enumerate(f):
    if (line.find('@') != -1) or (line.find('#') != -1):
        continue
    elif len(line.strip()) == 0:
        continue
    else:
        contents.append(map(float, line.split()[1:]))
        # contents.append(line)
f.close()
# contents = [x for x in contents if x != '\n']
print '%r' % contents
tranpose = np.transpose(contents)
print '%r' % tranpose
# tranpose = np.delete(tranpose, 0, axis=0)
print '%r' % tranpose
print type(tranpose)

# test seaborn
genTranposeFile('occupancy.xvg', '/media/quyngan/CoMoBioPhys/crc/10323441/run/run_A01')
plotHbond('/media/quyngan/CoMoBioPhys/crc/10323441/run/run_A01', 'occupancy.xvg')
# ax = sns.heatmap(tranpose)
# ax.plot()
# plt.show()
# ax.figure.savefig('output.png')
# plt.savefig('output_plt.png')
# ak = ax.get_figure()
# ak.savefig('output.png')
