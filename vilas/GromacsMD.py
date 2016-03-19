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
		runfolders = check_output('ls '+main_path+'/run', shell = True).splitlines()
		call('rm -r '+main_path+'/analyse/*/', shell=True)

		for x in range(0,len(runfolders)):
			run_path = main_path+'/run/'+runfolders[x]
			
			if not os.path.isdir(main_path+'/run/'+runfolders[x]):
				continue

			if os.path.isfile(run_path+'/solv_ions.gro') is False: 
				continue

			#create folder for analyse
			call('mkdir '+self.dataController.getdata('path ')+'/analyse/'+runfolders[x].split('_')[1], shell=True)

			# Check point to show log
			self.dataController.setdata('status', runfolders[x])

			run_path = main_path+'/run/'+runfolders[x]
			ligandCurrent = runfolders[x].split('_')[1] #A01

			print self.GroLeft+'mdrun'+self.GroRight+' '+self.GroOption
			groCmd = ''

			#Run em
			call('mkdir '+run_path+'/em', shell=True)
			if os.path.isfile(run_path+'/em/em.gro') is False: 
				groCmd += self.GroLeft+'grompp'+self.GroRight+' -maxwarn 20 -f mdp/minim.mdp -c solv_ions.gro -p topol.top -o em/em.tpr \n'
				groCmd += self.GroLeft+'mdrun'+self.GroRight+' '+self.GroOption+' -v -deffnm em/em -cpt 5\n'
			
			#Run nvt
			call('mkdir '+run_path+'/nvt', shell=True)
			if os.path.isfile(run_path+'/nvt/nvt.gro') is False: 
				groCmd += self.GroLeft+'grompp'+self.GroRight+' -maxwarn 20 -f mdp/nvt.mdp -c em/em.gro -p topol.top -n index.ndx -o nvt/nvt.tpr \n'
				groCmd += self.GroLeft+'mdrun'+self.GroRight+ ' '+self.GroOption+ ' -deffnm nvt/nvt -v -cpt 5\n'

			#Run npt
			call('mkdir '+run_path+'/npt', shell=True)
			if os.path.isfile(run_path+'/npt/npt.gro') is False: 
				groCmd += self.GroLeft+'grompp'+self.GroRight+' -maxwarn 20 -f mdp/npt.mdp -c nvt/nvt.gro -t nvt/nvt.cpt -p topol.top -n index.ndx -o npt/npt.tpr \n'
				groCmd += self.GroLeft+'mdrun'+self.GroRight+ ' '+self.GroOption+ ' -deffnm npt/npt -v -cpt 5\n'

			#Run md
			call('mkdir '+run_path+'/md', shell=True)
			if os.path.isfile(run_path+'/md/md.gro') is False:
				groCmd += self.GroLeft+'grompp'+self.GroRight+ ' -maxwarn 20 -f mdp/md.mdp -c npt/npt.gro -t npt/npt.cpt -p topol.top -n index.ndx -o md/md.tpr \n'
				groCmd += self.GroLeft+'mdrun'+self.GroRight+ ' '+self.GroOption+ ' -deffnm md/md -v -cpt 5\n'
			groCmd += 'echo -e \"System\"|' + self.GroLeft+'trjconv'+self.GroRight+' -s md/md.tpr -f md/md.xtc -o md/md_noPBC.xtc -pbc mol -ur compact\n'
			if(self.GroVersion >= 5):
				groCmd += 'echo -e \"Backbone\\nBackbone\"|' + self.GroLeft+'rms'+self.GroRight+' -s md/md.tpr -f md/md_noPBC.xtc -o md/rmsd.xvg -tu ns\n'
			else:
				groCmd += 'echo -e \"Backbone\\nBackbone\"|' + 'g_rms'+self.GroRight+' -s md/md.tpr -f md/md_noPBC.xtc -o md/rmsd.xvg -tu ns\n'

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

			analyse_path = main_path+'/analyse/'+runfolders[x].split('_')[1]
			pull_vec = self.dataController.getdata('smd-vel ')
			pullx_path = ''
			pullf_path = ''
			call('mkdir '+run_path+'/smd', shell=True)
			for k in range(1,int(self.repeat_times)+1):
				if os.path.isfile(run_path+'/smd/md_st_'+str(k)+'.gro') is False:
					groCmd += self.GroLeft+'grompp'+self.GroRight+ ' -maxwarn 20 -f mdp/md_pull_repeat.mdp -c md/md.gro -t md/md.cpt -p topol.top -n index.ndx -o smd/md_st_'+str(k)+'.tpr \n'
					groCmd += self.GroLeft+'mdrun'+self.GroRight+ ' '+self.GroOption+ ' -px smd/pullx_'+str(k)+'.xvg -pf smd/pullf_'+str(k)+'.xvg -deffnm smd/md_st_'+str(k)+' -v -cpt 5\n'
					groCmd += 'python2.7 parse_pull.py -x smd/pullx_'+str(k)+'.xvg -f smd/pullf_'+str(k)+'.xvg -o smd/pullfx_'+str(k)+'.xvg\n'
			
				pullx_path += ' smd/pullx_'+str(k)+'.xvg'
				pullf_path += ' smd/pullf_'+str(k)+'.xvg'
			groCmd += 'python2.7 pullana.py -px '+pullx_path+' -pf '+pullf_path+' -plot '+analyse_path+'/pull_force_time.png '+analyse_path+'/pull_force_distance.png -log '+analyse_path+'/pull_data.csv -v '+pull_vec+'\n'
			groCmd += 'python2.7 mathplot.py -i md/rmsd.xvg -o '+analyse_path+'/rmsd.png\n'
			# analyze cmd
			cmd_analyze = 'python2.7 LabpiAnalyzer.py --gro '+run_path+'/md/md.gro --trj '+run_path+'/md/md.xtc --mdp '+run_path+'/mdp/md.mdp --tpr '+run_path+'/md/md.tpr --start 0 --end 5 --receptor Receptor --ligand '+ligandCurrent+ ' --run '+run_path+' --analyze '+main_path+'/analyse '
			if self.GroLeft.replace(' ','') != '':
				cmd_analyze += ' --gleft '+self.GroLeft 
			if self.GroRight.replace(' ','') != '':
				cmd_analyze += ' --gright '+self.GroRight
			groCmd += cmd_analyze +' -i False\n'
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
			# print groCmd


		call('rm -r '+run_path+'/#*', shell=True)
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


if __name__ == '__main__':
	gromacsMD = GromacsMD()
	gromacsMD.setupOptions()
	gromacsMD.mdrun()