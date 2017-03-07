set nocompatible " neovim default

let python_host_prog = 'python2'
let python3_host_prog = 'python3'

if has('nvim')
	"auto-install vim-plug
	if empty(glob('~/.config/nvim/autoload/plug.vim'))
		silent !curl -fLo ~/.config/nvim/autoload/plug.vim --create-dirs https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
		autocmd VimEnter * PlugInstall
	endif

	try
		call plug#begin(expand('<sfile>:p:h').'/plugged')
		" extensions
		Plug 'kien/ctrlp.vim'
		Plug 'mbbill/undotree'
		Plug 'rhysd/clever-f.vim'
		Plug 'tpope/vim-fugitive'
		Plug 'junegunn/goyo.vim'
		" color schemes
		Plug 'tomasr/molokai'
		" settings
		Plug 'tpope/vim-sleuth'
		Plug 'christoomey/vim-tmux-navigator'
		" syntax
		Plug 'hdima/python-syntax', {'for': 'python'}
		Plug 'justinnhli/journal.vim', {'for': 'journal'}
		call plug#end()
	catch
	endtry

	" FIXME use additional runtime directories when available: local neovim clone, Arch vim install, MacVim install
	" we need these for UTF-8 and ASCII spell files (see https://github.com/neovim/neovim/issues/1551)
	let s:vim_runtimes = [expand('~/neovim/runtime'), '/usr/share/vim/vim74', '/Applications/MacVim.app/Contents/Resources/vim/runtime']
	for runtime in s:vim_runtimes
		if isdirectory(runtime) && &runtimepath !~ runtime
			let &runtimepath = &runtimepath.','.runtime
		endif
	endfor
endif

" script-only functions {
	function! s:CloseRightTabs()
		let l:cur = tabpagenr()
		while l:cur < tabpagenr('$')
			exe 'tabclose '.(l:cur + 1)
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

	function! s:StartTerminal(...)
		for l:cmd in a:000
			exe l:cmd
		endfor
		setlocal nospell
		terminal
	endfunction

	function! s:ToggleFoldMethod()
		if &foldmethod == "indent"
			set foldmethod=syntax
		elseif &foldmethod == "syntax"
			set foldmethod=indent
		endif
	endfunction
" }

" functional functions {
	function! UnicodeToAscii()
		" space (0x20)
		%s/\%u00A0/ /eg " no-break space
		%s/\%u00AD/ /eg " soft hyphen
		%s/\%u200A/ /eg " hair space
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
		" ellipsis
		%s/\%u2026/.../eg " horizontal ellipsis
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
		exec 'b'.l:cur_buf
		let l:new_tab = tabpagenr()
		exec 'tabnext'.l:cur_tab
		exec l:cur_win.'wincmd c'
		if l:new_tab > l:num_tabs
			exec 'tabnext'.(l:new_tab-1)
		else
			exec 'tabnext'.l:new_tab
		endif
		" FIXME fails when new_tab is the highest tab
	endfunction
" }

" setting functions {
	function! MyTabLine()
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
			if l:filename == ''
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

" vim GUI {
	set   confirm
	set   display=lastline,uhex
	set noerrorbells
	set guioptions-=T
	set guioptions-=L
	set guioptions-=r
	set   laststatus=2 " neovim default
	set   lazyredraw
	set   mouse=
	if has('linebreak')
		set   linebreak
	endif
	set   number
	if has('cmdline_info')
		set   showcmd
	endif
	if has('windows')
		set   splitbelow
	endif
	if has('vertsplit')
		set   splitright
	endif
	if has('statusline')
		set   statusline=%n\ %f%(\ %M%)\ [%{&ff}]%r%y%#warningmsg#%{&paste?'[paste]':''}%*%=%<%1.30{getcwd()}\ (%l/%L,%c)%4P
	endif
	if has('windows')
		set showtabline=2
		set tabline=%!MyTabLine()
	endif
	set   tabpagemax=50 " neovim default
	set   title
	if has('gui_running')
		set   visualbell
	else
		set novisualbell
	endif
	if has('wildmenu')
		set   wildmenu " neovim default
		set   wildmode=longest,list
		set   wildignore+=*.aux,*.bbl,*.blg,*.eps,*.nav,*.pdf,*.pyc,*.snm,*.toc
	endif
	set nowrap
" }

