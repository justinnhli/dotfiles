set nocompatible " neovim default

let g:python3_host_prog = $PYTHON_VENV_HOME.'/neovim/bin/python3'

if has('nvim')
	"auto-install vim-plug
	if empty(glob('~/.config/nvim/autoload/plug.vim'))
		silent !curl -fLo ~/.config/nvim/autoload/plug.vim --create-dirs https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
		augroup justinnhli_vimplug
			autocmd!
			autocmd VimEnter * PlugInstall
		augroup END
	endif

	try
		call plug#begin(expand('<sfile>:p:h').'/plugged')
		" tools
		Plug 'junegunn/goyo.vim'
		Plug 'junegunn/limelight.vim'
		Plug 'mbbill/undotree'
		" extensions
		Plug 'ludovicchabant/vim-gutentags'
		Plug 'rhysd/clever-f.vim'
		Plug 'tpope/vim-fugitive'
		" color schemes
		Plug 'cocopon/iceberg.vim'
		" settings
		Plug 'tpope/vim-sleuth'
		" syntax
		Plug 'justinnhli/journal.vim', {'for': 'journal'}
		Plug 'leafgarland/typescript-vim'
		call plug#end()
	catch
	endtry
endif

" script-only functions {
	function! s:CloseRightTabs()
		let l:cur = tabpagenr()
		while l:cur < tabpagenr('$')
			exec 'tabclose '.(l:cur + 1)
		endwhile
	endfunction

	function! s:IndentTextObject(updown, inout, visual)
		if a:visual
			normal!gv
		endif
		let l:line_num = line('.')
		let l:step = (a:updown > 0 ? 1 : -1)
		let l:src_indent = indent(l:line_num)
		let l:dest_indent = l:src_indent + (a:inout * &tabstop)
		if dest_indent < 0
			let l:dest_indent = 0
		endif
		let l:cur_indent = indent(l:line_num)
		let l:line_num += l:step
		while 1 <= l:line_num && l:line_num <= line('$')
			let l:cur_indent = indent(l:line_num)
			if l:cur_indent < l:src_indent || l:cur_indent == l:dest_indent
				if a:visual && l:step == 1
					let l:line_num -= 1
				end
				call cursor(l:line_num, 0)
				return
			endif
			let l:line_num += l:step
		endwhile
	endfunction

	function! s:StartTerminal(pre_cmd, cmd)
		for l:pre_cmd in a:pre_cmd
			exec l:pre_cmd
		endfor
		let l:cmd = substitute(a:cmd, '^\s*\(.\{-}\)\s*$', '\1', '')
		if l:cmd == ''
			terminal
			normal! 1|
			startinsert
		else
			call termopen(l:cmd)
		endif
	endfunction

	function! s:ToggleColorColumn()
		if &colorcolumn == 0
			setlocal colorcolumn=80
		elseif &colorcolumn == 80
			setlocal colorcolumn=100
		else
			setlocal colorcolumn=0
		endif
	endfunction

	function! s:ToggleDiff()
		if &diff
			diffoff
		else
			diffthis
		endif
	endfunction

	function! s:ToggleFoldMethod()
		if &foldmethod ==# 'indent'
			set foldmethod=syntax
		elseif &foldmethod ==# 'syntax'
			set foldmethod=indent
		endif
	endfunction

	function! s:ToggleColorScheme()
		if g:colors_name ==# 'default'
			exec 'colorscheme '.g:colorscheme
		else
			colorscheme default
		endif
	endfunction

	function! s:DuplicateBufferInTab()
		let l:bufnum = bufnr('%')
		tabnew
		exec 'b '.l:bufnum
	endfunction

	function! s:LoadFileTypeTemplate()
		let l:templates_file = fnamemodify($MYVIMRC, ':p:h').'/templates/'.&filetype
		if filereadable(l:templates_file)
			" read in the template file
			exec '0r '.l:templates_file
			" delete the blank last line
			exec "normal! :$\<cr>dd"
			" place cursor at first triple blank line
			exec "normal! /\\n\\n\\n\<cr>jj"
		endif
	endfunction
" }

