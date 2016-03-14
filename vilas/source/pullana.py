#!/usr/bin/env python
import os
import sys
import string
import math
from cycler import cycler
import matplotlib.pyplot as plt
import numpy as np

def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

class traj(object):
    vel = None
    plot = False
    def __init__(self,pf,px):
        self.v = traj.vel
        self.dt = 0.0
        self.pfname = pf # store filename
        self.pxname = px
        self.xyz = None #Check if the postions have both x y z components
        self.pullf = [] # kJ/mol/nm
        self.pullx = []
        ff = open(pf,'r')
        fx = open(px,'r')
        t1 = None
        t2 = None
        for line in ff:
            if line[0]!="#" and line[0]!="@":
                sp = line.split()
                t = float(sp[0])
                v = float(sp[1])
                if t1 == None:
            	    t1 = t
            	elif t2 == None:
            	    t2 = t
            	    self.dt = t2 - t1
            	self.pullf.append(v)
        ########
        for line in fx:
            if line[0]!="#" and line[0]!="@":
                sp = line.split()
                if self.xyz == None:
                	if len(sp) == 3:
                	    self.xyz = False
                	elif len(sp) == 7:
                	    self.xyz = True
                	else: sys.exit("Problems occur with %s!"%self.pxname)
                if self.xyz:
                    self.pullx.append((float(sp[4]),float(sp[5]),float(sp[6])))
                else:
                    self.pullx.append(float(sp[2]))
        ff.close()
        fx.close()
        if len(self.pullf) != len(self.pullx):
            sys.exit("Invalid input files: %s, %s"%(self.pfname,self.pxname))

    def integrate(self):
    	s = 0.0
    	for i in xrange(1,len(self.pullf)):
    		s = s + ((self.pullf[i-1]+self.pullf[i])*self.v*self.dt)/2.0
    	return s

    def max(self):
    	m = 0.0
    	for v in self.pullf:
    		if m<v: m = v
    	return m

    def getPosition(self,i): #Get z component of the postion
    	if self.xyz:
    		return self.pullx[i][3]
    	else: return self.pullx[i]

    def genfx(self,filename):
    	first_value = self.getPosition(0)
    	f = open(filename,'w')
    	f.write('@    xaxis  label "Position (nm)"\n')
    	f.write('@    yaxis  label "Force (kJ/mol/nm)"\n')
    	f.write('@TYPE xy\n')
    	for i in range(len(self.pullf)):
    	    f.write("%f\t%f\n"%(self.getPosition(i)-first_value,self.pullf[i]))
    	f.close()



    def plotf(self,outfile):
    	grace = which("grace")
    	if grace == None: sys.exit("Please install Grace to plot data!")
    	else:
    		os.system("%s %s -hdevice PNG -hardcopy -printfile %s"%(grace,self.pfname,outfile))

    def plotx(self,outfile):
    	grace = which("grace")
    	if grace == None: sys.exit("Please install Grace to plot data!")
    	else:
    		os.system("%s %s -hdevice PNG -hardcopy -printfile %s"%(grace,self.pxname,outfile))

def pfiles(list_pf,list_px):
	n = len(list_pf)
	for i in xrange(n):
		pf = list_pf[i]
		px = list_px[i]
		if os.path.isfile(pf) and os.path.isfile(px):
			yield (pf,px,i+1)
		else: sys.exit("%s or/and %s not found!"%(pf,px))

def read_files(pf,px,log,list_obj):
	num_tras = None
	force = []
	integral = [] #List of integrals
	tra_log = open(log,'w')
	tra_log.write("%s,%s,%s\n"%("Traj","Force(pN)","Intergral(kcal/mol)"))
	for ffile,xfile,i in pfiles(pf,px):
		#declare needed variables
		num_tras = i
		obj = traj(ffile,xfile)
		list_obj.append(obj)
		s = obj.integrate()/4.18 # Convert from kJ/mol -> kcal/mol
		f_max = obj.max()*1.66 # Convert from kJ/mol/nm -> pN
		force.append(f_max)
		integral.append(s)
		tra_log.write("%d,%.2f,%.2f\n"%(i,f_max,s))
	favg = sum(force)/num_tras
	savg = sum(integral)/num_tras
	#Calculate error for Fmax
	err = [abs(i - favg) for i in force]
	eavg = 0.0
	for e in err:
		eavg = eavg + e*e
	eavg = math.sqrt(eavg)
	eavg = eavg/num_tras
	#Calculate error for integral
	errs = [abs(i - savg) for i in integral]
	eavgs = 0.0
	for e in errs:
		eavgs = eavgs + e*e
	eavgs = math.sqrt(eavgs)
	eavgs = eavgs/num_tras
	tra_log.write("%s,%s,%s,%s\n"%("Average(pN)","Error(pN)","Integral(kcal/mol)","Error(kcal/mol)"))
	tra_log.write("%.2f,%.2f,%.2f,%.2f\n"%(favg,eavg,savg,eavgs))
