from subprocess import check_output
from subprocess import call

#Check_out to read, call to call :))
#Chon version gromacs tuong ung
print '\n*********************************'
print "Which version do you want to use? "
commands = check_output("compgen -ac | grep md", shell=True, executable='/bin/bash').splitlines()
for x in range(0, len(commands)):
  print "{0:2d} => {1:15s}".format(x,str(commands[x]))
index = raw_input("Enter version: ")
print "You choosed: " + str(commands[int(index)])

