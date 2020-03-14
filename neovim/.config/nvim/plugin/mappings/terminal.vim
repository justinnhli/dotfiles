if exists(':terminal')

	function s:StartTerminal(pre_cmd, cmd)
		for l:pre_cmd in a:pre_cmd
			execute l:pre_cmd
		endfor
		let l:cmd = substitute(a:cmd, '^\s*\(.\{-}\)\s*$', '\1', '')
		if l:cmd == ''
			terminal
			normal! 1|
			startinsert
		else
			call termopen(l:cmd)
		endif
	endfunction

	nnoremap       <leader>!     :call <SID>StartTerminal(['silent! lcd '.expand('%:p:h')], '')<cr>
	nnoremap       <leader>wth   :call <SID>StartTerminal(['leftabove vnew', 'silent! lcd '.expand('%:p:h')], '')<cr>
	nnoremap       <leader>wtj   :call <SID>StartTerminal(['rightbelow new', 'silent! lcd '.expand('%:p:h')], '')<cr>
	nnoremap       <leader>wtk   :call <SID>StartTerminal(['leftabove new', 'silent! lcd '.expand('%:p:h')], '')<cr>
	nnoremap       <leader>wtl   :call <SID>StartTerminal(['rightbelow vnew', 'silent! lcd '.expand('%:p:h')], '')<cr>
	nnoremap       <leader>tt    :call <SID>StartTerminal(['tabnew', 'silent! lcd ~'], '')<cr>
	nnoremap       <leader>tT    :call <SID>StartTerminal(['tabnew', 'silent! lcd '.expand('%:p:h')], '')<cr>
	vnoremap       <leader>!     y<Esc>:call <SID>StartTerminal(['silent! lcd '.expand('%:p:h')], '<C-r>"')<cr>
	vnoremap       <leader>wth   y<Esc>:call <SID>StartTerminal(['leftabove vnew', 'silent! lcd '.expand('%:p:h')], '<C-r>"')<cr>
	vnoremap       <leader>wtj   y<Esc>:call <SID>StartTerminal(['rightbelow new', 'silent! lcd '.expand('%:p:h')], '<C-r>"')<cr>
	vnoremap       <leader>wtk   y<Esc>:call <SID>StartTerminal(['leftabove new', 'silent! lcd '.expand('%:p:h')], '<C-r>"')<cr>
	vnoremap       <leader>wtl   y<Esc>:call <SID>StartTerminal(['rightbelow vnew', 'silent! lcd '.expand('%:p:h')], '<C-r>"')<cr>
	vnoremap       <leader>tt    y<Esc>:call <SID>StartTerminal(['tabnew', 'silent! lcd ~'], '<C-r>"')<cr>
	vnoremap       <leader>tT    y<Esc>:call <SID>StartTerminal(['tabnew', 'silent! lcd '.expand('%:p:h')], '<C-r>"')<cr>

	if exists(':tnoremap')
		tnoremap  <Esc><Esc>  <C-\><C-n>
	endif
endif
