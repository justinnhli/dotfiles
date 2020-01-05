highlight link pythonBuiltin Special
setlocal expandtab
setlocal foldmethod=indent
setlocal tabstop=4
if executable('yapf')
	setlocal formatprg=$PYTHON_VENV_HOME/mypylint/bin/python3\ -m\ yapf
endif
if executable('mypylint')
	setlocal makeprg=mypylint\ '%:p'
	setlocal errorformat=%f:%l:%c:\ %m
endif
