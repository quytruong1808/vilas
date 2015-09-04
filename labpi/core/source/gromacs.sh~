#!/bin/bash

protein="2UXN"

ligand_1="FAD"
ligand_1_file="vina_FAD.pdbqt"

#ligand_2="A01"
#ligand_2_file="vina_other_1000.pdbqt"

mkdir ../$protein"_"$ligand_1"_"$ligand_2
rm ../$protein"_"$ligand_1"_"$ligand_2/*
for x in *;do cp -R $x ../$protein"_"$ligand_1"_"$ligand_2; done
cd ../$protein"_"$ligand_1"_"$ligand_2

cp -r ../Ligand/$ligand_1.acpype .
cp -r ../Ligand/$ligand_2.acpype .

###########################################################
#function
function add_ligand_to_gro () {
  awk '{l[NR] = $0} END {for (i=3; i<=NR-1; i++) print l[i]}' $1.acpype/$1"_GMX.gro" > ligand_temple.txt
  count=$(($(wc -l < $protein.gro)-1)) 
  sed -i "$count r ligand_temple.txt" $protein.gro

  #Them so nguyen tu
  number=$(sed -n '2p' 2UXN.gro) 
  newnumber=$(( $number+ $(wc -l < ligand_temple.txt) ))
  sed -i "s/$number/$newnumber/" $protein.gro
  rm ligand_temple.txt
}

function atomtypes_itp () {
  cp $1.acpype/$1_GMX.itp $1.acpype/$1_GMX_backup.itp
  start=$(cat -n $1.acpype/$1_GMX_backup.itp | grep "atomtypes" | awk '{print $1;}')
  end=$(($(cat -n $1.acpype/$1_GMX_backup.itp | grep "moleculetype" | awk '{print $1;}')-1))
  sed -n " $start , $end p" $1.acpype/$1_GMX_backup.itp >> ligand_atomtypes.itp
  sed -i " $start , $end d" $1.acpype/$1_GMX_backup.itp
}

function atoms_itp () {
  line_include=$(($2-1))
  sed -i "$line_include i \; Include ligand topology\ " topol.top
  line_include=$((line_include+1))

  ligand_itp="#include \""$1".acpype/"$1"_GMX_backup.itp\""
  sed -i "$line_include i \\$ligand_itp\ " topol.top
  echo "$1                 1" >> topol.top
}

function posres_itp () {
  line_include=$(($(cat -n topol.top | grep $1".acpype" | awk '{print $1;}')+1));
  ligand_itp="; Ligand position restraints \n#ifdef POSRES"
  sed -i "$line_include i \\$ligand_itp\ " topol.top
  line_include=$((line_include+2))

  echo -e "2\n" | genrestr_mpi -f $1.acpype/$1"_GMX.gro" -o posre_$1.itp -fc 1000 1000 1000
  ligand_itp="#include \"posre_$1.itp\"\n#endif\n"
  sed -i "$line_include i \\$ligand_itp\ " topol.top
}

function porsres_protein(){
  #Restrain protein
  line_include=$(($(cat -n topol.top | grep "topol_Protein_"$1".itp" | awk '{print $1;}')+1));
  ligand_itp="#ifdef POSRES_P"
  sed -i "$line_include i \\$ligand_itp\ " topol.top
  line_include=$((line_include+1))
  
  ligand_itp="#include \"posre_Protein_$1.itp\"\n#endif\n"
  sed -i "$line_include i \\$ligand_itp\ " topol.top
}

function steer_md(){
  cp gromacs_mdp/md.mdp gromacs_mdp/md_pull.mdp

  #porsres_protein "chain_A"
  #Khai bao trong md.mdp
  #line_include=$(($(cat -n topol.top | grep "title" | awk '{print $1;}')+2));
  #sed -i "$line_include i \\define          = -DPOSRES_P\ " gromacs_mdp/md.mdp

echo "; Pull code
pull            = umbrella
pull_geometry   = distance  ; simple distance increase 
pull_dim        = N N Y
pull_start      = yes       ; define initial COM distance > 0
pull_ngroups    = 1
pull_nstxout    = 10
pull_nstfout    = 10
pull_group0     = Oxidase 
pull_group1     = $ligand_2 
pull_rate1      = 0.004     ; 0.004 nm per ps = 4 nm per ns
pull_k1         = 600       ; kJ mol^-1 nm^-2" >> gromacs_mdp/md_pull.mdp

  #Define Oxidase domain in index.ndx file (Luu y so 18 - kiem tra lai moi lan chay khac)
  echo -e "a 5582-10447\nname 18 Oxidase\n1|13|14\nq\n" | make_ndx_mpi -f em.gro
  sed -i "s/ Water ].*/ Water_and_ions ]/" index.ndx

  #Chay md pull
  sed -i "s/^nsteps.*/nsteps          = 500000      ;1 ns/" gromacs_mdp/md_pull.mdp
  grompp_mpi -maxwarn 20 -f gromacs_mdp/md_pull.mdp -c md_1.gro -t md_1.cpt -p topol.top -n index.ndx -o md_2.tpr
  mdrun_mpi -ntomp 4 -gpu_id 0 -deffnm md_2 -px pullx.xvg -pf pullf.xvg -v
}

