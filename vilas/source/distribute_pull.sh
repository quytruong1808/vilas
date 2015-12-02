#!/bin/bash

pullx_path=""
pullf_path=""
mkdir ../../analyse/run_g61

for i in $(seq 1 5); do 
  pullx_path="$pullx_path pullx_$i.xvg"
  pullf_path="$pullf_path pullf_$i.xvg"
done
python2.7 pullana.py -px $pullx_path -pf $pullf_path -plot ../../analyse/run_g61/pull_force_pull_force_time.jpg ../../analyse/run_g61/pull_force_distance.jpg -log ../../analyse/run_g61/pull_data_5.csv -v 0.004
  
