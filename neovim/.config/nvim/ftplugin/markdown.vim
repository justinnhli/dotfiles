setlocal expandtab
setlocal wrap
if executable('cmark')
	setlocal makeprg=cmark\ '%:p'\ >\ '%:p:r.html'
endif
if executable('fmt')
	setlocal formatprg=fmt\ -w\ 2500
endif
