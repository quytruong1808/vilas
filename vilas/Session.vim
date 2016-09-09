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
badd +254 LabpiAnalyzer.py
badd +1 analyzer/plot_potential.r
badd +6 analyzer/potential.plot
badd +9 analyzer/test_hbond.plot
badd +92 test.py
badd +6 GromacsMD.py
badd +257 LabpiRun.py
badd +95 LabpiRunning.py
badd +37 ~/crc/test.py
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
badd +143 source/pullana.py
badd +58 ~/Documents/vilas/vilas/setup.py
argglobal
silent! argdel *
argadd LabpiAnalyzer.py
edit source/pullana.py
set splitbelow splitright
set nosplitbelow
set nosplitright
wincmd t
set winheight=1 winwidth=1
argglobal
setlocal fdm=expr
setlocal fde=pymode#folding#expr(v:lnum)
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
28
normal! zo
28
normal! zc
let s:l = 231 - ((230 * winheight(0) + 18) / 37)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
231
normal! 021|
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
