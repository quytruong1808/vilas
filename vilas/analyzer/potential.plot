set terminal pngcairo enhanced font "arial,20" fontscale 1.0 size 1024, 768
set output 'potential_scan.png'
set style fill solid 1.00 border 0

set xrange[227:341]
set xlabel 'residue ID'
set ylabel 'Potential (kJ/mol)'
#set title 'Potential between each residue and dsRNA'
set grid
set xtics rotate by -45

plot './mean.dat' u 2:7:8 t 'potential' w boxerror
