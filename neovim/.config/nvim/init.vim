" vim: foldmethod=marker

" vint: -ProhibitSetNoCompatible

" preamble {{{1

" preamble {{{3
set nocompatible " neovim default
set encoding=utf-8 " neovim default
scriptencoding utf-8

let g:python3_host_prog = $PYTHON_VENV_HOME .. '/neovim/bin/python3'

let g:os = tolower(substitute(system('uname'), '\n', '', ''))

let g:justinnhli_pim_path=expand('~/Dropbox/pim')
let g:justinnhli_scholarship_path=expand('~/Dropbox/scholarship')
let g:justinnhli_library_path=expand('~/papers')

let g:large_file_size = 1024 * 1024 * 10 " define a large file as > 10MB

" vimplug {{{1

" vimplug {{{3
if has('nvim') && !empty($MYVIMRC)
	"auto-install vim-plug
	let s:plug_path = fnamemodify($MYVIMRC, ':p:h') .. '/autoload/plug.vim'
	if !filereadable(s:plug_path)
		call system('curl -fLo ' .. s:plug_path .. ' --create-dirs "https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim"')
		if filereadable(s:plug_path)
			augroup justinnhli_vimplug
				autocmd!
				autocmd VimEnter * PlugInstall --sync | source $MYVIMRC
			augroup END
		endif
	endif

	try
		call plug#begin(expand('<sfile>:p:h') .. '/plugged')
		" tools
		Plug 'junegunn/goyo.vim'
		Plug 'mbbill/undotree'
		Plug 'tpope/vim-fugitive'
		" extensions
		Plug 'ludovicchabant/vim-gutentags'
		Plug 'rhysd/clever-f.vim'
		" color schemes
		Plug 'sainnhe/everforest'
		Plug 'cocopon/iceberg.vim'
		Plug 'morhetz/gruvbox'
		Plug 'pgdouyon/vim-yin-yang'
		" settings
		Plug 'tpope/vim-sleuth'
		" syntax
		Plug 'glench/vim-jinja2-syntax'
		Plug 'justinnhli/journal.vim'
		Plug 'keith/swift.vim'
		Plug 'leafgarland/typescript-vim'
		Plug 'raimon49/requirements.txt.vim'
		call plug#end()
	catch
	endtry
endif

" settings {{{1

" setting functions {{{3
function BuildTabLine()
	let l:tabline = ''
	let l:cur_tab = tabpagenr()
	" for each tab page
	for l:i in range(tabpagenr('$'))
		let l:buffers = tabpagebuflist(l:i + 1)
		let l:filename = fnamemodify(bufname(l:buffers[tabpagewinnr(l:i + 1) - 1]), ':p:t')
		" set highlighting
		let l:tabline .= (l:i + 1 == l:cur_tab ? '%#TabLineSel#' : '%#TabLine#')
		let l:tabline .= ' '
		" set filename
		if l:filename ==# ''
			let l:tabline .= '[No Name]'
		elseif strlen(l:filename) > 15
			let l:tabline .= l:filename[:12] .. '...'
		else
			let l:tabline .= l:filename
		endif
		let l:tabline .= ' '
		" set window number and modified flag
		let l:tabline .= '[' .. tabpagewinnr(l:i + 1,'$') .. ']'
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

function s:UseHomeTilde(path)
	if a:path =~ '^' .. $HOME
		return '~' .. a:path[strlen($HOME):]
	else
		return a:path
	endif
endfunction

function s:GetGitBranch(path)
	let l:cmd = ''
	let l:cmd .= '( '
	let l:cmd .= 'cd ' .. shellescape(fnamemodify(a:path, ':p:h'))
	let l:cmd .= ' && '
	let l:cmd .= 'git symbolic-ref --quiet --short HEAD'
	let l:cmd .= ' ) 2>/dev/null'
	let l:gitoutput = substitute(system(l:cmd), '\n\+$', '', '')
	if len(l:gitoutput) == 0
		return ''
	else
		return '(' .. l:gitoutput .. ')'
	endif
endfunc

function GetStatusLineFile()
	" gives git branch, working path, and file path
	let l:branch = <SID>GetGitBranch(expand('%:p:h'))
	let l:pwd = <SID>UseHomeTilde(getcwd()) .. '/'
	let l:filepath = <SID>UseHomeTilde(expand('%'))
	let l:max_width = winwidth(0) - 32
	if strlen(l:branch) + strlen(l:pwd) + strlen(l:filepath) + 3 > l:max_width
		let l:pwd = pathshorten(l:pwd)
		if strlen(l:branch) + strlen(l:pwd) + strlen(l:filepath) + 3 > l:max_width
			let l:filepath = pathshorten(l:filepath)
		endif
	endif
	if l:filepath =~# '^\./'
		let l:filepath = l:filepath[2:]
	endif
	return l:branch .. ' ' .. l:pwd .. ' ' .. l:filepath
endfunction

" settings {{{3
filetype plugin on
filetype indent on
if has('syntax')
	syntax enable