" functional functions {
	function! UnicodeToAscii()
		set fileformat=unix
		" newline (0x13)
		%s///eg " newline
		%s/\%u2029//eg " paragraph separator
		" space (0x20)
		%s/\%u000B/ /eg " vertical tab
		%s/\%u00A0/ /eg " no-break space
		%s/\%u00AD/ /eg " soft hyphen
		%s/\%u2002/ /eg " en space
		%s/\%u2003/ /eg " em space
		%s/\%u200A/ /eg " hair space
		%s/\%u200B/ /eg " zero width space
		%s/\%u2028/ /eg " line separator
		" double quotes (0x22)
		%s/\%u2018\%u2018/"/eg " left single quotation mark
		%s/\%u2019\%u2019/"/eg " right single quotation mark
		%s/\%u201C/"/eg " left double quotation mark
		%s/\%u201D/"/eg " right double quotation mark
		" single quotes (0x27)
		%s/\%u2018/'/eg " left single quotation mark
		%s/\%u2019/'/eg " right single quotation mark
		%s/\%u2032/'/eg " prime
		" parentheses (0x28, 0x29)
		%s/\%uFD3E/(/eg " ornate left parenthesis
		%s/\%uFD3F/)/eg " ornate right parenthesis
		" asterisk  (0x2A)
		%s/\%u2022/* /eg " bullet
		" hyphen (0x2D)
		%s/\%u2010/ - /eg " hyphen
		%s/\%u2013/ - /eg " en dash
		%s/\%u2014/ - /eg " em dash
		%s/\%u2015/ - /eg " horizontal bar
		%s/\%u2500/ - /eg " box drawings light horizontal
		" ellipsis (0x2E)
		%s/\%u2026/.../eg " horizontal ellipsis
		" ligatures
		%s/\%uFB01/fi/eg " fi
		%s/\%uFB02/fl/eg " fl
		" specials
		%s/\%uFFFC//eg " object replacement character
	endfunction

	function! MoveToRelTab(n)
		let l:num_tabs = tabpagenr('$')
		let l:cur_tab = tabpagenr()
		let l:cur_win = winnr('#')
		let l:cur_buf = bufnr('%')
		let l:new_tab = a:n + l:cur_tab
		if a:n == 0 || (l:num_tabs == 1 && winnr('$') == 1)
			return
		endif
		if l:new_tab < 1
			exec '0tabnew'
			let l:cur_tab += 1
		elseif l:new_tab > l:num_tabs
			exec 'tablast'
			exec 'tabnew'
		else
			if a:n < 0
				if l:num_tabs == tabpagenr('$')
					exec 'tabprev '.abs(a:n)
				elseif a:n != -1
					exec 'tabprev '.(abs(a:n)-1)
				endif
			else
				if l:num_tabs == tabpagenr('$')
					exec 'tabnext '.l:new_tab
				elseif a:n != 1
					exec 'tabnext '.(l:new_tab-1)
				endif
			endif
			vert botright split
		endif
		exec 'buffer '.l:cur_buf
		let l:new_tab = tabpagenr()
		exec 'tabnext '.l:cur_tab
		exec l:cur_win.'wincmd c'
		if l:new_tab > l:num_tabs
			exec 'tabnext '.(l:new_tab-1)
		else
			exec 'tabnext '.l:new_tab
		endif
		" FIXME fails when new_tab is the highest tab
	endfunction
" }

" setting functions {
	function! BuildTabLine()
		let l:tabline = ''
		let s:cur_tab = tabpagenr()
		" for each tab page
		for i in range(tabpagenr('$'))
			let l:buffers = tabpagebuflist(i+1)
			let l:filename = bufname(l:buffers[tabpagewinnr(i+1) - 1])
			" set highlighting
			let l:tabline .= (i+1 == s:cur_tab ? '%#TabLineSel#' : '%#TabLine#')
			let l:tabline .= ' '
			" set filename
			if l:filename ==# ''
				let l:tabline .= '[No Name]'
			else
				let l:tabline .= fnamemodify(l:filename, ':p:t')
			endif
			let l:tabline .= ' '
			" set window number and modified flag
			let l:tabline .= '['.tabpagewinnr(i+1,'$').']'
			" tab page is modified if any buffer is modified
			for b in l:buffers
				if getbufvar(b, '&modified' )
					let l:tabline .= '+'
					break
				endif
			endfor
			let l:tabline .= ' '
		endfor
		let l:tabline .= '%T%#TabLineFill#%='
		return l:tabline
	endfunction

	function! GetGitBranch()
		let gitoutput = system('git status --porcelain=1 -b '.shellescape(expand('%')).' 2>/dev/null')
		if len(gitoutput) == 0
			return ''
		endif
		" python equivalent: gitoutput.splitlines()[0]
		let line = get(split(gitoutput, '\n'), 0, '')
		" python equivalent: line.split('...')[3:]
		let branch = strpart(get(split(line, '\.\.\.'), 0, ''), 3)
		return ' ('.branch.')'
	endfunc

	function! s:PatchColorschemes()
		if g:colors_name ==# 'iceberg'
		endif
	endfunction
" }

" plugin functions {
	function! s:EnterLimelight()
		if &filetype ==# 'journal'
			let g:limelight_bop = '^.'
			let g:limelight_eop = '\ze\n'
		endif
		Limelight
	endfunction
	function! s:LeaveLimelight()
		if &filetype ==# 'journal'
			if exists('g:limelight_bop')
				unlet g:limelight_bop
			endif
			if exists('g:limelight_eop')
				unlet g:limelight_eop
			endif
		endif
		Limelight!
	endfunction
" }

" sessions {
	set   directory=.,$XDG_DATA_HOME/nvim/sessions//,/var/tmp//
	set   history=10000 " neovim default
	if exists('&shada')
		set   shada='50,h
	else
		set   viminfo='50,<100,h,n~/.viminfo
	endif
	if has('persistent_undo')
		set   undodir=.
		set   undofile
	endif
" }

" settings {
	filetype plugin on
	filetype indent on
	if has('syntax')
		syntax enable
	endif
	set   autoindent " neovim default
	set   autoread " neovim default
	set   backspace=indent,eol,start " neovim default
	set   cinoptions=(s,m1
	set   confirm
	set   display=lastline,uhex
	set noerrorbells
	set   expandtab
	set   guioptions-=L
	set   guioptions-=T
	set   guioptions-=r
	set   ignorecase
	set   laststatus=2 " neovim default
	set   lazyredraw
	set   listchars=tab:>>,trail:.
	set   mouse=
	set   number
	set   scrolloff=1
	set   shiftwidth=4
	set   sidescroll=1
	set   sidescrolloff=10
	set   smartcase
	set   smarttab " neovim default
	set nostartofline
	set   tabpagemax=50 " neovim default
	set   tabstop=4
	set   tags+=./.tags,.tags
	set   title
	set   whichwrap=b,s,<,>,h,l,[,]
	set nowrap
	if has('cmdline_info')
		set   showcmd
	endif
	if has('folding')
		set   foldclose=all
		set nofoldenable
		set   foldmethod=syntax
		set   foldminlines=0
	endif
	if has('extra_search')
		set   hlsearch " neovim default
		set   incsearch " neovim default
	endif
	if has('gui_running')
		set   visualbell
	else
		set novisualbell
	endif
	if has('insert_expand')
		set   complete=.
		set   completeopt=longest,menu
		set noinfercase
	endif
	if has('linebreak')
		set   linebreak
	endif
	if has('multi_byte')
		set nobomb
		set   encoding=utf-8 " neovim default
		set   fileencoding=utf-8
	endif
	if has('statusline')
		set   statusline=
		" buffer number
		set   statusline+=%n
		" git branch
		set   statusline+=%{GetGitBranch()}
		" file name
		set   statusline+=\ %f
		" modified
		set   statusline+=%(\ %M%)
		" file format
		set   statusline+=\ [%{&ff}]
		" read only
		set   statusline+=%r
		" file type
		set   statusline+=%y
		" paste
		set   statusline+=%#ErrorMsg#%{&paste?'[paste]':''}%*
		" alignment separator
		set   statusline+=%=
		" pwd
		set   statusline+=%<%1.30{getcwd()}
		" cursor position
		set   statusline+=\ (%l/%L,%c)
		" buffer position
		set   statusline+=%4P
	endif
	if has('syntax')
		set   spell
		set   spellcapcheck=
	endif
	if (has('termguicolors'))
		set termguicolors
	endif
	if has('vertsplit')
		set   splitright
	endif
	if has('wildmenu')
		set   wildmenu " neovim default
		set   wildmode=longest,list
		set   wildignore+=*.aux,*.bbl,*.blg,*.nav,*.pyc,*.snm,*.toc
	endif
	if has('windows')
		set   splitbelow
		set   showtabline=2
		set   tabline=%!BuildTabLine()
	endif
	if exists('&breakindent')
		set   breakindent
		set   breakindentopt=shift:1
	endif
	if exists('&esckeys')
		set noesckeys
	endif
	if exists('&inccommand')
		set inccommand=split
	endif
" }

" key mappings {
	mapclear
	mapclear!
	let g:mapleader = ' '

	" disable the default leader
	nnoremap \ <nop>
	noremap <esc> <nop>
	noremap! <esc> <nop>

	" no-ops {
		" remove all uses of arrow keys
		noremap   <up>       <nop>
		noremap   <down>     <nop>
		noremap   <left>     <nop>
		noremap   <right>    <nop>
		noremap   <C-up>     <nop>
		noremap   <C-down>   <nop>
		noremap   <C-left>   <nop>
		noremap   <C-right>  <nop>
		noremap   <S-up>     <nop>
		noremap   <S-down>   <nop>
		noremap   <S-left>   <nop>
		noremap   <S-right>  <nop>
		inoremap  <up>       <nop>
		inoremap  <down>     <nop>
		inoremap  <left>     <nop>
		inoremap  <right>    <nop>
		inoremap  <C-up>     <nop>
		inoremap  <C-down>   <nop>
		inoremap  <C-left>   <nop>
		inoremap  <C-right>  <nop>
		inoremap  <S-up>     <nop>
		inoremap  <S-down>   <nop>
		inoremap  <S-left>   <nop>
		inoremap  <S-right>  <nop>
		nnoremap  <F1>       <nop>
		nnoremap  <F2>       <nop>
		nnoremap  <F3>       <nop>
		nnoremap  <F4>       <nop>
		nnoremap  <F5>       <nop>
		nnoremap  <F6>       <nop>
		nnoremap  <F7>       <nop>
		nnoremap  <F8>       <nop>
		nnoremap  <F9>       <nop>
		nnoremap  <F10>      <nop>
		nnoremap  <F11>      <nop>
		nnoremap  <F12>      <nop>
		inoremap  <F1>       <nop>
		inoremap  <F2>       <nop>
		inoremap  <F3>       <nop>
		inoremap  <F4>       <nop>
		inoremap  <F5>       <nop>
		inoremap  <F6>       <nop>
		inoremap  <F7>       <nop>
		inoremap  <F8>       <nop>
		inoremap  <F9>       <nop>
		inoremap  <F10>      <nop>
		inoremap  <F11>      <nop>
		inoremap  <F12>      <nop>
	" }

	" text movement {
		" bash/emacs home/end commands
		nnoremap  <C-a>  ^
		nnoremap  <C-e>  $
		cnoremap  <C-a>  <Home>
		cnoremap  <C-e>  <End>
		inoremap  <C-a>  <Home>
		inoremap  <C-e>  <End>
		vnoremap  <C-a>  <Home>
		vnoremap  <C-e>  <End>

		" jump to previous/next line with less/same/more indentation
		nnoremap <silent> [, :<C-u>call <SID>IndentTextObject(-1, -1, 0)<cr>
		nnoremap <silent> [. :<C-u>call <SID>IndentTextObject(-1, 0, 0)<cr>
		nnoremap <silent> [/ :<C-u>call <SID>IndentTextObject(-1, 1, 0)<cr>
		nnoremap <silent> ], :<C-u>call <SID>IndentTextObject(1, -1, 0)<cr>
		nnoremap <silent> ]. :<C-u>call <SID>IndentTextObject(1, 0, 0)<cr>
		nnoremap <silent> ]/ :<C-u>call <SID>IndentTextObject(1, 1, 0)<cr>
		onoremap <silent> [, :<C-u>call <SID>IndentTextObject(-1, -1, 0)<cr>
		onoremap <silent> [. :<C-u>call <SID>IndentTextObject(-1, 0, 0)<cr>
		onoremap <silent> [/ :<C-u>call <SID>IndentTextObject(-1, 1, 0)<cr>
		onoremap <silent> ], :<C-u>call <SID>IndentTextObject(1, -1, 0)<cr>
		onoremap <silent> ]. :<C-u>call <SID>IndentTextObject(1, 0, 0)<cr>
		onoremap <silent> ]/ :<C-u>call <SID>IndentTextObject(1, 1, 0)<cr>
		vnoremap <silent> [, <esc>:call <SID>IndentTextObject(-1, -1, 1)<cr><esc>gv
		vnoremap <silent> [. <esc>:call <SID>IndentTextObject(-1, 0, 1)<cr><esc>gv
		vnoremap <silent> [/ <esc>:call <SID>IndentTextObject(-1, 1, 1)<cr><esc>gv
		vnoremap <silent> ], <esc>:call <SID>IndentTextObject(1, -1, 1)<cr><esc>gv
		vnoremap <silent> ]. <esc>:call <SID>IndentTextObject(1, 0, 1)<cr><esc>gv
		vnoremap <silent> ]/ <esc>:call <SID>IndentTextObject(1, 0, 1)<cr><esc>gv
	" }

	" tab management {
		nnoremap  <leader>tn  :tabnew<space>
		nnoremap  <leader>tr  :tabnew scp://user@server.tld//absolute/path/to/file
		nnoremap  <leader>te  :Texplore<cr>
		nnoremap  <leader>to  :tabonly<cr>
		nnoremap  <leader>tp  :call <SID>CloseRightTabs()<cr>
		nnoremap  <leader>tc  :tabclose<cr>

		" Shift+HL for moving between tabs
		nnoremap  <S-h>  :tabprev<cr>
		nnoremap  <S-l>  :tabnext<cr>

		" Meta+N and Alt+N for going to tabs
		nnoremap <M-1> :tabnext 1<cr>
		nnoremap <M-2> :tabnext 2<cr>
		nnoremap <M-3> :tabnext 3<cr>
		nnoremap <M-4> :tabnext 4<cr>
		nnoremap <M-5> :tabnext 5<cr>
		nnoremap <M-6> :tabnext 6<cr>
		nnoremap <M-7> :tabnext 7<cr>
		nnoremap <M-8> :tabnext 8<cr>
		nnoremap <M-9> :tabnext 9<cr>
		nnoremap <M-0> :tabnext 0<cr>

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
	" }

	" window management {
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
		if !exists('g:loaded_tmux_navigator')
			nnoremap  <C-h>  <C-w>h
			nnoremap  <C-j>  <C-w>j
			nnoremap  <C-k>  <C-w>k
			nnoremap  <C-l>  <C-w>l
		endif

		" terminal shortcuts
		if exists(':terminal')
			nnoremap       <leader>!     :call <SID>StartTerminal(['silent! lcd '.expand('%:p:h')], '')<cr>
			nnoremap       <leader>wth   :call <SID>StartTerminal(['leftabove vnew', 'silent! lcd '.expand('%:p:h')], '')<cr>
			nnoremap       <leader>wtj   :call <SID>StartTerminal(['rightbelow new', 'silent! lcd '.expand('%:p:h')], '')<cr>
			nnoremap       <leader>wtk   :call <SID>StartTerminal(['leftabove new', 'silent! lcd '.expand('%:p:h')], '')<cr>
			nnoremap       <leader>wtl   :call <SID>StartTerminal(['rightbelow vnew', 'silent! lcd '.expand('%:p:h')], '')<cr>
			nnoremap       <leader>tt    :call <SID>StartTerminal(['tabnew', 'silent! lcd ~'], '')<cr>
			nnoremap       <leader>tT    :call <SID>StartTerminal(['tabnew', 'silent! lcd '.expand('%:p:h')], '')<cr>
			vnoremap       <leader>!     y<Esc>:call <SID>StartTerminal(['silent! lcd '.expand('%:p:h')], '<C-r>"')<cr>
			vnoremap       <leader>wth   y<Esc>:call <SID>StartTerminal(['leftabove vnew', 'silent! lcd '.expand('%:p:h')], '<C-r>"')<cr>
			vnoremap       <leader>wtj   y<Esc>:call <SID>StartTerminal(['rightbelow new', 'silent! lcd '.expand('%:p:h')], '<C-r>"')<cr>
			vnoremap       <leader>wtk   y<Esc>:call <SID>StartTerminal(['leftabove new', 'silent! lcd '.expand('%:p:h')], '<C-r>"')<cr>
			vnoremap       <leader>wtl   y<Esc>:call <SID>StartTerminal(['rightbelow vnew', 'silent! lcd '.expand('%:p:h')], '<C-r>"')<cr>
			vnoremap       <leader>tt    y<Esc>:call <SID>StartTerminal(['tabnew', 'silent! lcd ~'], '<C-r>"')<cr>
			vnoremap       <leader>tT    y<Esc>:call <SID>StartTerminal(['tabnew', 'silent! lcd '.expand('%:p:h')], '<C-r>"')<cr>
		endif
	" }

	" buffer management {
		nnoremap  <leader>e    :e<space>
	" }

	" disable annoying features {
		" disable Shift+JK in visual mode
		vnoremap  <S-j>  <nop>
		vnoremap  <S-k>  <nop>

		" disable the manpage lookup
		vnoremap  K  <Nop>

		" disable Ex mode
		nnoremap  Q  <Nop>
	" }

	" search, command line, and quick fix {
		" default to very magic search
		nnoremap  /  /\v
		nnoremap  ?  ?\v

		" easily search for selected text
		vnoremap  /  y<Esc>/\V<C-r>"<cr>
		vnoremap  ?  y<Esc>?\V<C-r>"<cr>

		" rebind n/N to always go forwards/backwards (and turns on highlighting)
		nnoremap  n       :set hlsearch<cr>/<cr>zz
		nnoremap  <S-n>   :set hlsearch<cr>?<cr>zz
		vnoremap  n       :set hlsearch<cr>/<cr>zz
		vnoremap  <S-n>   :set hlsearch<cr>?<cr>zz

		" force the use of the command line window
		nnoremap  :  :<C-f>i
		nnoremap  q: :
		vnoremap  :  :<C-f>i
		vnoremap  q: :

		" Shift+JK for moving between quickfixes
		nnoremap  <S-j>  :cnext<cr>
		nnoremap  <S-k>  :cprevious<cr>
	" }

	" terminal {
		if exists(':tnoremap')
			tnoremap <Esc><Esc> <C-\><C-n>
		endif
	" }

	" editing {
		" stay in visual mode after tabbing
		vnoremap  <tab>    >gv
		vnoremap  <S-tab>  <gv
		vnoremap  >        >gv
		vnoremap  <        <gv

		" select previously pasted text
		nnoremap gp `[v`]

		" jump to the end of pasted text
		nnoremap <silent> p p`]

		" make Y behave like other capitals
		nnoremap Y y$
	" }

	" keyboard shortcuts {
		" <C-s> to write file
		nnoremap <C-s> :update<cr>
		inoremap <C-s> <esc>:update<cr>
		vnoremap <C-s> <esc>:update<cr>gv

		" rebind undo/redo traverse the undo tree instead of the undo stack
		nnoremap  u      g-
		nnoremap  <C-r>  g+
	" }

	" open special files
	let g:justinnhli_journal_path=expand('~/Dropbox/journal')
	let g:justinnhli_scholarship_path=expand('~/Dropbox/scholarship')
	let g:justinnhli_library_path=expand('~/papers')
	nnoremap           <leader>B     :tabnew ~/.bashrc<cr>
	nnoremap           <leader>V     :tabnew $MYVIMRC<cr>
	nnoremap           <leader>S     :tabnew ~/.config/nvim/spell/en.utf-8.add<cr>
	nnoremap           <leader>C     :tabnew ~/Dropbox/personal/contacts/contacts.vcf<cr>
	nnoremap           <leader>H     :tabnew ~/Dropbox/personal/logs/<C-R>=strftime('%Y')<cr>.shistory<cr>
	nnoremap           <leader>T     :tabnew ~/Dropbox/personal/logs/ifttt/tweets.txt<cr>
	nnoremap           <leader>R     :tabnew <C-r>=g:justinnhli_scholarship_path<cr>/journal/<C-R>=strftime('%Y')<cr>.journal<cr>:$<cr>
	nnoremap           <leader>L     :tabnew <C-r>=g:justinnhli_scholarship_path<cr>/journal/library.bib<cr>
	nnoremap           <leader>P     :tabnew <C-r>=g:justinnhli_scholarship_path<cr>/journal/papers<cr>
	if executable('zathura')
		nnoremap           <leader>O     eb"zye:!zathura $(find <C-r>=g:justinnhli_library_path<cr> -name <C-r>=expand('<cword>')<cr>.pdf) &<cr><cr>
	else
		nnoremap           <leader>O     eb"zye:!open $(find <C-r>=g:justinnhli_library_path<cr> -name <C-r>=expand('<cword>')<cr>.pdf) &<cr><cr>
	endif
	" open journal files with leader-J
	nnoremap           <leader>JE    :tabnew <C-r>=g:justinnhli_journal_path<cr>/next.journal<cr>
	nnoremap           <leader>JL    :tabnew <C-r>=g:justinnhli_journal_path<cr>/list.journal<cr>
	nnoremap           <leader>JR    :tabnew <C-r>=g:justinnhli_journal_path<cr>/repo.journal<cr>
	nnoremap           <leader>JD    :tabnew<cr>:r!dynalist.py mobile<cr>:0d<cr>:setlocal buftype=nowrite filetype=journal nomodifiable<cr>zM
	" toggle settings with double leader
	nnoremap           <leader><leader>c     :call <SID>ToggleColorColumn()<cr>:setlocal colorcolumn?<cr>
	nnoremap           <leader><leader>d     :call <SID>ToggleDiff()<cr>:echo (&diff ? 'diffthis' : 'diffoff')<cr>
	nnoremap           <leader><leader>f     :call <SID>ToggleFoldMethod()<cr>:set foldmethod?<cr>
	nnoremap           <leader><leader>l     :set list!<cr>:set list?<cr>
	nnoremap           <leader><leader>m     :call <SID>ToggleColorScheme()<cr>:colorscheme<cr>
	nnoremap           <leader><leader>n     :set number!<cr>:set number?<cr>
	nnoremap           <leader><leader>p     :set paste!<cr>:set paste?<cr>
	nnoremap           <leader><leader>s     :set spell!<cr>:set spell?<cr>
	nnoremap           <leader><leader>w     :set wrap!<cr>:set wrap?<cr>
	nnoremap           <leader><leader>/     :set hlsearch!<cr>:set hlsearch?<cr>
	" editor function shortcuts
	nnoremap           <leader>a     ggVG
	nnoremap           <leader>f     q:ivimgrep //g **/*<esc>Fg<left>i
	nnoremap           <leader>o     :!open<space>
	nnoremap           <leader>p     "+p
	nnoremap           <leader>y     "+y
	vnoremap           <leader>y     "+y
	nnoremap           <leader>z     1z=
	nnoremap           <leader>/     :2match IncSearch ''<left>
	nnoremap           <leader>@     :<C-f>ilet @=<C-r><C-r>
	nnoremap           <leader>]     <C-w><C-]><C-w>T
	vnoremap           <leader>]     <C-w><C-]><C-w>T
	vnoremap           <leader><bar> :s/  \+/	/eg<cr>:'<,'>!column -ts '	'<cr>gv
	nnoremap           <leader><cr>  :make<cr>
	vnoremap           <leader><cr>  y<Esc>:!<C-r>"<cr>
	nnoremap  <silent> <leader>;     :lcd %:p:h<cr>
	" custom functions
	nnoremap  <silent> <leader>.     :exec 'set foldenable foldlevel='.foldlevel('.')<cr>
