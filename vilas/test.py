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
import seaborn as sns; sns.set()

os.chdir('/media/quyngan/CoMoBioPhys/crc/10323441/run/run_A01')
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
ax = sns.heatmap(tranpose)
ax.figure.savefig('output.png')
