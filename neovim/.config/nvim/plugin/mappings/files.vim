let g:justinnhli_journal_path=expand('~/Dropbox/journal')
let g:justinnhli_scholarship_path=expand('~/Dropbox/scholarship')
let g:justinnhli_library_path=expand('~/papers')

" journal files
nnoremap  <leader>JL  :tabnew <C-r>=g:justinnhli_journal_path<cr>/list.journal<cr>
nnoremap  <leader>JN  :tabnew <C-r>=g:justinnhli_journal_path<cr>/next.journal<cr>
nnoremap  <leader>JR  :tabnew <C-r>=g:justinnhli_journal_path<cr>/repo.journal<cr>
" TODO make asynchronous; see :help job-control-usage
nnoremap  <leader>JD  :tabnew<cr>:r!dynalist.py mobile<cr>:0d<cr>:setlocal buftype=nowrite filetype=journal nomodifiable<cr>zM

" other special files
nnoremap  <leader>B  :tabnew ~/.bashrc<cr>
nnoremap  <leader>V  :tabnew $MYVIMRC<cr>
nnoremap  <leader>S  :tabnew ~/.config/nvim/spell/en.utf-8.add<cr>
nnoremap  <leader>C  :tabnew ~/Dropbox/personal/contacts/contacts.vcf<cr>
nnoremap  <leader>H  :tabnew ~/Dropbox/personal/logs/<C-R>=strftime('%Y')<cr>.shistory<cr>
nnoremap  <leader>T  :tabnew ~/Dropbox/personal/logs/ifttt/tweets.txt<cr>
nnoremap  <leader>R  :tabnew <C-r>=g:justinnhli_scholarship_path<cr>/journal/<C-R>=strftime('%Y')<cr>.journal<cr>:$<cr>
nnoremap  <leader>L  :tabnew <C-r>=g:justinnhli_scholarship_path<cr>/journal/library.bib<cr>
nnoremap  <leader>P  :tabnew <C-r>=g:justinnhli_scholarship_path<cr>/journal/papers<cr>

" papers
if executable('zathura')
	nnoremap  <leader>O  eb"zye:!zathura $(find <C-r>=g:justinnhli_library_path<cr> -name <C-r>=expand('<cword>')<cr>.pdf) &<cr><cr>
else
	nnoremap  <leader>O  eb"zye:!open $(find <C-r>=g:justinnhli_library_path<cr> -name <C-r>=expand('<cword>')<cr>.pdf) &<cr><cr>
endif