" }

" autocommands {
	augroup justinnhli
		" filetypes
		autocmd  BufNewFile          *       call s:LoadFileTypeTemplate()
		" keep windows equal in size
		autocmd  VimResized          *       normal! <c-w>=
		" restore cursor position
		autocmd  BufReadPost         *       if line("'\"") > 1 && line("'\"") <= line('$') | exec 'normal! g`"' | endif
		" disable audio bell in MacVim
		autocmd  GUIEnter            *       set visualbell t_vb=
		" automatically leave insert mode after 'updatetime' milliseconds
		autocmd  CursorHoldI         *       stopinsert
		autocmd  InsertEnter         *       let updaterestore=&updatetime | set updatetime=5000
		autocmd  InsertLeave         *       let &updatetime=updaterestore
		" easily cancel the command line window
		autocmd  CmdwinEnter         *       nnoremap <buffer> <C-c> :quit<cr>
		autocmd  CmdwinEnter         *       inoremap <buffer> <C-c> <Esc>
		" automatically open and close the quickfix window
		autocmd  QuickFixCmdPost     [^l]*   nested cwindow
		autocmd  WinEnter            *       if winnr('$') == 1 && getbufvar(winbufnr(winnr()), '&buftype') == 'quickfix' | q | endif
		" bound scope of search to the original window
		autocmd  WinLeave            *       let w:search_on = &hlsearch | let w:last_search = @/
		autocmd  WinEnter            *       if exists('w:search_on') && w:search_on | let @/ = w:last_search | else | set nohlsearch | endif
		" disable spellcheck in virtual terminal
		if exists('##TermOpen')
			autocmd  TermOpen        *       setlocal nonumber nospell scrollback=-1
			autocmd  TermClose       *       call feedkeys("i")
		endif
		" patch colorschemes
		autocmd  ColorScheme         *       call s:PatchColorschemes()

		" protect large files (>10M) from sourcing and other overhead.
		" Set options:
		" eventignore+=FileType (no syntax highlighting etc.; assumes FileType always on)
		" noswapfile (save copy of file)
		" bufhidden=unload (save memory when other file is viewed)
		" undolevels=-1 (no undo possible)
		let g:LargeFile = 1024 * 1024 * 10
		autocmd BufReadPre           *       let f=expand('<afile>') | if getfsize(f) > g:LargeFile | set eventignore+=FileType | setlocal noswapfile bufhidden=unload undolevels=-1 | else | set eventignore-=FileType | endif
	augroup END
