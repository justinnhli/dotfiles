if executable('yapf')
	autocmd      BufEnter        *.py    setlocal formatprg=yapf
endif