endif
set   autoindent " neovim default
set   autoread " neovim default
set   background=dark " neovim default
set   backspace=indent,eol,start " neovim default
set   cinoptions=(s,m1
set   confirm
set   directory=.,$XDG_DATA_HOME/nvim/sessions//,/var/tmp//
set   display=lastline,uhex
set noerrorbells
set   expandtab
set   guioptions-=L
set   guioptions-=T
set   guioptions-=r
set nohidden
set   history=10000 " neovim default
set   ignorecase
set   laststatus=2 " neovim default
set   lazyredraw
set   listchars=tab:>>,trail:.
set   number
set   scrolloff=1
set   shiftwidth=4
set   sidescroll=1 " neovim default
set   sidescrolloff=10
set   smartcase
set   smarttab " neovim default
set nostartofline " neovim default
set   tabpagemax=50 " neovim default
set   tabstop=4
set   tags+=./.tags,.tags
set   timeoutlen=500
set   whichwrap=b,s,<,>,h,l,[,]
set nowrap
if has('cmdline_info')
	set   showcmd " neovim default
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
	set   fileencoding=utf-8
endif
if has('persistent_undo')
	set   undodir=.
	set   undofile
endif
if has('statusline')
	set   statusline=
	" buffer number
	set   statusline+=%n
	" git branch, pwd, file path
	set   statusline+=\ %{GetStatusLineFile()}
	" modified
	set   statusline+=%(\ %M%)
	" file format
	set   statusline+=\ [%{&ff}]
	" byte-order mark (BOM)
	set   statusline+=%{&bomb?'[BOM]':''}
	" read only
	set   statusline+=%r
	" file type
	set   statusline+=%y
	" paste
	set   statusline+=%#ErrorMsg#%{&paste?'[paste]':''}%*
	" alignment separator
	set   statusline+=%=
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
	set   termguicolors " neovim default
endif
if has('vertsplit')
	set   splitright
endif
if has('wildmenu')
	set   wildmenu " neovim default
	set   wildmode=longest,list
	" ignore intermediate files
	set   wildignore+=*.aux,*.bbl,*.blg,*.nav,*.snm,*.toc
	" ignore compiled files
	set   wildignore+=*.pyc
	" ignore cache files
	set   wildignore+=__pycache__,.mypy_cache
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
	set   inccommand=nosplit
endif
if exists('&shada')
	set   shada='50,h
else
	set   viminfo='50,<100,h,n~/.viminfo
endif
if exists('&tagcase')
	set   tagcase=followscs
endif

" map leader {{{1

" map leader {{{3
mapclear
mapclear!
let g:mapleader = ' '

" plugin settings {{{1

" clever f {{{3
let g:clever_f_fix_key_direction = 1
let g:clever_f_timeout_ms = 5000

" fugitive {{{3
nnoremap  <leader>gg  :Git<space>
nnoremap  <leader>gb  :Git blame<cr>
nnoremap  <leader>gc  :Git commit -m ""<left>
nnoremap  <leader>gd  :Gdiffsplit<cr>
nnoremap  <leader>gp  :Git push<cr>

" goyo {{{3
nnoremap  <leader><leader>g  :Goyo<cr>

" gutentags {{{3
let g:gutentags_ctags_tagfile = '.tags'
function ShouldEnableGutentags(path) abort
	return fnamemodify(a:path, ':e') !=# 'journal'
endfunction
let g:gutentags_enabled_user_func = 'ShouldEnableGutentags'

" journal {{{3
let g:jrnl_ignore_files = split(globpath('~/journal', '*.journal'), '\n')
augroup justinnhli_journal
	autocmd  FileType  journal  nnoremap  <buffer>  <leader>j  q:iJournal -S
	autocmd  FileType  journal  xnoremap  <buffer>  <leader>j  "zyq:iJournal -S "<C-r>z"
augroup END

" netrw {{{3
let g:netrw_browse_split = 3
let g:netrw_liststyle = 3
let g:netrw_list_hide = '\.swp$,\.un\~$'
let g:netrw_winsize = 50

" sqlcomplete {{3
let g:loaded_sql_completion = 0

" undotree {{{3
nnoremap  <leader><leader>u  :UndotreeToggle<cr>

" colorscheme {{{1

" colorscheme {{{3
let g:colorschemes = []
let g:colorschemes = g:colorschemes + [['everforest', 'dark'],]
let g:colorschemes = g:colorschemes + [['gruvbox', 'light'],]
let g:colorschemes = g:colorschemes + [['yang', 'light'],]
let g:colorschemes = g:colorschemes + [['iceberg', 'light'],]
let g:colorschemes = g:colorschemes + [['default', 'dark'],]
let g:colorschemes = g:colorschemes + [['iceberg', 'dark'],]
if $TERM =~# 'color'
	let g:colorscheme_index = 0
else
	let g:colorscheme_index = len(g:colorschemes) - 1
endif
function s:SetColorScheme()
	execute 'set background=' .. g:colorschemes[g:colorscheme_index][1]
	execute 'colorscheme ' .. g:colorschemes[g:colorscheme_index][0]
	execute 'set ft=' .. &ft
endfunction
for i in range(len(g:colorschemes))
	try
		call s:SetColorScheme()
		break
	catch
		let g:colorscheme_index += 1
	endtry
endfor

" mappings {{{1

" window spawning functions {{{2

" start terminal {{{3
if exists(':terminal')
	function s:StartTerminal(pre_cmd, cmd)
		for l:pre_cmd in a:pre_cmd
			execute l:pre_cmd
		endfor
		" strip whitespace from command
		let l:cmd = trim(a:cmd)
		if l:cmd ==# ''
			terminal
			setlocal nonumber nospell scrollback=100000
			normal! 1|
			startinsert
		else
			call termopen(l:cmd)
		endif
	endfunction
endif

" window spawning mappings {{{2

" open file {{{3
nnoremap  <leader>wee  :edit<space>
nnoremap  <leader>whe  :leftabove vsplit<space>
nnoremap  <leader>wje  :rightbelow split<space>
nnoremap  <leader>wke  :leftabove split<space>
nnoremap  <leader>wle  :rightbelow vsplit<space>
nnoremap  <leader>te   :tabnew<space>

" open buffer {{{3
nnoremap  <leader>web  :buffer<space>
nnoremap  <leader>whb  :leftabove vertical sbuffer<space>
nnoremap  <leader>wjb  :rightbelow sbuffer<space>
nnoremap  <leader>wkb  :leftabove sbuffer<space>
nnoremap  <leader>wlb  :rightbelow vertical sbuffer<space>
nnoremap  <leader>tb   :tabnew<cr>:buffer<space>

" open new file {{{3
nnoremap  <leader>wen  :enew<cr>
nnoremap  <leader>whn  :leftabove vnew<cr>
nnoremap  <leader>wjn  :rightbelow new<cr>
nnoremap  <leader>wkn  :leftabove new<cr>
nnoremap  <leader>wln  :rightbelow vnew<cr>
nnoremap  <leader>tn   :tabnew<space>

" open remote file {{{3
nnoremap  <leader>wer  q:iedit scp://user@server.tld//absolute/path/to/file<esc>F:w
nnoremap  <leader>whr  q:ileftabove vsplit scp://user@server.tld//absolute/path/to/file<esc>F:w
nnoremap  <leader>wjr  q:irightbelow split scp://user@server.tld//absolute/path/to/file<esc>F:w
nnoremap  <leader>wkr  q:ileftabove split scp://user@server.tld//absolute/path/to/file<esc>F:w
nnoremap  <leader>wlr  q:irightbelow vsplit scp://user@server.tld//absolute/path/to/file<esc>F:w
nnoremap  <leader>tr   q:itabnew scp://user@server.tld//absolute/path/to/file<esc>F:w

" open terminal (at $HOME if new tab, at the directory of the current file otherwise) {{{3
if exists(':terminal')
	nnoremap  <silent>  <leader>wet  :call <SID>StartTerminal(['silent! lcd ' .. expand('%:p:h')], '')<cr>
	nnoremap  <silent>  <leader>wht  :call <SID>StartTerminal(['leftabove vnew', 'silent! lcd ' .. expand('%:p:h')], '')<cr>
	nnoremap  <silent>  <leader>wjt  :call <SID>StartTerminal(['rightbelow new', 'silent! lcd ' .. expand('%:p:h')], '')<cr>
	nnoremap  <silent>  <leader>wkt  :call <SID>StartTerminal(['leftabove new', 'silent! lcd ' .. expand('%:p:h')], '')<cr>
	nnoremap  <silent>  <leader>wlt  :call <SID>StartTerminal(['rightbelow vnew', 'silent! lcd ' .. expand('%:p:h')], '')<cr>
	nnoremap  <silent>  <leader>tt   :call <SID>StartTerminal(['tabnew', 'silent! lcd ~'], '')<cr>
	nnoremap  <silent>  <leader>tT   :call <SID>StartTerminal(['tabnew', 'silent! lcd ' .. expand('%:p:h')], '')<cr>
endif

" open file under cursor {{{3
nnoremap  <leader>we.  :execute 'edit ' .. expand('<cfile>')<cr>
nnoremap  <leader>wh.  :execute 'leftabove vsplit ' .. expand('<cfile>')<cr>
nnoremap  <leader>wj.  :execute 'rightbelow split ' .. expand('<cfile>')<cr>
nnoremap  <leader>wk.  :execute 'leftabove split ' .. expand('<cfile>')<cr>
nnoremap  <leader>wl.  :execute 'rightbelow vsplit ' .. expand('<cfile>')<cr>
nnoremap  <leader>t.   :execute 'tabnew ' .. expand('<cfile>')<cr>
xnoremap  <leader>we.  gf
xnoremap  <leader>wh.  :<C-u>leftabove vertical wincmd f<cr>
xnoremap  <leader>wj.  :<C-u>rightbelow wincmd f<cr>
xnoremap  <leader>wk.  :<C-u>leftabove wincmd f<cr>
xnoremap  <leader>wl.  :<C-u>rightbelow vertical wincmd f<cr>
xnoremap  <leader>t.   <C-w>gf

" open tag {{{3
nnoremap  <leader>weg  :execute 'tjump ' .. expand('<cword>')<cr>
nnoremap  <leader>whg  :execute 'leftabove vertical stjump ' .. expand('<cword>')<cr>
nnoremap  <leader>wjg  :execute 'rightbelow stjump ' .. expand('<cword>')<cr>
nnoremap  <leader>wkg  :execute 'leftabove stjump ' .. expand('<cword>')<cr>
nnoremap  <leader>wlg  :execute 'rightbelow vertical stjump ' .. expand('<cword>')<cr>
nnoremap  <leader>tg   <C-w><C-]><C-w>T
xnoremap  <leader>weg  "zy:<C-u>tjump <C-r>z<cr>
xnoremap  <leader>whg  "zy:<C-u>leftabove vertical stjump <C-r>z<cr>
xnoremap  <leader>wjg  "zy:<C-u>rightbelow stjump <C-r>z<cr>
xnoremap  <leader>wkg  "zy:<C-u>leftabove stjump <C-r>z<cr>
xnoremap  <leader>wlg  "zy:<C-u>rightbelow vertical stjump <C-r>z<cr>
xnoremap  <leader>tg   <C-w><C-]><C-w>T

