let g:justinnhli_pim_path=expand('~/Dropbox/pim')
let g:justinnhli_scholarship_path=expand('~/Dropbox/scholarship')
let g:justinnhli_library_path=expand('~/papers')

" PIM files
nnoremap  <leader>JL  :tabnew <C-r>=g:justinnhli_pim_path<cr>/journal/list.journal<cr>
nnoremap  <leader>JN  :tabnew <C-r>=g:justinnhli_pim_path<cr>/journal/next.journal<cr>
nnoremap  <leader>JR  :tabnew <C-r>=g:justinnhli_pim_path<cr>/journal/repo.journal<cr>
" TODO make asynchronous; see :help job-control-usage
nnoremap  <leader>JD  :tabnew<cr>:r!dynalist.py mobile<cr>:0d<cr>:setlocal buftype=nowrite filetype=journal nomodifiable<cr>zM
nnoremap  <leader>C  :tabnew <C-r>=g:justinnhli_pim_path<cr>/contacts/contacts.vcf<cr>
nnoremap  <leader>L  :tabnew <C-r>=g:justinnhli_pim_path<cr>/library.bib<cr>
if executable('zathura')
	nnoremap  <leader>O  eb"zye:!zathura $(find <C-r>=g:justinnhli_library_path<cr> -name <C-r>=expand('<cword>')<cr>.pdf) &<cr><cr>
else
	nnoremap  <leader>O  eb"zye:!open $(find <C-r>=g:justinnhli_library_path<cr> -name <C-r>=expand('<cword>')<cr>.pdf) &<cr><cr>
endif

" other special files
nnoremap  <leader>B  :tabnew ~/.bashrc<cr>
nnoremap  <leader>V  :tabnew $MYVIMRC<cr>
nnoremap  <leader>S  :tabnew ~/.config/nvim/spell/en.utf-8.add<cr>
nnoremap  <leader>H  :tabnew ~/Dropbox/personal/logs/<C-R>=strftime('%Y')<cr>.shistory<cr>
nnoremap  <leader>T  :tabnew ~/Dropbox/personal/logs/ifttt/tweets.txt<cr>
