#!/bin/bash

protein="2UXN"
ligand_1="FAD"
cd ../$protein"_"$ligand_1"_"$ligand_2


cp gromacs_mdp/md.mdp gromacs_mdp/md_pull.mdp

  #porsres_protein "chain_A"
  #Khai bao trong md.mdp
  #line_include=$(($(cat -n topol.top | grep "title" | awk '{print $1;}')+2));
  #sed -i "$line_include i \\define          = -DPOSRES_P\ " gromacs_mdp/md.mdp

echo "; Pull code
pull            = umbrella
pull_geometry   = direction  ; simple distance increase 
pull_dim        = Y Y Y
pull_start      = yes       ; define initial COM distance > 0
pull_ngroups    = 1
pull_nstxout    = 1
pull_nstfout    = 1
pull_group0     = Oxidase 
pull_group1     = $ligand_2 
pull_vec1	= -1.478 -6.833 2.243
pull_rate1      = 0.004     ; 0.004 nm per ps = 4 nm per ns
pull_k1         = 600       ; kJ mol^-1 nm^-2" >> gromacs_mdp/md_pull.mdp

  #Define Oxidase domain in index.ndx file (Luu y so 18 - kiem tra lai moi lan chay khac)
  echo -e "a 5582-10447\nname 18 Oxidase\n1|13|14\nq\n" | make_ndx_mpi -f em.gro
  sed -i "s/ Water ].*/ Water_and_ions ]/" index.ndx

  #Chay md pull
  sed -i "s/^nsteps.*/nsteps          = 500000      ;1 ns/" gromacs_mdp/md_pull.mdp
  grompp_mpi -maxwarn 20 -f gromacs_mdp/md_pull.mdp -c md_1.gro -t md_1.cpt -p topol.top -n index.ndx -o md_2.tpr
  mdrun_mpi -ntomp 4 -gpu_id 0 -deffnm md_2 -px pullx.xvg -pf pullf.xvg -v