" }

" colorscheme {
	" place after autocmds to patch colors
	let g:colorscheme = 'iceberg'
	set background=dark
	try
		exec 'colorscheme '.g:colorscheme
	catch
		colorscheme default
	endtry
" }

" commands {
	function! s:TagnewCommand(args)
		tabnew
		exec 'tag '.a:args
	endfunction
	command! -nargs=1 Tagnew call <SID>TagnewCommand(<q-args>)

	command! -nargs=0 CloseRightTabs call <SID>CloseRightTabs()
	command! -nargs=1 MoveToRelTab call <SID>MoveToRelTab(<q-args>)
" }

" plugin settings {
	" clever-f
	let g:clever_f_fix_key_direction = 1
	let g:clever_f_timeout_ms = 5000
	" fugitive
	nnoremap  <leader>gg    :Git<space>
	nnoremap  <leader>gb    :Gblame<cr>
	nnoremap  <leader>gc    :Gcommit -m "
	nnoremap  <leader>gd    :Gdiff<cr>
	nnoremap  <leader>gp    :Gpush<cr>
	" goyo.vim
	nnoremap  <leader><leader>g     :Goyo<cr>
	" gutentag
	let g:gutentags_ctags_tagfile = '.tags'
	" journal.vim
	let g:jrnl_ignore_files = split(globpath('~/journal', '*.journal'), '\n')
	" limelight.vim
	augroup justinnhli_limelight
		autocmd! User GoyoEnter call <SID>EnterLimelight()
		autocmd! User GoyoLeave call <SID>LeaveLimelight()
	augroup END
	" netrw
	let g:netrw_browse_split = 3
	let g:netrw_liststyle = 3
	let g:netrw_list_hide = '\.swp$,\.un\~$'
	let g:netrw_winsize = 50
	" undotree
	nnoremap  <leader><leader>u     :UndotreeToggle<cr>
" }
