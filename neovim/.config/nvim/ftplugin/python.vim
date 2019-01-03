highlight link pythonBuiltin Special

let python_space_error_highlight = 1

setlocal expandtab
setlocal foldmethod=indent
setlocal tabstop=4
if executable('yapf')
	autocmd      BufEnter        *.py    setlocal formatprg=yapf
endif