" open grep {{{3
nnoremap  <leader>wef  q:ilvimgrep /\m\c/g **/*<esc>Fca
nnoremap  <leader>whf  :leftabove vnew<cr>q:ilvimgrep /\m\c/g **/*<esc>Fca
nnoremap  <leader>wjf  :rightbelow new<cr>q:ilvimgrep /\m\c/g **/*<esc>Fca
nnoremap  <leader>wkf  :leftabove new<cr>q:ilvimgrep /\m\c/g **/*<esc>Fca
nnoremap  <leader>wlf  :rightbelow vnew<cr>q:ilvimgrep /\m\c/g **/*<esc>Fca
nnoremap  <leader>tf   :tabnew<cr>q:ilvimgrep /\m\c/g **/*<esc>Fca
xnoremap  <leader>wef  "zy:<C-u>lvimgrep /<C-r>z/g **/*<cr>
xnoremap  <leader>whf  "zy:<C-u>leftabove vnew<cr>:lvimgrep /<C-r>z/g **/*<cr>
xnoremap  <leader>wjf  "zy:<C-u>rightbelow new<cr>:lvimgrep /<C-r>z/g **/*<cr>
xnoremap  <leader>wkf  "zy:<C-u>leftabove new<cr>:lvimgrep /<C-r>z/g **/*<cr>
xnoremap  <leader>wlf  "zy:<C-u>rightbelow vnew<cr>:lvimgrep /<C-r>z/g **/*<cr>
xnoremap  <leader>tf   "zy:<C-u>tabnew<cr>:lvimgrep /<C-r>z/g **/*<cr>

" window manipulation functions {{{2

" duplicate buffer {{{3
function s:DuplicateBuffer()
	let l:bufnum = bufnr('%')
	tabnew
	execute 'buffer ' .. l:bufnum
endfunction

" maximize window {{{3
function s:MaximizeWindow()
	if !exists('w:maximized') || w:maximized == 0
		let w:maximized = 1
		resize
		vertical resize
		augroup justinnhli_maximize_window
			autocmd!
			autocmd WinLeave * execute 'normal! \<C-w>='
		augroup END
	else
		let w:maximized = 0
		execute 'normal! \<C-w>='
		autocmd! justinnhli_maximize_window
	endif
endfunction

" close right tabs {{{3
function s:CloseRightTabs()
	let l:cur = tabpagenr()
	while l:cur < tabpagenr('$')
		execute 'tabclose ' .. (l:cur + 1)
	endwhile
endfunction

" move to relative tab {{{3
function s:MoveToRelativeTab(n)
	let l:num_tabs = tabpagenr('$')
	let l:cur_tab = tabpagenr()
	let l:cur_win = winnr('#')
	let l:cur_buf = bufnr('%')
	let l:new_tab = a:n + l:cur_tab
	if a:n == 0 || (l:num_tabs == 1 && winnr('$') == 1)
		return
	endif
	if l:new_tab < 1
		execute '0tabnew'
		let l:cur_tab += 1
	elseif l:new_tab > l:num_tabs
		execute 'tablast'
		execute 'tabnew'
	else
		if a:n < 0
			if l:num_tabs == tabpagenr('$')
				execute 'tabprev ' .. abs(a:n)
			elseif a:n != -1
				execute 'tabprev ' .. (abs(a:n) - 1)
			endif
		else
			if l:num_tabs == tabpagenr('$')
				execute 'tabnext ' .. l:new_tab
			elseif a:n != 1
				execute 'tabnext ' .. (l:new_tab - 1)
			endif
		endif
		vert botright split
	endif
	execute 'buffer ' .. l:cur_buf
	let l:new_tab = tabpagenr()
	execute 'tabnext ' .. l:cur_tab
	execute l:cur_win .. 'wincmd c'
	if l:new_tab > l:num_tabs
		execute 'tabnext ' .. (l:new_tab - 1)
	else
		execute 'tabnext ' .. l:new_tab
	endif
	" FIXME fails when new_tab is the highest tab
endfunction

" window manipulation mappings {{{2

" window manipulation mappings {{{3
nnoremap  <leader>wd     :call <SID>DuplicateBuffer()<cr>
nnoremap  <leader>wT     <C-w>T
nnoremap  <leader>wc     :close<cr>
nnoremap  <leader>wo     :only<cr>
nnoremap  <leader>w<cr>  :call <SID>MaximizeWindow()<cr>

" tab manipulation mappings {{{3
nnoremap  <leader>tc     :tabclose<cr>
nnoremap  <leader>to     :tabonly<cr>
nnoremap  <leader>tp     :call <SID>CloseRightTabs()<cr>
nnoremap  <leader>t1     :tabmove 0<cr>
nnoremap  <leader>t2     :tabmove 1<cr>
nnoremap  <leader>t3     :tabmove 2<cr>
nnoremap  <leader>t4     :tabmove 3<cr>
nnoremap  <leader>t5     :tabmove 4<cr>
nnoremap  <leader>t6     :tabmove 5<cr>
nnoremap  <leader>t7     :tabmove 6<cr>
nnoremap  <leader>t8     :tabmove 7<cr>
nnoremap  <leader>t9     :tabmove 8<cr>
nnoremap  <leader>t0     :tabmove 9<cr>
nnoremap  <leader>th     :tabmove -1<cr>
nnoremap  <leader>tl     :tabmove +1<cr>
nnoremap  <leader>t-     :call <SID>MoveToRelativeTab(-1)<cr>
nnoremap  <leader>t=     :call <SID>MoveToRelativeTab(1)<cr>

" window movement mappings {{{3
nnoremap  <C-h>  <C-w>h
nnoremap  <C-j>  <C-w>j
nnoremap  <C-k>  <C-w>k
nnoremap  <C-l>  <C-w>l

