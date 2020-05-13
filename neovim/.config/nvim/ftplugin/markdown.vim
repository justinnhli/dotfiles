" must load Java first since it screws up `syntax spell`
" see https://vi.stackexchange.com/questions/18335/vim-cannot-check-markdown-spell
let g:markdown_fenced_languages = ['java']
let g:markdown_fenced_languages += ['css', 'html', 'javascript', 'python', 'sh', 'vim']
setlocal expandtab
setlocal wrap
if executable('cmark')
	setlocal makeprg=cmark\ --unsafe\ '%:p'\ >\ '%:p:r.html'
endif
if executable('fmt')
	setlocal formatprg=fmt\ -w\ 2500
endif