" settings {
	filetype plugin on
	filetype indent on
	set   autoindent " neovim default
	set   autoread " neovim default
	set   backspace=indent,eol,start " neovim default
	set noesckeys
	set   ignorecase
	set   scrolloff=1
	set   shiftwidth=4
	set   sidescroll=1
	set   sidescrolloff=10
	set   smartcase
	set   smarttab " neovim default
	set nostartofline
	set   tabstop=4
	set   tags+=./.tags,.tags
	set   whichwrap=b,s,<,>,h,l,[,]
	if has('multi_byte')
		set nobomb
	endif
	if exists('&breakindent')
		set   breakindent
		set   breakindentopt=shift:1
	endif
	if has('insert_expand')
		set   complete=.
		set   completeopt=longest,menu
	endif
	if has('multi_byte')
		set   encoding=utf-8 " neovim default
	endif
	if has('multi_byte')
		set   fileencoding=utf-8
	endif
	if has('folding')
		set   foldclose=all
		set nofoldenable
		set   foldmethod=syntax
		set   foldminlines=0
	endif
	if has('extra_search')
		set   hlsearch " neovim default
	endif
	if has('insert_expand')
		set noinfercase
	endif
	if has('extra_search')
		set   incsearch " neovim default
	endif
	if exists('&inccommand')
		set inccommand=split
	endif
	if has('syntax')
		set   spell
		set   spellcapcheck=
	endif
" }

" highlighting and color {
	if has('syntax')
		syntax enable
	endif
	set background=dark
	try
		colorscheme molokai
	catch
		colorscheme default
	endtry
" }

