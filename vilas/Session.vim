let SessionLoad = 1
if &cp | set nocp | endif
let s:so_save = &so | let s:siso_save = &siso | set so=0 siso=0
let v:this_session=expand("<sfile>:p")
silent only
cd ~/Documents/vilas/vilas/vilas
if expand('%') == '' && !&modified && line('$') <= 1 && getline(1) == ''
  let s:wipebuf = bufnr('%')
endif
set shortmess=aoO
badd +435 LabpiAnalyzer.py
badd +1 analyzer/plot_potential.r
badd +6 analyzer/potential.plot
badd +9 analyzer/test_hbond.plot
badd +31 test.py
badd +6 GromacsMD.py
badd +257 LabpiRun.py
badd +95 LabpiRunning.py
badd +1 ~/crc/test.py
badd +169 LabpiConfiguration.py
badd +63 config/md_pull.mdp
badd +48 config/md_pull_5.mdp
badd +1 HOME
badd +470 LabpiConfiguration.kv
badd +1 ~/crc/qsub/10062694.e101725
badd +35 ~/crc/qsub/testAnalyzer.py
badd +1 ~/crc/Hoa/Hoa/Hoa/run/run_A01/script.sh
badd +42 ~/crc/Hoa/Hoa/Hoa/run/install.sh
badd +81 analyzer/readHBmap.py
badd +16 /media/quyngan/CoMoBioPhys/crc/testAnalyzer.py
badd +1 analyzer/hbond.plot
badd +1 source/pullana.py
argglobal
silent! argdel *
argadd LabpiAnalyzer.py
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winheight=1 winwidth=1
tabnext 1
if exists('s:wipebuf')
  silent exe 'bwipe ' . s:wipebuf
endif
unlet! s:wipebuf
set winheight=1 winwidth=20 shortmess=filnxtToO
let s:sx = expand("<sfile>:p:r")."x.vim"
if file_readable(s:sx)
  exe "source " . fnameescape(s:sx)
endif
let &so = s:so_save | let &siso = s:siso_save
let g:this_session = v:this_session
let g:this_obsession = v:this_session
let g:this_obsession_status = 2
doautoall SessionLoadPost
unlet SessionLoad
" vim: set ft=vim :