" tab movement mappings {{{3
nnoremap  <S-h>      :tabprev<cr>
nnoremap  <S-l>      :tabnext<cr>
nnoremap  <C-tab>    :tabnext<cr>
nnoremap  <C-S-tab>  :tabprev<cr>
xnoremap  <S-h>      <esc>:tabprev<cr>
xnoremap  <S-l>      <esc>:tabnext<cr>
nnoremap  <M-1>      :1tabnext<cr>
nnoremap  <M-2>      :2tabnext<cr>
nnoremap  <M-3>      :3tabnext<cr>
nnoremap  <M-4>      :4tabnext<cr>
nnoremap  <M-5>      :5tabnext<cr>
nnoremap  <M-6>      :6tabnext<cr>
nnoremap  <M-7>      :7tabnext<cr>
nnoremap  <M-8>      :8tabnext<cr>
nnoremap  <M-9>      :9tabnext<cr>
nnoremap  <M-0>      :10tabnext<cr>

" file mappings {{{2

" pim file mappings {{{3
if isdirectory(g:justinnhli_pim_path)
	nnoremap  <silent>  <leader>JJ  :tabnew <C-r>=g:justinnhli_pim_path<cr>/journal/next.journal<cr>
	nnoremap  <silent>  <leader>JL  :tabnew <C-r>=g:justinnhli_pim_path<cr>/journal/list.journal<cr>
	nnoremap  <silent>  <leader>JR  :tabnew <C-r>=g:justinnhli_pim_path<cr>/journal/repo.journal<cr>
	nnoremap  <silent>  <leader>JM  :tabnew <C-r>=g:justinnhli_pim_path<cr>/journal/memo.md<cr>
	nnoremap  <silent>  <leader>JN  :tabnew <C-r>=g:justinnhli_pim_path<cr>/notes/<C-r>=strftime('%Y-%m')<cr>.journal<cr>:$<cr>
	nnoremap  <silent>  <leader>JS  :tabnew $HOME/Dropbox/sync.txt<cr>
	nnoremap  <silent>  <leader>JD  :tabnew<cr>:r!dynalist.py mobile<cr>:0d<cr>:setlocal buftype=nowrite filetype=journal nomodifiable<cr>zM
	nnoremap  <silent>  <leader>JC  :tabnew <C-r>=g:justinnhli_pim_path<cr>/contacts/contacts.vcf<cr>
	nnoremap  <silent>  <leader>JP  :tabnew <C-r>=g:justinnhli_pim_path<cr>/library.bib<cr>
endif

" float output functions {{{3
if exists('*nvim_create_buf')
	function FloatOutput(cmd)
		" get the output to display
		let output = [''] + systemlist(a:cmd)
		let output = map(output, '" " .. v:val')
		" compute window properties
		let col = wincol() - (winwidth(0) / 2)
		let row = winline() - (winheight(0) / 2)
		if row < 0
			let row_offset = 1
			let col_offset = (col < 0 ? 0 : 1)
			let anchor = (col < 0 ? 'NW' : 'NE')
		else
			let row_offset = 0
			let col_offset = (col < 0 ? 0 : 1)
			let anchor = (col < 0 ? 'SW' : 'SE')
		endif
		" create the window
		let buf = nvim_create_buf(v:false, v:true)
		call nvim_buf_set_lines(buf, 0, -1, v:true, output)
		let opts = {
			\ 'relative': 'cursor',
			\ 'width': max(map(output, 'len(v:val)')) + 2,
			\ 'height': len(output) + 1,
			\ 'col': col_offset, 'row': row_offset,
			\ 'anchor': anchor,
			\ 'style': 'minimal',
		\}
		let win = nvim_open_win(buf, 0, opts)
		" create a remap to close the window
		execute 'nnoremap  <buffer>  <cr>  :call nvim_win_close(' .. win .. ', v:false) \| nunmap <buffer> <lt>cr><cr>'
	endfunction
endif

" float output mappings {{{3
if exists('*FloatOutput')
	nnoremap  <leader>cc  :call FloatOutput('python3 -c "print()"')<left><left><left><left>
	xnoremap  <leader>cc  "zy:call FloatOutput('python3 -c "print(<C-r>z)"')<cr>
	nnoremap  <leader>ca  :call FloatOutput('ccal.py')<cr>
	xnoremap  <leader>ca  "zy:call FloatOutput('ccal.py <C-r>z')<cr>
endif

" open external functions {{{3
function s:OpenExternal(arg)
	let l:target = trim(a:arg)
	if l:target !=# '.' && l:target !=# '..' && l:target !=# '~'
		let l:target = substitute(l:target, '^[^~/0-9A-Za-z.]*', '', '')
		let l:target = substitute(l:target, '[^/0-9A-Za-z-]*$', '', '')
	endif
	if l:target =~# '^[^{}]*$' && (isdirectory(expand(l:target)) || filereadable(expand(l:target)))
		" file or directory
		let l:target = expand(l:target)
	elseif l:target =~# '[A-Za-z]\+[0-9]\{4\}[A-Z][A-Za-z]*'
		" research paper
		let l:paper_id = substitute(l:target, '^.\{-}\([A-Za-z]\+[0-9]\{4\}[A-Z][0-9A-Za-z]*\).*$', '\1', '')
		let l:target = expand(system('find ' .. g:justinnhli_library_path .. ' -name ' .. l:paper_id .. '.pdf'))
	elseif l:target =~# '[A-Za-z]\+[0-9A-Za-z.]\+@[0-9A-Za-z.]\+\.[0-9A-Za-z.]\+'
		" email
		let l:target = 'https://mail.google.com/mail/u/0/?tf=cm&to=' .. l:target
	elseif l:target =~# 'https\?://'
		" URL; further process to delete everything up to the first 'http'
		let l:target = substitute(l:target, '^.\{-\}\(https\?://\)', '\1', '')
	else
		let l:target = ''
	endif
	if l:target ==# ''
		echo 'executing `gx`'
		normal! gx
		return
	endif
	let l:target = trim(l:target)
	if g:os ==# 'linux'
		let l:program = 'xdg-open'
	else
		let l:program = 'open'
	endif
	call jobstart([l:program, l:target])
	echo 'executing ' .. l:program .. ' ' .. l:target
endfunction

" open external mappings{{{3
nnoremap  <leader>O  :call <SID>OpenExternal('<C-r>=expand('<cWORD>')<cr>')<cr>
xnoremap  <leader>O  "zy:call <SID>OpenExternal('<C-r>z')<cr>

" vim setting mappings {{{3
nnoremap  <leader>VV   :tabnew $MYVIMRC<cr>
nnoremap  <leader>VS   :tabnew <C-r>=fnamemodify($MYVIMRC, ':p:h')<cr>/spell/en.utf-8.add<cr>
nnoremap  <leader>VZ   :tabnew <C-r>=fnamemodify($MYVIMRC, ':p:h')<cr>/autocorrect.vim<cr>

" other file mappings {{{3
nnoremap  <leader>B   :tabnew ~/.bashrc<cr>
nnoremap  <leader>H   :tabnew ~/Dropbox/personal/logs/shistory/<C-r>=strftime('%Y')<cr>.shistory<cr>

" toggle functions {{{2