" key mappings {
	mapclear
	mapclear!
	let g:mapleader = ' '

	" disable the default leader
	nnoremap \ <nop>

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
		nnoremap  <leader>tn  :tabnew 
		nnoremap  <leader>te  :Texplore<cr>
		nnoremap  <leader>to  :tabonly<cr>
		nnoremap  <leader>tp  :call <SID>CloseRightTabs()<cr>
		nnoremap  <leader>tc  :tabclose<cr>
		nnoremap  <leader>th  :tabmove -1<cr>
		nnoremap  <leader>tl  :tabmove +1<cr>
		nnoremap  <leader>t0  :tabmove 0<cr>
		nnoremap  <leader>t1  :tabmove 1<cr>
		nnoremap  <leader>t2  :tabmove 2<cr>
		nnoremap  <leader>t3  :tabmove 3<cr>
		nnoremap  <leader>t4  :tabmove 4<cr>
		nnoremap  <leader>t5  :tabmove 5<cr>
		nnoremap  <leader>t6  :tabmove 6<cr>
		nnoremap  <leader>t7  :tabmove 7<cr>
		nnoremap  <leader>t8  :tabmove 8<cr>
		nnoremap  <leader>t9  :tabmove 9<cr>

		" Shift+HL for moving between tabs
		noremap  <S-h>  :tabprev<cr>
		noremap  <S-l>  :tabnext<cr>
	" }

	" window management {
		nnoremap  <leader>wnh  :leftabove vnew<cr>
		nnoremap  <leader>wnj  :rightbelow new<cr>
		nnoremap  <leader>wnk  :leftabove new<cr>
		nnoremap  <leader>wnl  :rightbelow vnew<cr>
		nnoremap  <leader>wh   :leftabove vsplit 
		nnoremap  <leader>wj   :rightbelow split 
		nnoremap  <leader>wk   :leftabove split 
		nnoremap  <leader>wl   :rightbelow vsplit 
		nnoremap  <leader>weh  :Vexplore<cr>
		nnoremap  <leader>wej  :Hexplore<cr>
		nnoremap  <leader>wek  :Hexplore!<cr>
		nnoremap  <leader>wel  :Vexplore!<cr>
		nnoremap  <leader>wo   :only<cr>
		nnoremap  <leader>wc   :close<cr>

		" Ctrl+HJKL for moving between windows
		if !exists('g:loaded_tmux_navigator')
			noremap  <C-h>  <C-w>h
			noremap  <C-j>  <C-w>j
			noremap  <C-k>  <C-w>k
			noremap  <C-l>  <C-w>l
		endif

		" terminal shortcuts
		if exists(':terminal')
			nnoremap       <leader>!     :call <SID>StartTerminal('silent! lcd '.expand('%:p:h'))<cr>
			nnoremap       <leader>wth   :call <SID>StartTerminal('leftabove vnew', 'silent! lcd '.expand('%:p:h'))<cr>
			nnoremap       <leader>wtj   :call <SID>StartTerminal('rightbelow new', 'silent! lcd '.expand('%:p:h'))<cr>
			nnoremap       <leader>wtk   :call <SID>StartTerminal('leftabove new', 'silent! lcd '.expand('%:p:h'))<cr>
			nnoremap       <leader>wtl   :call <SID>StartTerminal('rightbelow vnew', 'silent! lcd '.expand('%:p:h'))<cr>
			nnoremap       <leader>tt    :call <SID>StartTerminal('tabnew', 'silent! lcd ~')<cr>
			nnoremap       <leader>tT    :call <SID>StartTerminal('tabnew', 'silent! lcd '.expand('%:p:h'))<cr>
		endif
	" }

	" buffer management {
		nnoremap  <leader>e    :e 
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
		nnoremap  <S-j>  :lnext<cr>
		nnoremap  <S-k>  :lprevious<cr>
	" }

	" terminal {
		if exists(':tnoremap')
			tnoremap <Esc><Esc> <C-\><C-n>{}
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
		inoremap <C-s> <C-o>:update<cr>

		" rebind undo/redo traverse the undo tree instead of the undo stack
		nnoremap  u      g-
		nnoremap  <C-r>  g+
	" }

	" open special files
	let g:justinnhli_journal_path=expand('~/Dropbox/journal')
	let g:justinnhli_scholarship_path=expand('~/Dropbox/scholarship')
	let g:justinnhli_library_path=expand('~/papers')
	nnoremap           <leader>B     :tabnew ~/.bashrc<cr>
	nnoremap           <leader>V     :tabnew ~/.config/nvim/init.vim<cr>
	nnoremap           <leader>C     :tabnew ~/Dropbox/personal/contacts/contacts-*<cr>
	nnoremap           <leader>H     :tabnew ~/Dropbox/personal/logs/shell_history<cr>
	nnoremap           <leader>T     :tabnew ~/Dropbox/personal/logs/ifttt/tweets.txt<cr>
	nnoremap           <leader>L     :tabnew <C-r>=g:justinnhli_scholarship_path<cr>/journal/library.bib<cr>
	nnoremap           <leader>R     :tabnew <C-r>=g:justinnhli_scholarship_path<cr>/journal/<C-R>=strftime("%Y")<cr>.journal<cr>
	nnoremap           <leader>O     eb"zye:!open $(find <C-r>=g:justinnhli_library_path<cr> -name <C-r>=expand('<cword>')<cr>.pdf)<cr><cr>
	" open journal files with leader-J
	nnoremap           <leader>JJ    :tabnew <C-r>=g:justinnhli_journal_path<cr>/notes.journal<cr>
	nnoremap           <leader>JL    :tabnew <C-r>=g:justinnhli_journal_path<cr>/list.journal<cr>
	nnoremap           <leader>JS    :tabnew <C-r>=g:justinnhli_journal_path<cr>/scratch.journal<cr>
	nnoremap           <leader>JH    :tabnew <C-r>=g:justinnhli_journal_path<cr>/htsacsd.journal<cr>
	nnoremap           <leader>JP    :tabnew <C-r>=g:justinnhli_journal_path<cr>/ponderings.journal<cr>
	nnoremap           <leader>JR    :tabnew <C-r>=g:justinnhli_journal_path<cr>/research.journal<cr>
	" toggle settings with double leader
	nnoremap           <leader><leader>f     :call <SID>ToggleFoldMethod()<cr>:set foldmethod?<cr>
	nnoremap           <leader><leader>n     :set number!<cr>:set number?<cr>
	nnoremap           <leader><leader>p     :set paste!<cr>:set paste?<cr>
	nnoremap           <leader><leader>s     :set spell!<cr>:set spell?<cr>
	nnoremap           <leader><leader>w     :set wrap!<cr>:set wrap?<cr>
	nnoremap           <leader><leader>/     :set hlsearch!<cr>:set hlsearch?<cr>
	" editor function shortcuts
	nnoremap           <leader>a     ggVG
	nnoremap           <leader>o     :!open 
	nnoremap           <leader>p     "+p
	nnoremap           <leader>y     "+y
	vnoremap           <leader>y     "+y
	nnoremap           <leader>z     1z=
	nnoremap           <leader>/     :2match IncSearch ''<left>
	nnoremap           <leader>@     :<C-f>ilet @=<C-r><C-r>
	nnoremap           <leader>]     <C-w><C-]><C-w>T
	vnoremap           <leader>]     <C-w><C-]><C-w>T
	nnoremap           <leader><cr>  :make<cr>
	nnoremap  <silent> <leader>;     :lcd %:p:h<cr>
	" custom functions
	nnoremap  <silent> <leader>.     :exe 'set foldenable foldlevel='.foldlevel('.')<cr>
" }

