highlight link pythonBuiltin Special
setlocal expandtab
setlocal foldmethod=indent
setlocal tabstop=4
if executable('yapf')
	setlocal formatprg=yapf
endif
if executable('pylint')
	setlocal makeprg=pylint\ --reports=n\ --msg-template=\"{path}:{line}:{column}\ {msg_id}\ {symbol},\ {obj}\ {msg}\"\ %:p
	setlocal errorformat=%f:%l:%c\ %m
endif
