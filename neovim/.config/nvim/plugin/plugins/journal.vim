let g:jrnl_ignore_files = split(globpath('~/journal', '*.journal'), '\n')

augroup justinnhli_journal
	autocmd  FileType  journal  nnoremap  <buffer>  <leader>j  q:iJournal -S
	autocmd  FileType  journal  xnoremap  <buffer>  <leader>j  "zyq:iJournal -S "<C-r>z"
	autocmd  FileType  journal  inoremap  <buffer>  <C-d>      <c-r>=strftime("%Y-%m-%d")<cr>
augroup END