" toggle scrolloff {{{3
function s:ToggleScrollOff()
	if &scrolloff == 0
		setlocal scrolloff=999
	elseif &scrolloff == 1
		setlocal scrolloff=0
	elseif &scrolloff == 999
		setlocal scrolloff=1
	endif
endfunction

" toggle colorcolumn {{{3
function s:ToggleColorColumn()
	if &colorcolumn == 0
		setlocal colorcolumn=80
	elseif &colorcolumn == 80
		setlocal colorcolumn=100
	else
		setlocal colorcolumn=0
	endif
endfunction

" toggle diff {{{3
function s:ToggleDiff()
	if &diff
		diffoff
	else
		diffthis
	endif
endfunction

" toggle foldmethod {{{3
function s:ToggleFoldMethod()
	if &foldmethod ==# 'indent'
		setlocal foldmethod=syntax
	elseif &foldmethod ==# 'syntax'
		setlocal foldmethod=indent
	endif
endfunction

" toggle colorscheme {{{3
function s:ToggleColorScheme()
	let g:colorscheme_index += 1
	let g:colorscheme_index = g:colorscheme_index % len(g:colorschemes)
	call s:SetColorScheme()
endfunction

" toggle spellcheck {{{3
function s:ToggleSpellCheck()
	let l:spellgroups = ['SpellBad', 'SpellCap', 'SpellRare', 'SpellLocal']
	if &spell == 0
		setlocal spell
		for group in l:spellgroups
			execute 'highlight clear ' .. group
		endfor
		call s:SetColorScheme()
	elseif execute('highlight SpellBad') !~? 'links to Error'
		setlocal spell
		for group in l:spellgroups
			execute 'highlight clear ' .. group
			execute 'highlight link ' .. group .. ' Error'
		endfor
	else
		setlocal nospell
	endif
endfunction

" setting toggle mappings {{{2

" setting toggle mappings {{{3
nnoremap  <leader><leader>0  :call <SID>ToggleScrollOff()<cr>:set scrolloff?<cr>
nnoremap  <leader><leader>c  :call <SID>ToggleColorColumn()<cr>:setlocal colorcolumn?<cr>
nnoremap  <leader><leader>d  :call <SID>ToggleDiff()<cr>:echo (&diff ? 'diffthis' : 'diffoff')<cr>
nnoremap  <leader><leader>f  :call <SID>ToggleFoldMethod()<cr>:set foldmethod?<cr>
nnoremap  <leader><leader>l  :set list! list?<cr>
nnoremap  <leader><leader>m  :call <SID>ToggleColorScheme()<cr>:echo &background g:colors_name<cr>
nnoremap  <leader><leader>n  :set number! number?<cr>
nnoremap  <leader><leader>p  :set paste! paste?<cr>
nnoremap  <leader><leader>s  :call <SID>ToggleSpellCheck()<cr>:set spell?<cr>
nnoremap  <leader><leader>w  :set wrap! wrap?<cr>
nnoremap  <leader><leader>/  :set hlsearch! hlsearch?<cr>

" text movement functions {{{2

" indent text object {{{3
function s:IndentTextObject(updown, inout, visual)
	if a:visual
		normal! gv
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

" text movement mappings {{{2

" within-line movement mappings {{{3
nnoremap  <C-a>  ^
nnoremap  <C-e>  $
cnoremap  <C-a>  <home>
cnoremap  <C-e>  <end>
inoremap  <C-a>  <home>
inoremap  <C-e>  <end>
xnoremap  <C-a>  <home>
xnoremap  <C-e>  <end>

" text indent movement mappings {{{3
nnoremap  <silent>  [,  :<C-u>call <SID>IndentTextObject(-1, -1, 0)<cr>
nnoremap  <silent>  [.  :<C-u>call <SID>IndentTextObject(-1, 0, 0)<cr>
nnoremap  <silent>  [/  :<C-u>call <SID>IndentTextObject(-1, 1, 0)<cr>
nnoremap  <silent>  ],  :<C-u>call <SID>IndentTextObject(1, -1, 0)<cr>
nnoremap  <silent>  ].  :<C-u>call <SID>IndentTextObject(1, 0, 0)<cr>
nnoremap  <silent>  ]/  :<C-u>call <SID>IndentTextObject(1, 1, 0)<cr>
onoremap  <silent>  [,  :<C-u>call <SID>IndentTextObject(-1, -1, 0)<cr>
onoremap  <silent>  [.  :<C-u>call <SID>IndentTextObject(-1, 0, 0)<cr>
onoremap  <silent>  [/  :<C-u>call <SID>IndentTextObject(-1, 1, 0)<cr>
onoremap  <silent>  ],  :<C-u>call <SID>IndentTextObject(1, -1, 0)<cr>
onoremap  <silent>  ].  :<C-u>call <SID>IndentTextObject(1, 0, 0)<cr>
onoremap  <silent>  ]/  :<C-u>call <SID>IndentTextObject(1, 1, 0)<cr>
xnoremap  <silent>  [,  <esc>:call <SID>IndentTextObject(-1, -1, 1)<cr><esc>gv
xnoremap  <silent>  [.  <esc>:call <SID>IndentTextObject(-1, 0, 1)<cr><esc>gv
xnoremap  <silent>  [/  <esc>:call <SID>IndentTextObject(-1, 1, 1)<cr><esc>gv
xnoremap  <silent>  ],  <esc>:call <SID>IndentTextObject(1, -1, 1)<cr><esc>gv
xnoremap  <silent>  ].  <esc>:call <SID>IndentTextObject(1, 0, 1)<cr><esc>gv
xnoremap  <silent>  ]/  <esc>:call <SID>IndentTextObject(1, 0, 1)<cr><esc>gv

