let g:markdown_fenced_languages = ['css', 'html', 'java', 'javascript', 'python', 'sh', 'vim']
setlocal expandtab
setlocal wrap
if executable('cmark')
	setlocal makeprg=cmark\ --unsafe\ '%:p'\ >\ '%:p:r.html'
endif
if executable('fmt')
	setlocal formatprg=fmt\ -w\ 2500
endif
