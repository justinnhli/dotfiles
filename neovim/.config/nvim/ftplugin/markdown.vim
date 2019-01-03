setlocal expandtab
if executable('cmark')
	autocmd      BufEnter        *.md    setlocal wrap makeprg=cmark\ '%:p'\ >\ '%:p:r.html'
endif
