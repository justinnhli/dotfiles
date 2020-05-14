function s:CloseRightTabs()
	let l:cur = tabpagenr()
	while l:cur < tabpagenr('$')
		execute 'tabclose '.(l:cur + 1)
	endwhile
endfunction

" basic
nnoremap  <leader>tn  :tabnew<space>
nnoremap  <leader>tr  :tabnew scp://user@server.tld//absolute/path/to/file
nnoremap  <leader>to  :tabonly<cr>
nnoremap  <leader>tp  :call <SID>CloseRightTabs()<cr>
nnoremap  <leader>tc  :tabclose<cr>

" Shift+HL for moving between tabs
nnoremap  <S-h>       :tabprev<cr>
nnoremap  <S-l>       :tabnext<cr>

" Meta+N and Alt+N for going to tabs
nnoremap  <M-1>       :tabnext 1<cr>
nnoremap  <M-2>       :tabnext 2<cr>
nnoremap  <M-3>       :tabnext 3<cr>
nnoremap  <M-4>       :tabnext 4<cr>
nnoremap  <M-5>       :tabnext 5<cr>
nnoremap  <M-6>       :tabnext 6<cr>
nnoremap  <M-7>       :tabnext 7<cr>
nnoremap  <M-8>       :tabnext 8<cr>
nnoremap  <M-9>       :tabnext 9<cr>
nnoremap  <M-0>       :tabnext 0<cr>

" Leader+T+N to move a tab to an absolute position
nnoremap  <leader>t1  :tabmove 0<cr>
nnoremap  <leader>t2  :tabmove 1<cr>
nnoremap  <leader>t3  :tabmove 2<cr>
nnoremap  <leader>t4  :tabmove 3<cr>
nnoremap  <leader>t5  :tabmove 4<cr>
nnoremap  <leader>t6  :tabmove 5<cr>
nnoremap  <leader>t7  :tabmove 6<cr>
nnoremap  <leader>t8  :tabmove 7<cr>
nnoremap  <leader>t9  :tabmove 8<cr>
nnoremap  <leader>t0  :tabmove 9<cr>

" Leader+T+HL to move a tab to a relative position
nnoremap  <leader>th  :tabmove -1<cr>
nnoremap  <leader>tl  :tabmove +1<cr>
