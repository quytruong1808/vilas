import os
from subprocess import call
from subprocess import check_output
from Utils import DataController
from Utils import CheckPoint


class GromacsMD(object):
	dataController = DataController() 
	# Get version of gromacs
	GroLeft = ''
	GroRight = ''
	GroVersion = ''
	GroOption = ''
	repeat_times = 0

	def mdrun(self):
		main_path = self.dataController.getdata('path ')
		runfolders = check_output('ls '+main_path+'/run/', shell = True).splitlines()

		for x in range(0,len(runfolders)):
			#create folder for analyse
			call('mkdir '+self.dataController.getdata('path ')+'/analyse/'+runfolders[x].split('_')[1], shell=True)

			# Check point to show log
			self.dataController.setdata('status', runfolders[x])

			run_path = main_path+'/run/'+runfolders[x]
			ligandCurrent = runfolders[x].split('_')[1] #A01

			print self.GroLeft+'mdrun'+self.GroRight+' '+self.GroOption
			groCmd = ''
			#Run em
			if os.path.isfile(run_path+'/em.gro') is False: 
				groCmd += self.GroLeft+'grompp'+self.GroRight+' -maxwarn 20 -f mdp/minim.mdp -c solv_ions.gro -p topol.top -o em.tpr \n'
				groCmd += self.GroLeft+'mdrun'+self.GroRight+' '+self.GroOption+' -v -deffnm em -cpt 5\n'
			
			#Run nvt
			if os.path.isfile(run_path+'/nvt.gro') is False: 
				groCmd += self.GroLeft+'grompp'+self.GroRight+' -maxwarn 20 -f mdp/nvt.mdp -c em.gro -p topol.top -n index.ndx -o nvt.tpr \n'
				groCmd += self.GroLeft+'mdrun'+self.GroRight+ ' '+self.GroOption+ ' -deffnm nvt -v -cpt 5\n'

			#Run npt
			if os.path.isfile(run_path+'/npt.gro') is False: 
				groCmd += self.GroLeft+'grompp'+self.GroRight+' -maxwarn 20 -f mdp/npt.mdp -c nvt.gro -t nvt.cpt -p topol.top -n index.ndx -o npt.tpr \n'
				groCmd += self.GroLeft+'mdrun'+self.GroRight+ ' '+self.GroOption+ ' -deffnm npt -v -cpt 5\n'

			#Run md
			if os.path.isfile(run_path+'/md.gro') is False:
				groCmd += self.GroLeft+'grompp'+self.GroRight+ ' -maxwarn 20 -f mdp/md.mdp -c npt.gro -t npt.cpt -p topol.top -n index.ndx -o md.tpr \n'
				groCmd += self.GroLeft+'mdrun'+self.GroRight+ ' '+self.GroOption+ ' -deffnm md -v -cpt 5\n'
			
			# if int(Method) == 1:
			# if (int(self.repeat_times) == 1 or int(self.repeat_times) == 0 ):
			# 	if(self.GroVersion >= 5):
			# 		self.replaceLine('pull-group2-name', 'pull-group2-name     = '+ligandCurrent+'\n', run_path+'/mdp/md_pull_5.mdp')
			# 		groCmd += self.GroLeft+'grompp'+self.GroRight+ ' -maxwarn 20 -f mdp/md_pull_5.mdp -c md.gro -t md.cpt -p topol.top -n index.ndx -o md_st.tpr \n'
			# 	else:
			# 		self.replaceLine('pull_group1', 'pull_group1     = '+ligandCurrent+'\n', run_path+'/mdp/md_pull.mdp')
			# 		groCmd += self.GroLeft+'grompp'+self.GroRight+ ' -maxwarn 20 -f mdp/md_pull.mdp -c md.gro -t md.cpt -p topol.top -n index.ndx -o md_st.tpr \n'
				
			# 	groCmd += self.GroLeft+'mdrun'+self.GroRight+ ' '+self.GroOption+ ' -px pullx.xvg -pf pullf.xvg -deffnm md_1 -v -cpt 5\n'
			# 	groCmd += 'python2.7 parse_pull.py -x pullx.xvg -f pullf.xvg -o pullfx.xvg\n'
						
			# else:
				# Repeat the steered for times
			if(self.GroVersion >= 5):
				self.CallCommand(run_path, 'cp mdp/md_pull_5.mdp mdp/md_pull_repeat.mdp')
				self.replaceLine('gen_vel','gen_vel   = yes\ngen_temp = 300\ngen_seed = -1\n', run_path+'/mdp/md_pull_repeat.mdp')
				self.replaceLine('pull-group2-name', 'pull-group2-name     = '+ligandCurrent+'\n', run_path+'/mdp/md_pull_repeat.mdp')
				if (self.dataController.getdata('smd-direction ') == 'True'):
					self.addLine('pull-coord1-vec = 0 0 1', run_path+'/mdp/md_pull_repeat.mdp')
			else:
				self.CallCommand(run_path, 'cp mdp/md_pull.mdp mdp/md_pull_repeat.mdp')
				self.replaceLine('gen_vel','gen_vel   = yes\ngen_temp = 300\ngen_seed = -1\n', run_path+'/mdp/md_pull_repeat.mdp')
				self.replaceLine('pull_group1', 'pull_group1     = '+ligandCurrent+'\n', run_path+'/mdp/md_pull_repeat.mdp')
				if (self.dataController.getdata('smd-direction ') == 'True'):
					self.addLine('pull_vec1 = 0 0 1', run_path+'/mdp/md_pull_repeat.mdp')

			self.replaceLine('continuation', 'continuation  = no   ; Restarting after NPT\n', run_path+'/mdp/md_pull_repeat.mdp')
			if (self.dataController.getdata('smd-direction ') == 'True'):
				self.replaceLine('pull-geometry', 'pull-geometry  = direction  \n', run_path+'/mdp/md_pull_repeat.mdp')

			analyse_path = main_path+'/analyse/'+runfolders[x].split('_')[1]
			pull_vec = self.dataController.getdata('smd-vel ')
			pullx_path = ''
			pullf_path = ''
			for k in range(0,int(self.repeat_times)):
				if os.path.isfile(run_path+'/md_st_'+str(k)+'.gro') is False:
					groCmd += self.GroLeft+'grompp'+self.GroRight+ ' -maxwarn 20 -f mdp/md_pull_repeat.mdp -c md.gro -t md.cpt -p topol.top -n index.ndx -o md_st_'+str(k)+'.tpr \n'
					groCmd += self.GroLeft+'mdrun'+self.GroRight+ ' '+self.GroOption+ ' -px pullx_'+str(k)+'.xvg -pf pullf_'+str(k)+'.xvg -deffnm md_st_'+str(k)+' -v -cpt 5\n'
					groCmd += 'python2.7 parse_pull.py -x pullx_'+str(k)+'.xvg -f pullf_'+str(k)+'.xvg -o pullfx_'+str(k)+'.xvg\n'
			
				pullx_path += ' pullx_'+str(k)+'.xvg'
				pullf_path += ' pullf_'+str(k)+'.xvg'
			groCmd += 'python2.7 pullana.py -px '+pullx_path+' -pf '+pullf_path+' -plot '+analyse_path+'/pull_force_time.xvg '+analyse_path+'/pull_force_distance.xvg -log '+analyse_path+'/pull_data.csv -v '+pull_vec+'\n'

			# elif int(Method) == 2:
			#   if os.path.isfile(run_path+'/md_2.gro') is False:
			#     groCmd += GroLeft+'grompp'+GroRight+ ' -maxwarn 20 -f mdp/md_md.mdp -c md.gro -t md.cpt -p topol.top -n index.ndx -o md_2.tpr \n'
			#     groCmd += GroLeft+'mdrun'+GroRight+ ' '+GroOption+ ' -deffnm md_2 -v \n'

			#   groCmd += 'export OMP_NUM_THREADS=4\n'
			#   groCmd += 'echo -e \"Receptor\\n'+ligandCurrent+'\\n\" | g_mmpbsa -f md_2.trr -b 100 -dt 20 -s md_2.tpr -n index.ndx -pdie 2 -decomp \n'
			#   groCmd += 'echo -e \"Receptor\\n'+ligandCurrent+'\\n\" | g_mmpbsa -f md_2.trr -b 100 -dt 20 -s md_2.tpr -n index.ndx -i mdp/polar.mdp -nomme -pbsa -decomp \n'
			#   groCmd += 'echo -e \"Receptor\\n'+ligandCurrent+'\\n\" | g_mmpbsa -f md_2.trr -b 100 -dt 20 -s md_2.tpr -n index.ndx -i mdp/apolar_sasa.mdp -nomme -pbsa -decomp -apol sasa.xvg -apcon sasa_contrib.dat \n'
			#   groCmd += 'python2.7 MmPbSaStat.py -m energy_MM.xvg -p polar.xvg -a sasa.xvg \n'

			self.CallCommand(run_path, groCmd)


		self.dataController.setdata('status', 'finished')
		self.CallCommand(main_path, 'rm -r caver')
		self.CallCommand(main_path+'/analyse', 'python2.7 top_pull.py')
		self.CallCommand(main_path+'/analyse', 'rm top_pull.py')


	def setupOptions(self):
		gromacs_version = self.dataController.getdata('gromacs_version ')
		version_array = gromacs_version.split(' VERSION ')[1].split('.')
		print version_array
		# If version >= 5
		if int(version_array[0]) == 5:
			# If version >= 5.1
			if int(version_array[1]) > 0:
				self.GroLeft = gromacs_version.split(' VERSION ')[0]
				self.GroRight = ''
			else: 
				# Check gmx
				mdrun_array = gromacs_version.split(' VERSION ')[0].split('mdrun')
				self.GroLeft = 'gmx '
				self.GroRight = mdrun_array[1]

			self.GroVersion = 5
		# If version = 4
		else:
			mdrun_array = gromacs_version.split(' VERSION ')[0].split('mdrun')
			self.GroLeft = mdrun_array[0]
			self.GroRight = mdrun_array[1]
			self.GroVersion = 4

		# Set number of core or gpu
		number_cores = self.dataController.getdata('maximum_cores ')
		if int(number_cores) > 0:
			self.GroOption = ' -ntomp '+number_cores
		else:
			self.GroOption = ''

		check_gpu = check_output(gromacs_version.split(' VERSION ')[0]+" -version", shell=True, executable='/bin/bash').splitlines()
		if( [s for s in check_gpu if "GPU support:" in s][0].split(":")[1].replace(' ','') == 'enabled'):
			self.GroOption += ' -gpu_id 0'

		#Repeat times 
		self.repeat_times = int(self.dataController.getdata('repeat_times '))

	def CallCommand(self, patch, command):
		call('cd '+patch+'; '+command, shell = True, executable='/bin/bash')

	def replaceLine(self, search, replace, myfile):
		f = open(myfile, "r")
		contents = f.readlines()
		f.close()

		contents[self.substring(search,contents)[0]] = replace

		f = open(myfile, "w")
		contents = "".join(contents)
		f.write(contents)
		f.close()

	def addLine(self, line, myfile):
		with open(myfile, "a") as mf:
			mf.write(line)

	def substring(self, mystr, mylist): 
		return [i for i, val in enumerate(mylist) if mystr in val]

if __name__ == '__main__':
	gromacsMD = GromacsMD()
	gromacsMD.setupOptions()
	gromacsMD.mdrun()