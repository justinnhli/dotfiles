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

" opening windows
nnoremap  <leader>wnh    :leftabove vnew<cr>
nnoremap  <leader>wnj    :rightbelow new<cr>
nnoremap  <leader>wnk    :leftabove new<cr>
nnoremap  <leader>wnl    :rightbelow vnew<cr>
nnoremap  <leader>wrh    :leftabove vsplit scp://user@server.tld//absolute/path/to/file
nnoremap  <leader>wrj    :rightbelow split scp://user@server.tld//absolute/path/to/file
nnoremap  <leader>wrk    :leftabove split scp://user@server.tld//absolute/path/to/file
nnoremap  <leader>wrl    :rightbelow vsplit scp://user@server.tld//absolute/path/to/file
nnoremap  <leader>wh     :leftabove vsplit<space>
nnoremap  <leader>wj     :rightbelow split<space>
nnoremap  <leader>wk     :leftabove split<space>
nnoremap  <leader>wl     :rightbelow vsplit<space>
nnoremap  <leader>wd     :call <SID>DuplicateBufferInTab()<cr>
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