function normal_md(){
  sed -i "s/^nsteps.*/nsteps          = 500000      ;1 ns/" gromacs_mdp/md.mdp
  grompp_mpi -maxwarn 20 -f gromacs_mdp/md.mdp -c md_1.gro -t md_1.cpt -p topol.top -n index.ndx -o md_2.tpr
  mdrun_mpi -ntomp 4 -gpu_id 0 -deffnm md_2 -v
}

function mm_pbsa(){
  export OMP_NUM_THREADS=4
  #Tinh deltaG giua protein(1) vs ligand_2(14)  (neu chi 1 ligand: 1-13)
  echo -e "1\n14\n" | g_mmpbsa -f md_1.trr -b 100 -dt 10 -s md_1.tpr -n index.ndx -pdie 2 -decomp
  echo -e "1\n14\n" | g_mmpbsa -f md_1.trr -b 100 -dt 10 -s md_1.tpr -n index.ndx -i polar.mdp -nomme -pbsa -decomp
  echo -e "1\n14\n" | g_mmpbsa -f md_1.trr -b 100 -dt 10 -s md_1.tpr -n index.ndx -i apolar_sasa.mdp -nomme -pbsa -decomp -apol sasa.xvg -apcon sasa_contrib.dat
  python2.7 MmPbSaStat.py -m energy_MM.xvg -p polar.xvg -a sasa.xvg 
}


###########################################################
#Chuan bi file protein.pdb 
sed -i '/HETATM/d' $protein.pdb

###########################################################
##Parameterize ligand from SDF or PDB
#antechamber -i ligand/$ligand_1.sdf -fi sdf -o ligand/$ligand_1.pdb -fo pdb -rn $ligand_1
#sed -i '/ H/d' ligand/$ligand_1.pdb
#pymol ligand/$ligand_1.pdb -d 'h_add; save ligand_1.pdb; quit'
#mv ligand_1.pdb $ligand_1.pdb
#python2.7 amber/acpype.py -i $ligand_1.pdb

##Parameterize ligand from PDBQT
#file=$ligand_1_file resname=$ligand_1 index=1 .amber/optimize_ligand.sh
#file=$ligand_2_file resname=$ligand_2 index=1 .amber/optimize_ligand.sh

############################################################
#add force field
echo -e "\n5" | pdb2gmx_mpi -f $protein.pdb -o "$protein".gro -water spce

############################################################
#Chen ligand vao protein.gro

add_ligand_to_gro $ligand_1
add_ligand_to_gro $ligand_2

#############################################################
#Chen ligand vao topol.top
#Luu y: tach rieng atomtypes ra file rieng va de len tren cung (duoi ff)
line_include=$(($(cat -n topol.top | grep "Include forcefield parameters" | awk '{print $1;}')+2));
ligand_itp="#include \"ligand_atomtypes.itp\""
sed -i "$line_include i \\$ligand_itp\ " topol.top

