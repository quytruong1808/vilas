#!/bin/bash

mkdir temple

name=$(basename $file .pdbqt)
vina_split --input ligand/$file --ligand temple/$name"_"
babel temple/$name"_"$index".pdbqt" temple/"babel_"$name"_"$index".pdb"

#Xoa hydrogen cu va add all hydrogen
sed -i '/ H/d' temple/"babel_"$name"_"$index".pdb"
pymol temple/"babel_"$name"_"$index".pdb" -d 'h_add; save ligand.pdb; quit'
#reduce -build $x > ../ligand/"hydro_"$x
antechamber -fi pdb -fo pdb -i ligand.pdb -o $resname.pdb -rn $resname

rm temple/*
rmdir temple
rm ligand.pdb

#set parameter cho ligand
#antechamber -i $x -fi pdb -o ../amber/"amber_"$name.pdb -fo pdb -c bcc
python2.7 amber/acpype.py -i $resname.pdb