" paragraph movement mappings {{{3
nnoremap  <expr>  }  foldclosed(search('^$', 'Wn')) == -1 ? "}" : "}j}"
nnoremap  <expr>  {  foldclosed(search('^$', 'Wnb')) == -1 ? "{" : "{k{"

" quickfix/location functions {{{2

" next quickfix/location {{{3
function s:NextQuickFixOrLocation()
	lopen
	lnext
endfunction
" prev quickfix/location {{{3
function s:PrevQuickFixOrLocation()
	lopen
	lprev
endfunction
" load buffers into location list {{{3
function s:LExprBuffers()
    let l:buffers = getbufinfo({'buflisted': 1})
    let l:result = []
    for l:buffer in l:buffers
        if l:buffer['hidden'] || empty(l:buffer['name']) || empty(l:buffer['windows'])
			continue
        endif
		if l:buffer['name'] =~# '^term:'
			continue
		endif
		let l:message = printf('buffer: %s; windows: %s', l:buffer['bufnr'], l:buffer['windows'])
		call add(l:result, fnamemodify(l:buffer['name'], ':p:~') .. ':0:' .. l:message)
    endfor
    return l:result
endfunction

" quickfix/location mappings {{{2

" create location lists from various sources {{{3
nnoremap  <leader>lb  :lgetexpr <SID>LExprBuffers() <bar> :lopen<cr>

" move to next quickfix/location {{{3
" TODO turn into autocmd that automatically maps to quickfix and location
" the event is QuickFixCmdPost
" check if location list is open with if get(getloclist(0, {'winid':0}), 'winid', 0)
nnoremap  <S-j>    :silent! call <SID>NextQuickFixOrLocation()<cr>
nnoremap  <S-k>    :silent! call <SID>PrevQuickFixOrLocation()<cr>
nnoremap  <C-S-j>  :silent! lnfile<cr>
nnoremap  <C-S-k>  :silent! lpfile<cr>

" disabled mappings {{{2

" disable arrow keys {{{3
nnoremap  <up>       <nop>
nnoremap  <down>     <nop>
nnoremap  <left>     <nop>
nnoremap  <right>    <nop>
nnoremap  <C-up>     <nop>
nnoremap  <C-down>   <nop>
nnoremap  <C-left>   <nop>
nnoremap  <C-right>  <nop>
nnoremap  <S-up>     <nop>
nnoremap  <S-down>   <nop>
nnoremap  <S-left>   <nop>
nnoremap  <S-right>  <nop>
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
xnoremap  <up>       <nop>
xnoremap  <down>     <nop>
xnoremap  <left>     <nop>
xnoremap  <right>    <nop>
xnoremap  <C-up>     <nop>
xnoremap  <C-down>   <nop>
xnoremap  <C-left>   <nop>
xnoremap  <C-right>  <nop>
xnoremap  <S-up>     <nop>
xnoremap  <S-down>   <nop>
xnoremap  <S-left>   <nop>
xnoremap  <S-right>  <nop>

" disable right mouse {{{3
nnoremap  <rightmouse>    <nop>
nnoremap  <2-rightmouse>  <nop>
nnoremap  <3-rightmouse>  <nop>
nnoremap  <4-rightmouse>  <nop>
inoremap  <rightmouse>    <nop>
inoremap  <2-rightmouse>  <nop>
inoremap  <3-rightmouse>  <nop>
inoremap  <4-rightmouse>  <nop>
xnoremap  <rightmouse>    <nop>
xnoremap  <2-rightmouse>  <nop>
xnoremap  <3-rightmouse>  <nop>
xnoremap  <4-rightmouse>  <nop>

" disable function keys {{{3
nnoremap  <F1>   <nop>
nnoremap  <F2>   <nop>
nnoremap  <F3>   <nop>
nnoremap  <F4>   <nop>
nnoremap  <F5>   <nop>
nnoremap  <F6>   <nop>
nnoremap  <F7>   <nop>
nnoremap  <F8>   <nop>
nnoremap  <F9>   <nop>
nnoremap  <F10>  <nop>
nnoremap  <F11>  <nop>
nnoremap  <F12>  <nop>
inoremap  <F1>   <nop>
inoremap  <F2>   <nop>
inoremap  <F3>   <nop>
inoremap  <F4>   <nop>
inoremap  <F5>   <nop>
inoremap  <F6>   <nop>
inoremap  <F7>   <nop>
inoremap  <F8>   <nop>
inoremap  <F9>   <nop>
inoremap  <F10>  <nop>
inoremap  <F11>  <nop>
inoremap  <F12>  <nop>
" disable Shift+JK in visual mode
xnoremap  <S-j>  <nop>
xnoremap  <S-k>  <nop>
" disable manpage lookup
xnoremap  K  <nop>
" disable Ex mode
nnoremap  Q  <nop>

" editor mappings {{{2

" <C-s> to write file {{{3
nnoremap  <C-s>  :update<cr>
inoremap  <C-s>  <esc>:update<cr>
xnoremap  <C-s>  <esc>:update<cr>gv

" <C-d> to insert date {{{3
inoremap  <C-d>  <C-r>=strftime('%Y-%m-%d')<cr>

" increment/decrement numbers
nnoremap  <C-=>  <C-a>
xnoremap  <C-=>  <C-a>
nnoremap  <C-->  <C-x>
xnoremap  <C-->  <C-x>

" default to very magic search {{{3
nnoremap  /      /\v
nnoremap  ?      ?\v

" easily search for selected text {{{3
xnoremap  /      y<esc>/\V<C-r>"<cr>
xnoremap  ?      y<esc>?\V<C-r>"<cr>

" rebind n/N to always go forwards/backwards (and turns on highlighting) {{{3
nnoremap  n      :set hlsearch<cr>/<cr>zz
nnoremap  <S-n>  :set hlsearch<cr>?<cr>zz
xnoremap  n      :<C-u>set hlsearch<cr>/<cr>zz
xnoremap  <S-n>  :<C-u>set hlsearch<cr>?<cr>zz

" force the use of the command line window {{{3
nnoremap  :      :<C-f>i
nnoremap  q:     :
xnoremap  :      :<C-f>i
xnoremap  q:     :

" editing functions {{{2

" format table {{{3
function s:FormatTable(visual, use_spaces)
	" vint: -ProhibitCommandWithUnintendedSideEffect -ProhibitCommandRelyOnUser
	if a:visual
		let l:range="'<,'>"
	else
		let l:range='%'
	endif
    let l:cursor = getpos('.')
	execute l:range .. 's/\m\C  \+/	/eg'
	if a:use_spaces
		execute "silent " .. l:range .. "!column -ts '	'"
		execute l:range .. 's/\m\C \+$//eg'
	endif
	call setpos('.', l:cursor)
endfunction

" editing mappings {{{2

" editing mappings {{{3
nnoremap  <leader><bar>     :<C-u>call <SID>FormatTable(v:false, v:false)<cr>
nnoremap  <leader><bslash>  :<C-u>call <SID>FormatTable(v:false, v:true)<cr>
xnoremap  <leader><bar>     :<C-u>call <SID>FormatTable(v:true, v:false)<cr>gv
xnoremap  <leader><bslash>  :<C-u>call <SID>FormatTable(v:true, v:true)<cr>gv

" thesaurus functions {{{2

" thesaurus functions {{{3
if exists('&thesaurusfunc')
	let g:thesaurus = {}
	let s:thesaurus_path = fnamemodify($MYVIMRC, ':p:h') .. '/thesaurus.vim'
	if filereadable(s:thesaurus_path)
		execute 'source ' .. s:thesaurus_path
	endif
	function s:ThesaurusFunc(find_start, base)
		if a:find_start
			return match(getline('.')[:col('.') - 2], '.*\zs\s\ze') + 1
		elseif has_key(g:thesaurus, a:base)
			return g:thesaurus[a:base]
		else
			return []
		endif
	endfunction
	set thesaurusfunc=s:ThesaurusFunc
endif

" thesaurus mappings {{{2

" thesaurus mappings {{{3
inoremap  <C-t>  <C-x><C-t><C-n><C-n><C-p>

" other mappings {{{2

" stay in visual mode after tabbing {{{3
xnoremap  <tab>    >gv
xnoremap  <S-tab>  <gv
xnoremap  >        >gv
xnoremap  <        <gv

" select previously pasted text {{{3
nnoremap  gp       `[v`]

