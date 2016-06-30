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
badd +382 LabpiAnalyzer.py
badd +1 analyzer/plot_potential.r
badd +6 analyzer/potential.plot
badd +1 analyzer/test_hbond.plot
badd +3 test.py
badd +46 GromacsMD.py
badd +973 LabpiRun.py
badd +168 LabpiRunning.py
argglobal
silent! argdel *
argadd LabpiAnalyzer.py
edit test.py
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
exe '1resize ' . ((&lines * 18 + 19) / 38)
exe 'vert 1resize ' . ((&columns * 59 + 59) / 119)
exe '2resize ' . ((&lines * 17 + 19) / 38)
exe 'vert 2resize ' . ((&columns * 59 + 59) / 119)
exe 'vert 3resize ' . ((&columns * 59 + 59) / 119)
argglobal
setlocal fdm=expr
setlocal fde=pymode#folding#expr(v:lnum)
setlocal fmr={{{,}}}
setlocal fdi=#
setlocal fdl=0
setlocal fml=1
setlocal fdn=20
setlocal fen
let s:l = 49 - ((17 * winheight(0) + 9) / 18)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
49
normal! 0
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
let s:l = 382 - ((373 * winheight(0) + 8) / 17)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
382
normal! 0
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
let s:l = 382 - ((381 * winheight(0) + 18) / 36)
if s:l < 1 | let s:l = 1 | endif
exe s:l
normal! zt
382
normal! 0
wincmd w
exe '1resize ' . ((&lines * 18 + 19) / 38)
exe 'vert 1resize ' . ((&columns * 59 + 59) / 119)
exe '2resize ' . ((&lines * 17 + 19) / 38)
exe 'vert 2resize ' . ((&columns * 59 + 59) / 119)
exe 'vert 3resize ' . ((&columns * 59 + 59) / 119)
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
