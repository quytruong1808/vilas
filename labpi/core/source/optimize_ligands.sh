#!/bin/bash

mkdir temple

name=$(basename $file .pdbqt)
vina_split --input $file --ligand temple/$resname"_"
babel temple/$resname"_"$index".pdbqt" temple/$resname.pdb
#antechamber -fi pdb -fo pdb -i temple/name"_"$index".pdb" -o temple/$resname.pdb -rn $resname

#Xoa hydrogen cu va add all hydrogen
#sed -i '/ H/d' temple/$resname.pdb
#pymol temple/"babel_"$name"_"$index".pdb" -d 'h_add; save ligand.pdb; quit'
#reduce -build $x > ../ligand/"hydro_"$x

avogadro temple/$resname.pdb
antechamber -fi pdb -fo pdb -i temple/$resname.pdb -o $resname.pdb -rn $resname
#set parameter cho ligand
#antechamber -i $x -fi pdb -o ../amber/"amber_"$name.pdb -fo pdb -c bcc

rm $resname.acpype/*
rmdir $resname.acpype

read -p "Net charge: " n
python2.7 Script/acpype.py -i $resname.pdb -c bcc -n $n

rm temple/*
rmdir temple