"""
def plot_data(list_obj,list_plot):
	grace = which("grace")
	if grace == None: sys.exit("Please install Grace to plot data!")
	tmp = "/tmp"
	if not os.path.isdir(tmp): sys.exit("/tmp directory not found!")
	#Create position-force profiles
	list_ft = []
	list_fx = []
	for i,obj in enumerate(list_obj):
		pfx = os.path.join(tmp,"pullfx%d.xvg"%(i+1))
		obj.genfx(pfx)
		list_ft.append(obj.pfname)
		list_fx.append(pfx)
	#Plotting
	buf = ""
	for f in list_ft:
		buf = buf + "%s "%f
	os.system("%s %s -hdevice PNG -hardcopy -printfile %s"%(grace,buf,list_plot[0]))

	buf = ""
	for f in list_fx:
		buf = buf + "%s "%f
	os.system("%s %s -hdevice PNG -hardcopy -printfile %s"%(grace,buf,list_plot[1]))
"""

def plot_data(list_obj,list_plot):
    cm = plt.get_cmap('gist_rainbow')
    numColors = len(list_obj)
    fontsize = 16
    linewidth = 2
    figsize = (9,6)
    #####
    figft = plt.figure(figsize=figsize)
    figft.suptitle('Force-time Profile',fontsize=fontsize)
    axft = figft.add_subplot(1,1,1)
    axft.set_color_cycle([cm(1.*i/numColors) for i in range(numColors)])
    #axft.set_prop_cycle(cycler('color',[cm(1.*i/numColors) for i in range(numColors)]))
    axft.set_xlabel("Time(ps)", fontsize=fontsize)
    axft.set_ylabel("Force(pN)", fontsize=fontsize)
    axft.grid(True)
    #####
    figfx = plt.figure(figsize=figsize)
    figfx.suptitle('Force-position Profile',fontsize=fontsize)
    axfx = figfx.add_subplot(1,1,1)
    axfx.set_color_cycle([cm(1.*i/numColors) for i in range(numColors)])
    #axfx.set_prop_cycle(cycler('color',[cm(1.*i/numColors) for i in range(numColors)]))
    axfx.set_xlabel("Position(nm)", fontsize=fontsize)
    axfx.set_ylabel("Force(pN)", fontsize=fontsize)
    axfx.grid(True)
    #####
    for i,obj in enumerate(list_obj):
        time = np.arange(0.0,len(obj.pullf)*obj.dt,obj.dt)
        force = np.array(obj.pullf)*1.66
        pos = np.array(obj.pullx) - obj.getPosition(0)
        axft.plot(time,force,linewidth=linewidth)
        axfx.plot(pos,force,linewidth=linewidth)
    #####
    figft.tight_layout(pad=1.5)
    figft.savefig(list_plot[0], dpi=125)
    figfx.tight_layout(pad=1.5)
    figfx.savefig(list_plot[1], dpi=125)





list_pf = []
list_px = []
list_plot = []

if '-pf' in sys.argv:
		i=sys.argv.index('-pf')
		i=i+1
		while i < len(sys.argv):
			if sys.argv[i][0] == '-': break
			list_pf.append(sys.argv[i])
			i=i+1

if '-px' in sys.argv:
		i=sys.argv.index('-px')
		i=i+1
		while i < len(sys.argv):
			if sys.argv[i][0] == '-': break
			list_px.append(sys.argv[i])
			i=i+1

if '-plot' in sys.argv:
		i=sys.argv.index('-plot')
		i=i+1
		while i < len(sys.argv):
			if sys.argv[i][0] == '-': break
			list_plot.append(sys.argv[i])
			i=i+1

logfile = "pull.csv"
if '-log' in sys.argv:
	i=sys.argv.index('-log')
	i=i+1
	logfile = sys.argv[i]

if '-v' in sys.argv:
	i=sys.argv.index('-v')
	i=i+1
	traj.vel = float(sys.argv[i])
else: sys.exit("Please enter the velocity!")

if len(list_pf) != len(list_px):
	sys.exit("len(list_pf) != len(list_px)")

if len(list_plot) != 2 and len(list_plot) != 0:
	sys.exit("Two files must be given for plotting!")

list_obj = [] #contain all information from Force and Position profiles

read_files(list_pf, list_px, logfile, list_obj)

if len(list_plot) != 0: plot_data(list_obj,list_plot)
