highlight link javaScriptFunction Keyword
if executable('eslint')
	setlocal makeprg=eslint\ '%:p'
endif
