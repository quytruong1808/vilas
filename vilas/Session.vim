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
badd +306 LabpiAnalyzer.py
badd +1 analyzer/plot_potential.r
badd +6 analyzer/potential.plot
badd +19 analyzer/test_hbond.plot
badd +1 test.py
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
badd +18 ~/crc/qsub/testAnalyzer.py
badd +1 ~/crc/Hoa/Hoa/Hoa/run/run_A01/script.sh
badd +42 ~/crc/Hoa/Hoa/Hoa/run/install.sh
badd +59 analyzer/readHBmap.py
argglobal
silent! argdel *
argadd LabpiAnalyzer.py
edit analyzer/readHBmap.py
set splitbelow splitright
wincmd _ | wincmd |
vsplit
1wincmd h
wincmd _ | wincmd |
split
1wincmd k
wincmd w
wincmd w
set nosplitbelow
set nosplitright
wincmd t
set winheight=1 winwidth=1
exe '1resize ' . ((&lines * 24 + 26) / 52)
exe 'vert 1resize ' . ((&columns * 42 + 57) / 114)
exe '2resize ' . ((&lines * 25 + 26) / 52)
exe 'vert 2resize ' . ((&columns * 42 + 57) / 114)
exe 'vert 3resize ' . ((&columns * 71 + 57) / 114)
argglobal
setlocal fdm=expr
setlocal fde=pymode#folding#expr(v:lnum)
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 59 - ((28 * winheight(0) + 12) / 24)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
59
normal! 0
wincmd w
argglobal
edit ~/crc/qsub/testAnalyzer.py
setlocal fdm=expr
setlocal fde=pymode#folding#expr(v:lnum)
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 34 - ((20 * winheight(0) + 12) / 25)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
34
normal! 03|
wincmd w
argglobal
edit LabpiAnalyzer.py
setlocal fdm=expr
setlocal fde=pymode#folding#expr(v:lnum)
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
17
normal! zo
76
normal! zo
76
normal! zc
127
normal! zo
127
normal! zc
143
normal! zo
143
normal! zc
167
normal! zo
167
normal! zc
245
normal! zo
275
normal! zo
330
normal! zo
331
normal! zo
330
normal! zc
359
normal! zo
359
normal! zc
444
normal! zo
468
normal! zo
468
normal! zo
let s:l = 304 - ((32 * winheight(0) + 25) / 50)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
304
normal! 06|
wincmd w
3wincmd w
exe '1resize ' . ((&lines * 24 + 26) / 52)
exe 'vert 1resize ' . ((&columns * 42 + 57) / 114)
exe '2resize ' . ((&lines * 25 + 26) / 52)
exe 'vert 2resize ' . ((&columns * 42 + 57) / 114)
exe 'vert 3resize ' . ((&columns * 71 + 57) / 114)
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
