function s:isdir(dir) abort
	return !empty(a:dir) && isdirectory(a:dir)
endfunction

augroup justinnhli_open_directories
	autocmd!
	autocmd VimEnter * silent! autocmd! FileExplorer *
	autocmd BufEnter * if s:isdir(expand('%')) | execute ':terminal' | setlocal nonumber nospell scrollback=-1 | startinsert | endif
augroup END
