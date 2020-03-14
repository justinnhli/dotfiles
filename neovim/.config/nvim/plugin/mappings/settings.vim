function s:ToggleColorColumn()
	if &colorcolumn == 0
		setlocal colorcolumn=80
	elseif &colorcolumn == 80
		setlocal colorcolumn=100
	else
		setlocal colorcolumn=0
	endif
endfunction

function s:ToggleDiff()
	if &diff
		diffoff
	else
		diffthis
	endif
endfunction

function s:ToggleFoldMethod()
	if &foldmethod ==# 'indent'
		set foldmethod=syntax
	elseif &foldmethod ==# 'syntax'
		set foldmethod=indent
	endif
endfunction

function s:ToggleColorScheme()
	if g:colors_name ==# 'default'
		execute 'colorscheme '.g:colorscheme
	else
		colorscheme default
	endif
endfunction

nnoremap            <leader><leader>c  :call <SID>ToggleColorColumn()<cr>:setlocal colorcolumn?<cr>
nnoremap            <leader><leader>d  :call <SID>ToggleDiff()<cr>:echo (&diff ? 'diffthis' : 'diffoff')<cr>
nnoremap            <leader><leader>f  :call <SID>ToggleFoldMethod()<cr>:set foldmethod?<cr>
nnoremap            <leader><leader>l  :set list!<cr>:set list?<cr>
nnoremap            <leader><leader>m  :call <SID>ToggleColorScheme()<cr>:colorscheme<cr>
nnoremap            <leader><leader>n  :set number!<cr>:set number?<cr>
nnoremap            <leader><leader>p  :set paste!<cr>:set paste?<cr>
nnoremap            <leader><leader>s  :set spell!<cr>:set spell?<cr>
nnoremap            <leader><leader>w  :set wrap!<cr>:set wrap?<cr>
nnoremap            <leader><leader>/  :set hlsearch!<cr>:set hlsearch?<cr>
nnoremap  <silent>  <leader>.          :execute 'set foldenable foldlevel='.foldlevel('.')<cr>
