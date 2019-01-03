if executable('dot')
	autocmd      BufEnter        *.dot   setlocal makeprg=dot\ -Tpng\ %:p\ >\ %:p:r.png
endif