" jump to the end of pasted text {{{3
nnoremap  p        p`]

" make Y behave like other capitals {{{3
nnoremap  Y        y$

" rebind undo/redo traverse the undo tree instead of the undo stack {{{3
nnoremap  u        g-
nnoremap  <C-r>    g+

" get fold level of line {{{3
function s:SetFoldLevelToLine()
	if &shiftwidth == 0
		let l:fold_level = indent('.') / &tabstop
	else
		let l:fold_level = indent('.') / &shiftwidth
	endif
	execute 'set foldenable foldlevel=' .. l:fold_level
	echo l:fold_level
endfunction

" log a autocorrected spellcheck word {{{3
function s:AutoCorrectAndLog()
	" get the incorrect word and the correct word
	let l:bad_word = expand('<cword>')
	execute 'normal! 1z='
	let l:new_word = expand('<cword>')
	" ignore if the word contains non-alphabetic characters
	if l:bad_word =~# '[^A-Za-z]'
		return
	endif
	" ignore if the word is in the dictionary
	if empty(spellbadword(l:bad_word)[0])
		return
	endif
	" ignore if the only differences are in capitalization
	if tolower(l:bad_word) == tolower(l:new_word)
		return
	endif
	" add the word to the autocorrect file
	let l:autocorrect_file = fnamemodify($MYVIMRC, ':p:h') .. '/autocorrect.vim'
	call writefile(['"iabbrev  <buffer>  ' .. l:bad_word .. '  ' .. l:new_word], l:autocorrect_file, 'a')
endfunction

" miscellaneous editing mappings {{{3
nnoremap  <leader>a         ggVG
nnoremap  <leader>o         :OpenExternal<space>
nnoremap  <leader>p         "+p
nnoremap  <leader>y         "+y
xnoremap  <leader>y         "+y
nnoremap  <leader>z         :<C-u>call <SID>AutoCorrectAndLog()<cr>
nnoremap  <leader>/         :2match IncSearch ''<left>
xnoremap  <leader>/         "zy:2match IncSearch <C-r>=shellescape(getreg('z'))<cr><cr>
nnoremap  <leader>@         :<C-f>ilet @=<C-r><C-r>
nnoremap  <leader><cr>      :silent lmake<cr>
xnoremap  <leader><cr>      y<esc>:!<C-r>"<cr>
nnoremap  <leader>;         :lcd %:p:h<cr>
nnoremap  <silent>  <leader>.          :<C-u>call <SID>SetFoldLevelToLine()<cr>
if exists(':tnoremap')
	tnoremap  <esc><esc>  <C-\><C-n>
	tnoremap  <C-[><C-[>  <C-\><C-n>
	tnoremap  <S-up>  <up>
	tnoremap  <S-down>  <down>
	tnoremap  <S-left>  <left>
	tnoremap  <S-right>  <right>
	tnoremap  <S-backspace>  <backspace>
	tnoremap  <S-cr>  <cr>
endif

" commands {{{1

" float output {{{3
if exists('*FloatOutput')
	command!  -nargs=1 -complete=file  FloatOutput  :call FloatOutput(<f-args>)
endif

" open external {{{3
command!  -nargs=1 -complete=file  OpenExternal  :call <SID>OpenExternal(<f-args>)

" autocmds {{{1

" quickfix and location windows {{{3
augroup justinnhli_quickfix
	autocmd!
	" open the location window after a quickfix command
	autocmd  QuickFixCmdPost  l*  silent! lclose | lwindow
	" close the location window if it's the only window in a tab
	autocmd  WinEnter         *   if winnr('$') == 1 && getbufvar(winbufnr(winnr()), '&buftype') == 'quickfix' | quit | endif
	" hide quickfix and location windows when typing
	autocmd  InsertEnter      *   silent! lclose | silent! cclose
	" hide quickfix and location windows when the file has changed
	if exists('#TextChanged')
		autocmd  TextChanged      *   silent! lclose | silent! cclose
	endif
augroup END

" change grep {{{3
function s:GrepTrim(str)
	if a:str =~# '^\s*$'
		return a:str
	else
		return trim(a:str)
	endif
endfunction
function s:AutosetGrepMappings()
	" we need this guard because normal grep requires specifying the files to search through
	if &grepprg !~# '^grep -n '
		nnoremap  <buffer>  <leader>wef  q:isilent lgrep<space>
		execute 'nnoremap  <buffer>  <leader>whf  :leftabove vnew<cr>:setlocal filetype=' .. &filetype .. '<cr>q:isilent lgrep<space>'
		execute 'nnoremap  <buffer>  <leader>wjf  :rightbelow new<cr>:setlocal filetype=' .. &filetype .. '<cr>q:isilent lgrep<space>'
		execute 'nnoremap  <buffer>  <leader>wkf  :leftabove new<cr>:setlocal filetype=' .. &filetype .. '<cr>q:isilent lgrep<space>'
		execute 'nnoremap  <buffer>  <leader>wlf  :rightbelow vnew<cr>:setlocal filetype=' .. &filetype .. '<cr>q:isilent lgrep<space>'
		execute 'nnoremap  <buffer>  <leader>tf  :tabnew<cr>:setlocal filetype=' .. &filetype .. '<cr>q:isilent lgrep<space>'
		xnoremap  <buffer>  <leader>wef  "zy:silent lgrep <C-r>=shellescape(<SID>GrepTrim(getreg('z')))<cr><cr>
		execute 'xnoremap  <buffer>  <leader>whf  "zy:leftabove vnew<cr>:setlocal filetype=' .. &filetype .. "<cr>q:isilent lgrep <C-r>=shellescape(<SID>GrepTrim(getreg('z')))<cr><cr>"
		execute 'xnoremap  <buffer>  <leader>wjf  "zy:rightbelow new<cr>:setlocal filetype=' .. &filetype .. "<cr>q:isilent lgrep <C-r>=shellescape(<SID>GrepTrim(getreg('z')))<cr><cr>"
		execute 'xnoremap  <buffer>  <leader>wkf  "zy:leftabove new<cr>:setlocal filetype=' .. &filetype .. "<cr>q:isilent lgrep <C-r>=shellescape(<SID>GrepTrim(getreg('z')))<cr><cr>"
		execute 'xnoremap  <buffer>  <leader>wlf  "zy:rightbelow vnew<cr>:setlocal filetype=' .. &filetype .. "<cr>q:isilent lgrep <C-r>=shellescape(<SID>GrepTrim(getreg('z')))<cr><cr>"
		execute 'xnoremap  <buffer>  <leader>tf  "zy:tabnew<cr>:setlocal filetype=' .. &filetype .. "<cr>q:isilent lgrep <C-r>=shellescape(<SID>GrepTrim(getreg('z')))<cr><cr>"
	endif
endfunction
augroup justinnhli_autoset_grep_mappings
	autocmd!
	autocmd  FileType  *  call <SID>AutosetGrepMappings()
augroup END

" create intermediate directories {{{3
function s:CreateIntermediateDirectories(file, buf)
	if empty(getbufvar(a:buf, '&buftype')) && a:file!~#'\v^\w+\:\/'
		let l:dir=fnamemodify(a:file, ':h')
		if !isdirectory(l:dir)
			call mkdir(l:dir, 'p')
		endif
	endif
endfunction
augroup justinnhli_create_directories
	autocmd!
	autocmd  BufWritePre  *  :call <SID>CreateIntermediateDirectories(expand('<afile>'), +expand('<abuf>'))
augroup END

" load filetype templates {{{3
function s:LoadFiletypeTemplate()
	let l:templates_file = fnamemodify($MYVIMRC, ':p:h') .. '/templates/' .. &filetype
	if filereadable(l:templates_file)
		" read in the template file
		execute '0r ' .. l:templates_file
		" delete the blank last line
		execute '$d_'
		" place cursor at the marker and delete it
		call search(' *TODO')
		execute 'normal! "_de'
	endif
endfunction
augroup justinnhli_create_directories
	autocmd!
	autocmd  BufNewFile  *  call <SID>LoadFiletypeTemplate()
augroup END

" open directories in terminal {{{3
if exists(':terminal')
	function s:IsDir(dir) abort
		return !empty(a:dir) && isdirectory(a:dir)
	endfunction
	augroup justinnhli_open_directories
		autocmd!
		autocmd  VimEnter  *  silent! autocmd! FileExplorer *
		autocmd  BufEnter  *  if s:IsDir(expand('%')) | call <SID>StartTerminal(['silent! lcd ' .. expand('%:p:h')], '') | endif
	augroup END
endif

" reduce large files overhead {{{3
function s:HandleLargeFiles()
	" set options:
	" eventignore+=FileType (no syntax highlighting etc.; assumes FileType always on)
	" noswapfile (save copy of file)
	" bufhidden=unload (save memory when other file is viewed)
	" undolevels=-1 (no undo possible)
	if getfsize(expand('<afile>')) > g:large_file_size
		set eventignore+=FileType
		setlocal noswapfile
		setlocal bufhidden=unload
		setlocal undolevels=-1
	else
		set eventignore-=FileType
	endif
endfunction

augroup justinnhli_large_files
	autocmd!
	autocmd  BufReadPre  *  call <SID>HandleLargeFiles()
augroup END

" automatically leave insert mode {{{3
augroup justinnhli_autoleave_insert
	autocmd!
	autocmd  CursorHoldI    *         stopinsert
	autocmd  InsertEnter    *         let g:updaterestore=&updatetime | set updatetime=5000
	autocmd  InsertLeave    *         let &updatetime=g:updaterestore
augroup END

" disallow opening other files in quickfix windows {{{3
function s:LockQuickfixRead()
	if exists('w:was_quickfix') && w:was_quickfix
		let l:cur_buf = bufnr()
		close
		exec 'buffer ' .. l:cur_buf
	endif
endfunction
function s:LockQuickfixWinLeave()
	if &buftype ==# 'quickfix'
		let w:was_quickfix = 1
	endif
endfunction
augroup justinnhli_lock_quickfix
	autocmd BufRead      *  call <sid>LockQuickfixRead()
	autocmd BufWinLeave  *  call <sid>LockQuickfixWinLeave()
augroup END

" miscellaneous {{{3
augroup justinnhli_miscellaneous
	autocmd!
	" automatically reload init.vim
	autocmd  BufWritePost   init.vim  source $MYVIMRC
	" keep windows equal in size
	autocmd  VimResized     *         normal! <C-w>=
	" restore cursor position
	autocmd  BufReadPost    *         if line("'\"") > 1 && line("'\"") <= line('$') | execute 'normal! g`"' | endif
	" disable audio bell in MacVim
	autocmd  GUIEnter       *         set visualbell t_vb=
	" easily cancel the command line window
	autocmd  CmdwinEnter    *         nnoremap <buffer> <C-c> :quit<cr>
	autocmd  CmdwinEnter    *         inoremap <buffer> <C-c> <esc>
	" bound scope of search to the original window
	autocmd  WinLeave       *         let w:search_on = &hlsearch | let w:last_search = @/
	autocmd  WinEnter       *         if exists('w:search_on') && w:search_on | let @/ = w:last_search | else | set nohlsearch | endif
	" disable spellcheck in virtual terminal
	if exists('##TermOpen')
		autocmd  TermOpen   *         setlocal nonumber nospell scrollback=-1
		autocmd  TermClose  *         call feedkeys('i')
	endif
