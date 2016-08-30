set terminal pngcairo  transparent enhanced font "arial,10" fontscale 1.0 size 1024, 768
set output 'hbond.png'

unset key
set view map

set xtics border in scale 0,0 mirror norotate  offset character 0, 0, 0 autojustify
set ytics ("1C  -340ILE" 0,"1C  -340ILE" 1,"8G  -279GLN" 2,"8G  -279GLN" 3,"322ARG-7C  " 4,"322ARG-7C  " 5,"322ARG-6G  " 6,"322ARG-7C  " 7,"312ARG-5U  " 8,"312ARG-4A  " 9,"312ARG-4A  " 10,"312ARG-5U  " 11,"312ARG-4A  " 12,"312ARG-4A  " 13,"282LYS-8G  " 14,"279GLN-8G  " 15) border in scale 0,0 mirror norotate  offset character 0, 0, 0 autojustify
set ztics border in scale 0,0 nomirror norotate  offset character 0, 0, 0 autojustify
set nocbtics
set rtics axis in scale 0,0 nomirror norotate  offset character 0, 0, 0 autojustify
set title "Hydrogen-bonds percentage of each residue throughout MD simulation of Receptor - above threshold of 10.00%"

set yrange[-0.5:15.5] noreverse nowriteback
set xrange[-0.5:100.5] noreverse nowriteback
set cbrange[0:100] noreverse nowriteback
set xlabel "frames"
set ylabel "residue"
set cblabel "percentage"
set palette rgbformula -7,2,-7

#set boxwidth 0.9
set xtic scale 0
#set bmargin 10 
unset cbtics
#set pm3d map
#set dgrid3d

splot 'tranpose.csv' matrix with image
