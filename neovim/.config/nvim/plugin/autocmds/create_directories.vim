function s:CreateNonExistantDirectories(file, buf)
	if empty(getbufvar(a:buf, '&buftype')) && a:file!~#'\v^\w+\:\/'
		let dir=fnamemodify(a:file, ':h')
		if !isdirectory(dir)
			call mkdir(dir, 'p')
		endif
	endif
endfunction

augroup justinnhli_create_directories
	autocmd!
	autocmd BufWritePre * :call <SID>CreateNonExistantDirectories(expand('<afile>'), +expand('<abuf>'))
augroup END
