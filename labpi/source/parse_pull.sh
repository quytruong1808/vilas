#!/bin/bash

read -p "Number of file: " cont


for((i=1;i<=$cont;i++)) 
do
   cd 2UXN_FAD_A$(printf "%02d\n" $i)
   echo 2UXN_FAD_A$(printf "%02d\n" $i)
   rm pullfx.xvg
   start_1=$(awk '{if($1==0.0) print NR}' pullf.xvg)
   start_2=$(awk '{if($1==0.0) print NR}' pullx.xvg)
   end_1=$( wc -l < pullf.xvg )
   end_2=$( wc -l < pullx.xvg )

   x_first=$(awk 'NR==start_2 {print sqrt(($5)^2+($6)^2+($7)^2)}' start_2=$start_2 pullx.xvg)
   awk 'NR>=start_2 {print sqrt(($5)^2+($6)^2+($7)^2)}' start_2=$start_2 pullx.xvg |
   while read x         
   do
      tf=$(sed -n " $start_1 p" pullf.xvg)
      start_1=$(($start_1+1))
      echo -e $tf"\t"$(($x-$x_first)) >> pullfx.xvg
   done
   cd ..   
done

#awk 'NR==row {print $1,$2,dx}' row=$j dx=$x pullfx.xvg
#sed -i "$j " pullfx.xvg
#sed -i "$j s/$/\t $x /" pullfx.xvg