augroup END

" user functions {{{1

" UnicodeToAscii {{{3
function UnicodeToAscii()
	" vint: -ProhibitCommandWithUnintendedSideEffect -ProhibitCommandRelyOnUser
	set fileformat=unix
	" newline (0x13)
	%s/\%u000B//eg " newline
	%s/\%u000C//eg " form feed
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
	%s/\%u202F/ /eg " narrow no-break space
	" double quotes (0x22)
	%s/\%u2018\%u2018/"/eg " left single quotation mark
	%s/\%u2019\%u2019/"/eg " right single quotation mark
	%s/\%u201C/"/eg " left double quotation mark
	%s/\%u201D/"/eg " right double quotation mark
	" single quotes (0x27)
	%s/\%u02BB/'/eg " modifier letter turned comma
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
	" caret (0x5E)
	%s/\%u02C6/^/eg " modifier letter circumflex accent
	" ligatures
	%s/\%uFB00/ff/eg " ff
	%s/\%uFB01/fi/eg " fi
	%s/\%uFB02/fl/eg " fl
	%s/\%uFB03/ffi/eg " ffi
	" arrows
	%s/\%u2190/->/eg " leftwards arrow
	%s/\%u2192/->/eg " rightwards arrow
	" specials
	%s/\%uFFFC//eg " object replacement character
endfunction

" EmojiToShortcode {{{3
function EmojiToShortcode()
	" vint: -ProhibitCommandWithUnintendedSideEffect -ProhibitCommandRelyOnUser
	" other
	"😊
	"😲
	"😧
	"😣
	" remove variant selectors
	%s/\%uFE00//eg
	%s/\%uFE01//eg
	%s/\%uFE02//eg
	%s/\%uFE03//eg
	%s/\%uFE04//eg
	%s/\%uFE05//eg
	%s/\%uFE06//eg
	%s/\%uFE07//eg
	%s/\%uFE08//eg
	%s/\%uFE09//eg
	%s/\%uFE0A//eg
	%s/\%uFE0B//eg
	%s/\%uFE0C//eg
	%s/\%uFE0D//eg
	%s/\%uFE0E//eg
	%s/\%uFE0F//eg
	" replace emoji with shortcodes
	%s/☺/:smile:/eg
	%s/❤/:heart:/eg
	%s/👍/:thumbs_up:/eg
	%s/💯/:100:/eg
	%s/🖕/:middle_finger:/eg
	%s/😀/:grinning:/eg
	%s/😁/:grinning:/eg
	%s/😂/:laughing_crying_face:/eg
	%s/😃/:grinning:/eg
	%s/😄/:grinning:/eg
	%s/😅/:smiling_sweat:/eg
	%s/😆/:grinning:/eg
	%s/😇/:halo:/eg
	%s/😈/:horns:/eg
	%s/😉/:wink:/eg
	%s/😊/:blushing_smile:/eg
	%s/😋/:yum:/eg
	%s/😍/:heart_eyes:/eg
	%s/😎/:sunglasses:/eg
	%s/😏/:smirk:/eg
	%s/😓/:defeated_sweat:/eg
	%s/😘/:kiss_with_hearts:/eg
	%s/😞/:disappointed_face:/eg
	%s/😠/:anger:/eg
	%s/😡/:anger:/eg
	%s/😢/:tear:/eg
	%s/😬/:grimace:/eg
	%s/😭/:streaming_tears:/eg
	%s/😮/:open_mouth_face:/eg
	%s/🙂/:grinning:/eg
	%s/🙃/:upside_down_smile:/eg
	%s/🙄/:eye_roll:/eg
	%s/🙏/:prayer_hands:/eg
	%s/🤔/:thinking_face:/eg
	%s/🤗/:hugging_face:/eg
	%s/🤣/:rofl:/eg
	%s/🤮/:vomit:/eg
	%s/🤯/:mind_blown:/eg
	%s/🥰/:smile_with_hearts:/eg
	%s/🥲/:tear:/eg
	%s/🥺/:glossy_eyes:/eg
endfunction