atomtypes_itp $ligand_1
atomtypes_itp $ligand_2

line_include=$(($(cat -n topol.top | grep "Include water topology" | awk '{print $1;}')-1));
sed -i "$line_include i \ \n \ " topol.top
line_include=$((line_include+2))

atoms_itp $ligand_1 $line_include
atoms_itp $ligand_2 $line_include

###############################################################
#Repare *.mdp file
sed -i "s/^energygrps.*/energygrps      = Protein $ligand_1 $ligand_2/" gromacs_mdp/minim.mdp
sed -i "s/^energygrps.*/energygrps      = Protein $ligand_1 $ligand_2/" gromacs_mdp/nvt.mdp
sed -i "s/^tc-grps.*/tc-grps         = Protein_"$ligand_1"_"$ligand_2" Water_and_ions/" gromacs_mdp/nvt.mdp
sed -i "s/^energygrps.*/energygrps      = Protein $ligand_1 $ligand_2/" gromacs_mdp/npt.mdp
sed -i "s/^tc-grps.*/tc-grps         = Protein_"$ligand_1"_"$ligand_2" Water_and_ions/" gromacs_mdp/npt.mdp
sed -i "s/^energygrps.*/energygrps      = Protein $ligand_1 $ligand_2/" gromacs_mdp/md.mdp
sed -i "s/^tc-grps.*/tc-grps         = Protein_"$ligand_1"_"$ligand_2" Water_and_ions/" gromacs_mdp/md.mdp

###############################################################
#Xoay file gro
python2.7 rotate.py -i "$protein".gro -o new_"$protein".gro

#Tao box + add ion 
#editconf_mpi -f new_$protein.gro -o newbox.gro -center 6 7.5 7 -box 12 14 18 -rotate -80 15 -10
editconf_mpi -f new_$protein.gro -o newbox.gro -center 6 6 7 -box 12 12 18
genbox_mpi -cp newbox.gro -cs spc216.gro -p topol.top -o solv.gro

cp solv.gro solv_ions.gro

#Luu y 2 ligand thi SOL la 16 ko phai 15
grompp_mpi -maxwarn 10 -f gromacs_mdp/ions.mdp -c solv.gro -p topol.top -o ions.tpr
echo -e "16\n" | genion_mpi -s ions.tpr -o solv_ions.gro -p topol.top -pname NA -nname CL -neutral 

grompp_mpi -maxwarn 20 -f gromacs_mdp/minim.mdp -c solv_ions.gro -p topol.top -o em.tpr
mdrun_mpi -ntomp 4 -gpu_id 0 -v -deffnm em

###############################################################
#Merge ligand vs protein
posres_itp $ligand_1 
posres_itp $ligand_2 

#Luu y 2 ligand thi 1|13|14 (check lai)
echo -e "1|13|14\nq\n" | make_ndx_mpi -f em.gro -o index.ndx

#Neu ko add ion thi can thay doi name water trong index.ndx
sed -i "s/ Water ].*/ Water_and_ions ]/" index.ndx

###################################################################
#Chay can bang
grompp_mpi -maxwarn 20 -f gromacs_mdp/nvt.mdp -c em.gro -p topol.top -n index.ndx -o nvt.tpr
mdrun_mpi -ntomp 4 -gpu_id 0 -deffnm nvt -v

grompp_mpi -maxwarn 20 -f gromacs_mdp/npt.mdp -c nvt.gro -t nvt.cpt -p topol.top -n index.ndx -o npt.tpr
mdrun_mpi -ntomp 4 -gpu_id 0 -deffnm npt -v

###################################################################
#Chay md vs steer or mmpbsa
sed -i "s/^nsteps.*/nsteps          = 250000      ;500ps/" gromacs_mdp/md.mdp
grompp_mpi -maxwarn 20 -f gromacs_mdp/md.mdp -c npt.gro -t npt.cpt -p topol.top -n index.ndx -o md_1.tpr
mdrun_mpi -ntomp 4 -gpu_id 0 -deffnm md_1 -v

steer_md
#normal_md

###################################################################
#Chay mmpbsa
#mm_pbsa







