highlight link pythonBuiltin Special
setlocal expandtab
setlocal foldmethod=indent
setlocal tabstop=4
if executable('yapf')
	setlocal formatprg=$PYTHON_VENV_HOME/mypylint/bin/python3\ -m\ yapf
endif
if executable('mypylint.py')
	execute 'setlocal makeprg=mypylint.py\ --pwd\ ' .. getcwd() .. '\ %'
	augroup justinnhli_python_lint_cwd
		autocmd!
		autocmd DirChanged <buffer> execute 'setlocal makeprg=mypylint.py\ --pwd\ ' .. expand('<afile>:p') .. '\ \%'
	augroup END
	setlocal errorformat=%f:%l:%c:\ %m
endif
