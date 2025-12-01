" must load Java first since it screws up `syntax spell`
" see https://vi.stackexchange.com/questions/18335/vim-cannot-check-markdown-spell
let g:markdown_fenced_languages = ['java']
let g:markdown_fenced_languages += ['css', 'html', 'javascript', 'python', 'sh', 'vim']
setlocal expandtab
setlocal wrap
if !empty(glob('~/bin/mfmd.sh'))
	setlocal makeprg=$HOME/bin/mfmd.sh\ '%:p'\ >\ '%:p:r.html'
	augroup justinnhli_markdown_make_on_write
		autocmd!
		autocmd BufWritePre *.md silent %s#\(^\|[^(<]\)\(\<https\?://[^[:blank:]()]\+\>/\?\)#\1<\2>#ge
		autocmd BufWritePost *.md silent make
	augroup END
endif
if executable('fmt')
	setlocal formatprg=fmt\ -w\ 2500
endif
execute 'source ' .. fnamemodify($MYVIMRC, ':p:h') .. '/autocorrect.vim'