" autocommands {
	" filetypes
	autocmd      BufRead,BufNewFile  *.lisp  setlocal expandtab
	autocmd      BufRead,BufNewFile  *.py    setlocal foldmethod=indent tabstop=4 expandtab
	autocmd      BufRead,BufNewFile  *.tex   setlocal foldmethod=indent spell
	" keep windows equal in size
	autocmd      VimResized          *       normal <c-w>=
	" restore cursor position
	autocmd      BufReadPost         *       if line("'\"") > 1 && line("'\"") <= line('$') | exe 'normal! g`"' | endif
	" disable audio bell in MacVim
	autocmd      GUIEnter            *       set visualbell t_vb=
	" automatically leave insert mode after 'updatetime' milliseconds, which is 7.5 seconds in insert mode
	autocmd      CursorHoldI         *       stopinsert
	augroup leave_insert
		autocmd  InsertEnter         *       let updaterestore=&updatetime | set updatetime=7500
		autocmd  InsertLeave         *       let &updatetime=updaterestore
	augroup END
	" easily cancel the command line window
	augroup leave_command
		autocmd  CmdwinEnter         *       nnoremap <buffer> <C-c> :quit<cr>
		autocmd  CmdwinEnter         *       inoremap <buffer> <C-c> <Esc>:quit<cr>
	augroup END
	" automatically open and close the quickfix window
	augroup quick_fix
		autocmd  QuickFixCmdPost     l*grep* lwindow
		autocmd  WinEnter            *       if winnr('$') == 1 && getbufvar(winbufnr(winnr()), '&buftype') == 'quickfix' | q | endif
	augroup END
	" bound scope of search to the original window
	augroup last_search
		autocmd  WinLeave            *       let w:search_on = &hlsearch | let w:last_search = @/
		autocmd  WinEnter            *       if exists('w:search_on') && w:search_on | let @/ = w:last_search | else | set nohlsearch | endif
	augroup END
	" disable spellcheck in virtual terminal
	if exists('##TermOpen')
		autocmd  TermOpen            *       setlocal nospell
	endif

	" override above settings for specific files
	" automatically fold notes.journal
	autocmd       BufRead            notes.journal syntax match flag '^.\{2000,\}$' | setlocal breakindent breakindentopt=shift:1 foldenable foldlevel=0
" }

" commands {
	function! s:TagnewCommand(args)
		tabnew
		execute ':tag '.a:args
	endfunction
	command! -nargs=1 Tagnew :call s:TagnewCommand(<q-args>)

	command! -nargs=0 CloseRightTabs :call <SID>CloseRightTabs()
	command! -nargs=1 MoveToRelTab :call <SID>MoveToRelTab(<q-args>)
" }

" neovim settings {
	let g:terminal_scrollback_buffer_size = 1000000
" }

" plugin settings {
	" ctrlp
	let g:ctrlp_map = '<leader>P'
	let g:ctrlp_prompt_mappings = {
		\ 'AcceptSelection("e")': ['<c-t>'],
		\ 'AcceptSelection("t")': ['<cr>', '<2-LeftMouse>'],
		\ }
	" clever-f
	let g:clever_f_fix_key_direction = 1
	let g:clever_f_timeout_ms = 5000
	" goyo.vim
	nnoremap  <leader><leader>g     :Goyo<cr>
	" journal.vim
	let g:jrnl_ignore_files = split(globpath('~/journal', '*.journal'), '\n')
	" netrw
	let g:netrw_browse_split = 3
	let g:netrw_liststyle = 3
	let g:netrw_list_hide = '\.swp$,\.un\~$'
	let g:netrw_winsize = 50
	" python-syntax
	let g:python_highlight_all = 1
	" undotree
	nnoremap  <leader>u     :UndotreeToggle<cr>
	" vim-fugitive
	nnoremap  <leader>G     :Git 
	nnoremap  <leader>gc    :Gcommit -m "
	nnoremap  <leader>gd    :Gdiff<cr>
	nnoremap  <leader>gs    :Gstatus<cr>
	nnoremap  <leader>gp    :Gpush<cr>
" }

" protect large files from sourcing and other overhead.
" files become read only
if !exists('g:my_auto_commands_loaded')
	let g:my_auto_commands_loaded = 1
	" Large files are > 10M
	" Set options:
	" eventignore+=FileType (no syntax highlighting etc.; assumes FileType always on)
	" noswapfile (save copy of file)
	" bufhidden=unload (save memory when other file is viewed)
	" undolevels=-1 (no undo possible)
	let g:LargeFile = 1024 * 1024 * 10
	augroup LargeFile
		autocmd BufReadPre * let f=expand('<afile>') | if getfsize(f) > g:LargeFile | set eventignore+=FileType | setlocal noswapfile bufhidden=unload undolevels=-1 | else | set eventignore-=FileType | endif
	augroup END
endif
