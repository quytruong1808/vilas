#!/bin/bash

read -p "Number of file: " cont
for((i=1;i<=$cont;i++)) 
do
   cd 2UXN_FAD_A$(printf "%02d\n" $i)
   echo 2UXN_FAD_A$(printf "%02d\n" $i)
   cp ../parse_pull.py .
   python parse_pull.py
   cd ..
done
