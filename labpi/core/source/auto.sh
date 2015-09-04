#!/bin/bash

cont=y
while [ $cont == "y" ]
do

  read -p "Select from 1-50: " other
  ligand=$(awk '{if($1==n) print $2}' n="$other" ../ResultL5/result)
  name="${ligand/_log/}"
  #name="${name/log\/}"

  ligand=../ResultL5/output/vina_$name.pdbqt
  file=$ligand resname=A$(printf "%02d\n" $other) index=01 Script/optimize_ligands.sh

  read -p "Do you want to continue (y/n): " cont
done
