# -*- coding: utf-8 -*-

import subprocess
from sys import argv
import os


def make_ndx(resid):
    if os.path.isfile('index.ndx'):
        subprocess.Popen('make_ndx -f npt.gro -n index.ndx -o index.ndx',
                         stdin=subprocess.PIPE,
                         shell=True).communicate('r ' + resid + '\nq\n')
        return 0
    else:
        subprocess.Popen('make_ndx -f npt.gro -o index.ndx',
                         stdin=subprocess.PIPE,
                         shell=True).communicate('r ' + resid + '\nq\n')
        return 0
    print "Add a residue to index file."


def Resid(filename):
    o = open(filename, 'r')
    resid = o.read().split()
    o.close()
    return resid


def mdp_generator(resid):
    subprocess.call('cp' + ' ../md.mdp ' + resid + '.mdp', shell=True)
    with open(resid + '.mdp', 'a') as edit:
        edit.write('energy_grps =\tr_' + resid + '\tRNA\n')
    print "Created %s.mdp" % resid


def mkdir(resid):
    print "Created folder %s" % resid
    subprocess.Popen('mkdir ' + resid, stdin=subprocess.PIPE,
                     shell=True).communicate()
    os.chdir(working_path + '/' + resid)
    subprocess.call("pwd", shell=True)
    mdp_generator(resid)
    os.chdir(working_path)


def g_energy(resid):
    os.chdir(working_path + '/' + resid)
    subprocess.Popen(['g_energy', '-f ener.edr', '-s ' + resid + '.tpr',
                     '-o energy' + resid + '.xvg'],
                     stdin=subprocess.PIPE,
                     shell=True).communicate('4 5 6 8 9 10 11 12 50 51 52 53 0\n')
    os.chdir(working_path)


def g_hbond(resid):
    subprocess.call(['sh', 'hbond.sh', resid], shell=True)


def mdrun(resid):
    os.chdir(working_path + '/' + resid)
    subprocess.call('grompp' + ' -f ' + resid + '.mdp'
                    + ' -c ../npt.gro -p ../topol.top -n ../index.ndx'
                    + ' -o ' + resid + '.tpr -maxwarn 20', shell=True)
    subprocess.call('mdrun -s ' + resid + '.tpr -rerun ../md_noPBC.xtc',
                    shell=True)
    print "Deleting new md_noPBC.xtc file in the folder %s created" % resid
    if not os.getcwd() == working_path:
        subprocess.Popen('rm md_noPBC.xtc', stdin=subprocess.PIPE,
                         shell=True).communicate()
    os.chdir(working_path)
    print "Finish reruning the md simulation"


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Set argv ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
script, first_argv = argv
resid_list = Resid(first_argv)
working_path = os.path.dirname(os.path.abspath(__file__))
print type(working_path)
print working_path

for i in range(len(resid_list)):
    make_ndx(resid_list[i])
subprocess.call('rm \\#*', shell=True)

for i in range(70, len(resid_list)):
    mkdir(resid_list[i])
    mdrun(resid_list[i])

for i in range(len(resid_list)):
    g_energy(resid_list[i])

os.chdir(working_path)
subprocess.Popen(['g_hbond ', '-n index.ndx', '-s md.tpr', '-f md_noPBC.xtc',
                  '-num hbond.xvg', '-hbn hbond.ndx', '-hbm hbond.xpm',
                  '-b 0', '-e 5000'], stdin=subprocess.PIPE,
                 shell=True).communicate('1' + '\nRNA\n')
