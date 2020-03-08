function s:DuplicateBufferInTab()
	let l:bufnum = bufnr('%')
	tabnew
	exec 'b '.l:bufnum
endfunction

" basic
nnoremap  <leader>wnh  :leftabove vnew<cr>
nnoremap  <leader>wnj  :rightbelow new<cr>
nnoremap  <leader>wnk  :leftabove new<cr>
nnoremap  <leader>wnl  :rightbelow vnew<cr>
nnoremap  <leader>wrh  :leftabove vsplit scp://user@server.tld//absolute/path/to/file
nnoremap  <leader>wri  :rightbelow split scp://user@server.tld//absolute/path/to/file
nnoremap  <leader>wrk  :leftabove split scp://user@server.tld//absolute/path/to/file
nnoremap  <leader>wrl  :rightbelow vsplit scp://user@server.tld//absolute/path/to/file
nnoremap  <leader>wh   :leftabove vsplit<space>
nnoremap  <leader>wj   :rightbelow split<space>
nnoremap  <leader>wk   :leftabove split<space>
nnoremap  <leader>wl   :rightbelow vsplit<space>
nnoremap  <leader>weh  :Vexplore<cr>
nnoremap  <leader>wej  :Hexplore<cr>
nnoremap  <leader>wek  :Hexplore!<cr>
nnoremap  <leader>wel  :Vexplore!<cr>
nnoremap  <leader>wo   :only<cr>
nnoremap  <leader>wc   :close<cr>
nnoremap  <leader>wd   :call <SID>DuplicateBufferInTab()<cr>

" Ctrl+HJKL for moving between windows
nnoremap  <C-h>        <C-w>h
nnoremap  <C-j>        <C-w>j
nnoremap  <C-k>        <C-w>k
nnoremap  <C-l>        <C-w>l
