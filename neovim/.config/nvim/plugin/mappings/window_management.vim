function s:DuplicateBufferInTab()
	let l:bufnum = bufnr('%')
	tabnew
	execute 'b '.l:bufnum
endfunction

function s:MaximizeWindow()
	if !exists('w:maximized') || w:maximized == 0
		let w:maximized = 1
		resize
		vertical resize
		augroup justinnhli_maximize_window
			autocmd!
			autocmd WinLeave * execute "normal! \<C-w>="
		augroup END
	else
		let w:maximized = 0
		execute "normal! \<C-w>="
		autocmd! justinnhli_maximize_window
	endif
endfunction

" opening new windows
nnoremap  <leader>wnh    :leftabove vnew<cr>
nnoremap  <leader>wnj    :rightbelow new<cr>
nnoremap  <leader>wnk    :leftabove new<cr>
nnoremap  <leader>wnl    :rightbelow vnew<cr>

" opening windows
nnoremap  <leader>wh     :leftabove vsplit<space>
nnoremap  <leader>wj     :rightbelow split<space>
nnoremap  <leader>wk     :leftabove split<space>
nnoremap  <leader>wl     :rightbelow vsplit<space>

" opening remote files in new windows
nnoremap  <leader>wrh    :leftabove vsplit scp://user@server.tld//absolute/path/to/file
nnoremap  <leader>wrj    :rightbelow split scp://user@server.tld//absolute/path/to/file
nnoremap  <leader>wrk    :leftabove split scp://user@server.tld//absolute/path/to/file
nnoremap  <leader>wrl    :rightbelow vsplit scp://user@server.tld//absolute/path/to/file

" opening tags in new windows
nnoremap  <leader>wgh    :execute 'leftabove vertical stjump ' . expand('<cword>')<cr>
nnoremap  <leader>wgj    :execute 'rightbelow stjump ' . expand('<cword>')<cr>
nnoremap  <leader>wgk    :execute 'leftabove stjump ' . expand('<cword>')<cr>
nnoremap  <leader>wgl    :execute 'rightbelow vertical stjump ' . expand('<cword>')<cr>
vnoremap  <leader>wgh    "zy:leftabove vertical stjump <C-r>z<cr>
vnoremap  <leader>wgj    "zy:rightbelow stjump <C-r>z<cr>
vnoremap  <leader>wgk    "zy:leftabove stjump <C-r>z<cr>
vnoremap  <leader>wgl    "zy:rightbelow vertical stjump <C-r>z<cr>

" duplicating windows in a new tab
nnoremap  <leader>wd     :call <SID>DuplicateBufferInTab()<cr>

" moving windows to a new tab
nnoremap  <leader>wT     <C-w>T

" moving between windows
nnoremap  <C-h>          <C-w>h
nnoremap  <C-j>          <C-w>j
nnoremap  <C-k>          <C-w>k
nnoremap  <C-l>          <C-w>l

" resizing windows
nnoremap  <leader>w<cr>  :call <SID>MaximizeWindow()<cr>

" closing windows
nnoremap  <leader>wo     :only<cr>
nnoremap  <leader>wc     :close<cr>
