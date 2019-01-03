if executable('dot')
	setlocal makeprg=dot\ -Tpng\ %:p\ >\ %:p:r.png
endif
