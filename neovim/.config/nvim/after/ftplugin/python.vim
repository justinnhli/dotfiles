setlocal expandtab
setlocal foldmethod=indent
setlocal tabstop=4
if executable('yapf')
	autocmd      BufEnter        *.py    setlocal formatprg=yapf
endif
