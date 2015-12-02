#!/bin/bash

#for (( i = 1; i <=1; i++ )); do
#  ligand_2=A$(printf "%02d" $i) ./steermd.sh
#done

for (( i = 1; i <=30; i++ )); do
  ligand_2=A$(printf "%02d" $i) ./gromacs.sh
done
