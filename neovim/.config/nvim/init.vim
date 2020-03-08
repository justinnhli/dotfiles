set nocompatible " neovim default

let g:python3_host_prog = $PYTHON_VENV_HOME.'/neovim/bin/python3'

if has('nvim')
	"auto-install vim-plug
	if empty(glob('~/.config/nvim/autoload/plug.vim'))
		silent !curl -fLo ~/.config/nvim/autoload/plug.vim --create-dirs https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim
		augroup justinnhli_vimplug
			autocmd!
			autocmd VimEnter * PlugInstall --sync | source $MYVIMRC
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
		Plug 'raimon49/requirements.txt.vim', {'for': 'requirements'}
		Plug 'leafgarland/typescript-vim'
		call plug#end()
	catch
	endtry
endif

" script-only functions {
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
	nnoremap           <leader>JL    :tabnew <C-r>=g:justinnhli_journal_path<cr>/list.journal<cr>
	nnoremap           <leader>JN    :tabnew <C-r>=g:justinnhli_journal_path<cr>/next.journal<cr>
	nnoremap           <leader>JR    :tabnew <C-r>=g:justinnhli_journal_path<cr>/repo.journal<cr>
	nnoremap           <leader>JD    :tabnew<cr>:r!dynalist.py mobile<cr>:0d<cr>:setlocal buftype=nowrite filetype=journal nomodifiable<cr>zM
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
