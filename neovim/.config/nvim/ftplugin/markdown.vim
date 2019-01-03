setlocal expandtab
setlocal wrap
if executable('cmark')
	setlocal makeprg=cmark\ '%:p'\ >\ '%:p:r.html'
endif
