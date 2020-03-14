" protect large files (>10M) from sourcing and other overhead.

function s:SetLargeFile()
	" define large as > 10MB
	let g:LargeFile = 1024 * 1024 * 10
	" set options:
	" eventignore+=FileType (no syntax highlighting etc.; assumes FileType always on)
	" noswapfile (save copy of file)
	" bufhidden=unload (save memory when other file is viewed)
	" undolevels=-1 (no undo possible)
	if getfsize(expand('<afile>')) > g:LargeFile
		set eventignore+=FileType
		setlocal noswapfile bufhidden=unload undolevels=-1
	else
		set eventignore-=FileType
	endif
endfunction

augroup justinnhli_large_files
	autocmd!
	autocmd  BufReadPre  *  call <SID>SetLargeFile()
augroup END
