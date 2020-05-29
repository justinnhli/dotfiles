" vim: foldmethod=marker

" preamble {{{1
" preamble {{{2
set nocompatible " neovim default

let g:python3_host_prog = $PYTHON_VENV_HOME .. '/neovim/bin/python3'

let g:os = substitute(system('uname'), '\n', '', '')

let g:justinnhli_pim_path=expand('~/Dropbox/pim')
let g:justinnhli_scholarship_path=expand('~/Dropbox/scholarship')
let g:justinnhli_library_path=expand('~/papers')

" vimplug {{{1
" vimplug {{{2
if has('nvim')
	"auto-install vim-plug
	let s:plug_path = fnamemodify($MYVIMRC, ':p:h') .. '/autoload/plug.vim'
	if empty(glob(s:plug_path))
		call system("curl -fLo " .. s:plug_path .. " --create-dirs 'https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim'")
		augroup justinnhli_vimplug
			autocmd!
			autocmd VimEnter * PlugInstall --sync | source $MYVIMRC
		augroup END
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
		Plug 'cocopon/iceberg.vim'
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
" setting functions {{{2
function BuildTabLine()
	let l:tabline = ''
	let s:cur_tab = tabpagenr()
	" for each tab page
	for i in range(tabpagenr('$'))
		let l:buffers = tabpagebuflist(i + 1)
		let l:filename = bufname(l:buffers[tabpagewinnr(i + 1) - 1])
		" set highlighting
		let l:tabline .= (i + 1 == s:cur_tab ? '%#TabLineSel#' : '%#TabLine#')
		let l:tabline .= ' '
		" set filename
		if l:filename ==# ''
			let l:tabline .= '[No Name]'
		else
			let l:tabline .= fnamemodify(l:filename, ':p:t')
		endif
		let l:tabline .= ' '
		" set window number and modified flag
		let l:tabline .= '[' .. tabpagewinnr(i + 1,'$') .. ']'
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

function GetGitBranch()
	let gitoutput = system('git status --porcelain=1 -b ' .. shellescape(expand('%')) .. ' 2>/dev/null')
	if len(gitoutput) == 0
		return ''
	endif
	" python equivalent: gitoutput.splitlines()[0]
	let line = get(split(gitoutput, '\n'), 0, '')
	" python equivalent: line.split('...')[3:]
	let branch = strpart(get(split(line, '\.\.\.'), 0, ''), 3)
	return ' (' .. branch .. ')'
endfunc

" settings {{{2
filetype plugin on
filetype indent on
if has('syntax')
	syntax enable
endif
set   autoindent " neovim default
set   autoread " neovim default
set   background=dark
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
set   history=10000 " neovim default
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
set   timeoutlen=500
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
if has('persistent_undo')
	set   undodir=.
	set   undofile
endif
if exists('&shada')
	set   shada='50,h
else
	set   viminfo='50,<100,h,n~/.viminfo
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

" map leader {{{1
" map leader {{{2
mapclear
mapclear!
let g:mapleader = ' '

" plugin settings {{{1
" clever f {{{2
let g:clever_f_fix_key_direction = 1
let g:clever_f_timeout_ms = 5000
" fugitive {{{2
nnoremap  <leader>gg  :Git<space>
nnoremap  <leader>gb  :Git blame<cr>
nnoremap  <leader>gc  :Git commit -m "
nnoremap  <leader>gd  :Gdiffsplit<cr>
nnoremap  <leader>gp  :Git push<cr>
" goyo {{{2
nnoremap  <leader><leader>g  :Goyo<cr>
" gutentags {{{2
let g:gutentags_ctags_tagfile = '.tags'
" journal {{{2
let g:jrnl_ignore_files = split(globpath('~/journal', '*.journal'), '\n')
augroup justinnhli_journal
	autocmd  FileType  journal  nnoremap  <buffer>  <leader>j  q:iJournal -S
	autocmd  FileType  journal  xnoremap  <buffer>  <leader>j  "zyq:iJournal -S "<C-r>z"
augroup END
" netrw {{{2
let g:netrw_browse_split = 3
let g:netrw_liststyle = 3
let g:netrw_list_hide = '\.swp$,\.un\~$'
let g:netrw_winsize = 50
" undotree {{{2
nnoremap  <leader><leader>u  :UndotreeToggle<cr>

" colorscheme {{{1
" colorscheme {{{2
let g:colorscheme = 'iceberg'
try
	execute 'colorscheme ' .. g:colorscheme
catch
	colorscheme default
endtry

" mappings {{{1
" window spawning functions {{{2
" start terminal {{{3
if exists(':terminal')
	function s:StartTerminal(pre_cmd, cmd)
		for l:pre_cmd in a:pre_cmd
			execute l:pre_cmd
		endfor
		" strip whitespace from command
		let l:cmd = substitute(a:cmd, '^\s*\(.\{-}\)\s*$', '\1', '')
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
nnoremap  <leader>we  :edit<space>
nnoremap  <leader>wh  :leftabove vsplit<space>
nnoremap  <leader>wj  :rightbelow split<space>
nnoremap  <leader>wk  :leftabove split<space>
nnoremap  <leader>wl  :rightbelow vsplit<space>
nnoremap  <leader>tn  :tabnew<space>
" open new file {{{3
nnoremap  <leader>wne  :enew<cr>
nnoremap  <leader>wnh  :leftabove vnew<cr>
nnoremap  <leader>wnj  :rightbelow new<cr>
nnoremap  <leader>wnk  :leftabove new<cr>
nnoremap  <leader>wnl  :rightbelow vnew<cr>
" open remote file {{{3
nnoremap  <leader>wre  :enew<cr>scp://user@server.tld//absolute/path/to/file
nnoremap  <leader>wrh  :leftabove vsplit scp://user@server.tld//absolute/path/to/file
nnoremap  <leader>wrj  :rightbelow split scp://user@server.tld//absolute/path/to/file
nnoremap  <leader>wrk  :leftabove split scp://user@server.tld//absolute/path/to/file
nnoremap  <leader>wrl  :rightbelow vsplit scp://user@server.tld//absolute/path/to/file
nnoremap  <leader>tr   :tabnew scp://user@server.tld//absolute/path/to/file
" open terminal at $HOME {{{3
nnoremap  <leader>wte  :call <SID>StartTerminal(['silent! lcd ~'], '')<cr>
nnoremap  <leader>wth  :call <SID>StartTerminal(['leftabove vnew', 'silent! lcd ~'], '')<cr>
nnoremap  <leader>wtj  :call <SID>StartTerminal(['rightbelow new', 'silent! lcd ~'], '')<cr>
nnoremap  <leader>wtk  :call <SID>StartTerminal(['leftabove new', 'silent! lcd ~'], '')<cr>
nnoremap  <leader>wtl  :call <SID>StartTerminal(['rightbelow vnew', 'silent! lcd ~'], '')<cr>
nnoremap  <leader>tt   :call <SID>StartTerminal(['tabnew', 'silent! lcd ~'], '')<cr>
" open terminal at current location {{{3
nnoremap  <leader>wTe  :call <SID>StartTerminal(['silent! lcd ' .. expand('%:p:h')], '')<cr>
nnoremap  <leader>wTh  :call <SID>StartTerminal(['leftabove vnew', 'silent! lcd ' .. expand('%:p:h')], '')<cr>
nnoremap  <leader>wTj  :call <SID>StartTerminal(['rightbelow new', 'silent! lcd ' .. expand('%:p:h')], '')<cr>
nnoremap  <leader>wTk  :call <SID>StartTerminal(['leftabove new', 'silent! lcd ' .. expand('%:p:h')], '')<cr>
nnoremap  <leader>wTl  :call <SID>StartTerminal(['rightbelow vnew', 'silent! lcd ' .. expand('%:p:h')], '')<cr>
nnoremap  <leader>tT   :call <SID>StartTerminal(['tabnew', 'silent! lcd ' .. expand('%:p:h')], '')<cr>
" open tag {{{3
nnoremap  <leader>wge  :execute 'tjump ' .. expand('<cword>')<cr>
nnoremap  <leader>wgh  :execute 'leftabove vertical stjump ' .. expand('<cword>')<cr>
nnoremap  <leader>wgj  :execute 'rightbelow stjump ' .. expand('<cword>')<cr>
nnoremap  <leader>wgk  :execute 'leftabove stjump ' .. expand('<cword>')<cr>
nnoremap  <leader>wgl  :execute 'rightbelow vertical stjump ' .. expand('<cword>')<cr>
nnoremap  <leader>tg   <C-w><C-]><C-w>T
xnoremap  <leader>wge  "zy:tjump <C-r>z<cr>
xnoremap  <leader>wgh  "zy:leftabove vertical stjump <C-r>z<cr>
xnoremap  <leader>wgj  "zy:rightbelow stjump <C-r>z<cr>
xnoremap  <leader>wgk  "zy:leftabove stjump <C-r>z<cr>
xnoremap  <leader>wgl  "zy:rightbelow vertical stjump <C-r>z<cr>
xnoremap  <leader>tg   <C-w><C-]><C-w>T
" open grep {{{3
nnoremap  <leader>wfe  q:ivimgrep //g **/*<esc>0f/a
nnoremap  <leader>wfh  :leftabove vnew<cr>q:ivimgrep //g **/*<esc>0f/a
nnoremap  <leader>wfj  :rightbelow new<cr>q:ivimgrep //g **/*<esc>0f/a
nnoremap  <leader>wfk  :leftabove new<cr>q:ivimgrep //g **/*<esc>0f/a
nnoremap  <leader>wfl  :rightbelow vnew<cr>q:ivimgrep //g **/*<esc>0f/a
nnoremap  <leader>tf   :tabnew<cr>q:ivimgrep //g **/*<esc>0f/a
xnoremap  <leader>wfe  "zy:vimgrep /<C-r>z/g **/*<cr>
xnoremap  <leader>wfh  "zy:leftabove vnew<cr>:vimgrep /<C-r>z/g **/*<cr>
xnoremap  <leader>wfj  "zy:rightbelow new<cr>:vimgrep /<C-r>z/g **/*<cr>
xnoremap  <leader>wfk  "zy:leftabove new<cr>:vimgrep /<C-r>z/g **/*<cr>
xnoremap  <leader>wfl  "zy:rightbelow vnew<cr>:vimgrep /<C-r>z/g **/*<cr>
xnoremap  <leader>tf   "zy:tabnew<cr>:vimgrep /<C-r>z/g **/*<cr>
" window manipulation functions {{{3
function s:DuplicateBuffer()
	let l:bufnum = bufnr('%')
	tabnew
	execute 'buffer ' .. l:bufnum
endfunction
function s:MaximizeWindow()
	if !exists('w:maximized') || w:maximized == 0
		let w:maximized = 1
		resize
		vertical resize
		augroup justinnhli_maximize_window
			autocmd!
			autocmd WinLeave * execute "normal! \<C-w>="
		augroup END
	else
		let w:maximized = 0
		execute "normal! \<C-w>="
		autocmd! justinnhli_maximize_window
	endif
endfunction
function s:CloseRightTabs()
	let l:cur = tabpagenr()
	while l:cur < tabpagenr('$')
		execute 'tabclose ' .. (l:cur + 1)
	endwhile
endfunction
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
nnoremap  <leader>t-     :call MoveToRelativeTab(-1)
nnoremap  <leader>t=     :call MoveToRelativeTab(1)
" window movement mappings {{{2
" window movement mappings {{{3
nnoremap  <C-h>  <C-w>h
nnoremap  <C-j>  <C-w>j
nnoremap  <C-k>  <C-w>k
nnoremap  <C-l>  <C-w>l
" tab movement mappings {{{3
nnoremap  <S-h>  :tabprev<cr>
nnoremap  <S-l>  :tabnext<cr>
" file mappings {{{2
" pim file mappings {{{3
nnoremap  <leader>JL  :tabnew <C-r>=g:justinnhli_pim_path<cr>/journal/list.journal<cr>
nnoremap  <leader>JN  :tabnew <C-r>=g:justinnhli_pim_path<cr>/journal/next.journal<cr>
nnoremap  <leader>JR  :tabnew <C-r>=g:justinnhli_pim_path<cr>/journal/repo.journal<cr>
nnoremap  <leader>JD  :tabnew<cr>:r!dynalist.py mobile<cr>:0d<cr>:setlocal buftype=nowrite filetype=journal nomodifiable<cr>zM
nnoremap  <leader>C   :tabnew <C-r>=g:justinnhli_pim_path<cr>/contacts/contacts.vcf<cr>
nnoremap  <leader>L   :tabnew <C-r>=g:justinnhli_pim_path<cr>/library.bib<cr>
" open external functions {{{3
function s:OpenExternal(arg)
	let l:target = trim(a:arg)
	if l:target =~ '^https\?://'
		" url
		let l:target = l:target
		if g:os == 'Linux'
			let l:program = 'firefox'
		else
			let l:program = 'open'
		endif
	else
		" research paper
		let l:target = system('find ' .. g:justinnhli_library_path .. ' -name ' .. l:target .. '.pdf')
		if g:os == 'Linux'
			let l:program = 'zathura'
		else
			let l:program = 'open'
		endif
	endif
	call system(l:program .. ' ' .. l:target)
endfunction
" open external mappings{{{3
nnoremap  <leader>O  :call <SID>OpenExternal('<C-r>=expand('<cword>')<cr>')<cr>
xnoremap  <leader>O  "zy:call <SID>OpenExternal('<C-r>z')<cr>
" other file mappings {{{3
nnoremap  <leader>B   :tabnew ~/.bashrc<cr>
nnoremap  <leader>V   :tabnew $MYVIMRC<cr>
nnoremap  <leader>S   :tabnew ~/.config/nvim/spell/en.utf-8.add<cr>
nnoremap  <leader>H   :tabnew ~/Dropbox/personal/logs/<C-R>=strftime('%Y')<cr>.shistory<cr>
nnoremap  <leader>T   :tabnew ~/Dropbox/personal/logs/ifttt/tweets.txt<cr>
" toggle functions {{{2
" toggle colorcolumn {{{3
function s:ToggleColorcolumn()
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
function s:ToggleFoldmethod()
	if &foldmethod ==# 'indent'
		set foldmethod=syntax
	elseif &foldmethod ==# 'syntax'
		set foldmethod=indent
	endif
endfunction
" toggle colorscheme {{{3
function s:ToggleColorscheme()
	if g:colors_name ==# 'default'
		execute 'colorscheme ' .. g:colorscheme
	else
		colorscheme default
	endif
endfunction
" setting toggle mappings {{{2
" setting toggle mappings {{{3
nnoremap  <leader><leader>c  :call <SID>ToggleColorcolumn()<cr>:setlocal colorcolumn?<cr>
nnoremap  <leader><leader>d  :call <SID>ToggleDiff()<cr>:echo (&diff ? 'diffthis' : 'diffoff')<cr>
nnoremap  <leader><leader>f  :call <SID>ToggleFoldmethod()<cr>:set foldmethod?<cr>
nnoremap  <leader><leader>l  :set list!<cr>:set list?<cr>
nnoremap  <leader><leader>m  :call <SID>ToggleColorscheme()<cr>:colorscheme<cr>
nnoremap  <leader><leader>n  :set number!<cr>:set number?<cr>
nnoremap  <leader><leader>p  :set paste!<cr>:set paste?<cr>
nnoremap  <leader><leader>s  :set spell!<cr>:set spell?<cr>
nnoremap  <leader><leader>w  :set wrap!<cr>:set wrap?<cr>
nnoremap  <leader><leader>/  :set hlsearch!<cr>:set hlsearch?<cr>
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
cnoremap  <C-a>  <Home>
cnoremap  <C-e>  <End>
inoremap  <C-a>  <Home>
inoremap  <C-e>  <End>
xnoremap  <C-a>  <Home>
xnoremap  <C-e>  <End>
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
" quickfix/location functions {{{2
function s:NextQuickFixOrLocation()
	cnext
endfunction
function s:PrevQuickFixOrLocation()
	cprev
endfunction
" quickfix/location mappings {{{2
" TODO turn into autocmd that automatically maps to quickfix and location
" the event is QuickFixCmdPost
" check if location list is open with if get(getloclist(0, {'winid':0}), 'winid', 0)
nnoremap  <S-j>  :call <SID>NextQuickFixOrLocation()<cr>
nnoremap  <S-k>  :call <SID>PrevQuickFixOrLocation()<cr>
" disabled mappings {{{2
" disable arrow keys {{{3
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
" <C-D> to insert date {{{3
inoremap  <C-d>  <c-r>=strftime("%Y-%m-%d")<cr>
" default to very magic search {{{3
nnoremap  /      /\v
nnoremap  ?      ?\v
" easily search for selected text {{{3
xnoremap  /      y<Esc>/\V<C-r>"<cr>
xnoremap  ?      y<Esc>?\V<C-r>"<cr>
" rebind n/N to always go forwards/backwards (and turns on highlighting) {{{3
nnoremap  n      :set hlsearch<cr>/<cr>zz
nnoremap  <S-n>  :set hlsearch<cr>?<cr>zz
xnoremap  n      :set hlsearch<cr>/<cr>zz
xnoremap  <S-n>  :set hlsearch<cr>?<cr>zz
" force the use of the command line window {{{3
nnoremap  :      :<C-f>i
nnoremap  q:     :
xnoremap  :      :<C-f>i
xnoremap  q:     :
" editing functions {{{2
" format table {{{3
function s:FormatTable()
	:'<,'>s/\m\C  \+/	/eg
	:silent '<,'>!column -ts '	'
endfunction
" format columns {{{3
function s:FormatColumns()
	:'<,'>s/\m\C  \+/	/eg
endfunction
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
" miscellaneous editing mappings {{{3
nnoremap  <leader>a         ggVG
nnoremap  <leader>o         :!open<space>
nnoremap  <leader>p         "+p
nnoremap  <leader>y         "+y
xnoremap  <leader>y         "+y
nnoremap  <leader>z         1z=
nnoremap  <leader>/         :2match IncSearch ''<left>
nnoremap  <leader>@         :<C-f>ilet @=<C-r><C-r>
nnoremap  <leader>]         <C-w><C-]><C-w>T
xnoremap  <leader>]         <C-w><C-]><C-w>T
xnoremap  <leader><bar>     :<C-u>call <SID>FormatColumns()<cr>
xnoremap  <leader><bslash>  :<C-u>call <SID>FormatTable()<cr>
nnoremap  <leader><cr>      :make<cr>
xnoremap  <leader><cr>      y<Esc>:!<C-r>"<cr>
nnoremap  <leader>;         :lcd %:p:h<cr>
nnoremap  <silent>  <leader>.          :execute 'set foldenable foldlevel=' .. foldlevel('.')<cr>
if exists(':tnoremap')
	tnoremap  <Esc><Esc>  <C-\><C-n>
endif

" autocmds {{{1
" change grep {{{2
function s:AutosetGrepMappings()
	if &grepprg !~# '^grep -n '
		nnoremap  <buffer>  <leader>wfe  q:isilent grep<space>
		execute 'nnoremap  <buffer>  <leader>wfh  :leftabove vnew<cr>:setlocal filetype=' .. &filetype .. '<cr>q:isilent grep<space>'
		execute 'nnoremap  <buffer>  <leader>wfj  :rightbelow new<cr>:setlocal filetype=' .. &filetype .. '<cr>q:isilent grep<space>'
		execute 'nnoremap  <buffer>  <leader>wfk  :leftabove new<cr>:setlocal filetype=' .. &filetype .. '<cr>q:isilent grep<space>'
		execute 'nnoremap  <buffer>  <leader>wfl  :rightbelow vnew<cr>:setlocal filetype=' .. &filetype .. '<cr>q:isilent grep<space>'
		execute 'nnoremap  <buffer>  <leader>tf  :tabnew<cr>:setlocal filetype=' .. &filetype .. '<cr>q:isilent grep<space>'
		xnoremap  <buffer>  <leader>wfe  "zy:silent grep <C-r>z<cr>
		execute 'xnoremap  <buffer>  <leader>wfh  "zy:leftabove vnew<cr>:setlocal filetype=' .. &filetype .. '<cr>q:isilent grep <C-r>z<cr>'
		execute 'xnoremap  <buffer>  <leader>wfj  "zy:rightbelow new<cr>:setlocal filetype=' .. &filetype .. '<cr>q:isilent grep <C-r>z<cr>'
		execute 'xnoremap  <buffer>  <leader>wfk  "zy:leftabove new<cr>:setlocal filetype=' .. &filetype .. '<cr>q:isilent grep <C-r>z<cr>'
		execute 'xnoremap  <buffer>  <leader>wfl  "zy:rightbelow vnew<cr>:setlocal filetype=' .. &filetype .. '<cr>q:isilent grep <C-r>z<cr>'
		execute 'xnoremap  <buffer>  <leader>tf  "zy:tabnew<cr>:setlocal filetype=' .. &filetype .. '<cr>q:isilent grep <C-r>z<cr>'
	endif
endfunction
augroup justinnhli_autoset_grep_mappings
	autocmd  FileType  *  call <SID>AutosetGrepMappings()
augroup END
" create intermediate directories {{{2
function s:CreateIntermediateDirectories(file, buf)
	if empty(getbufvar(a:buf, '&buftype')) && a:file!~#'\v^\w+\:\/'
		let dir=fnamemodify(a:file, ':h')
		if !isdirectory(dir)
			call mkdir(dir, 'p')
		endif
	endif
endfunction
augroup justinnhli_create_directories
	autocmd  BufWritePre  *  :call <SID>CreateIntermediateDirectories(expand('<afile>'), +expand('<abuf>'))
augroup END
" load filetype templates {{{2
function s:LoadFiletypeTemplate()
	let l:templates_file = fnamemodify($MYVIMRC, ':p:h') .. '/templates/' .. &filetype
	if filereadable(l:templates_file)
		" read in the template file
		execute '0r ' .. l:templates_file
		" delete the blank last line
		execute "normal! :$\<cr>dd"
		" place cursor at first triple blank line,
		" or at the first line otherwise
		call cursor(0, 0)
		if search("\\n\\n\\n", 'c')
			normal! jj
		else
			normal! gg
		endif
	endif
endfunction
augroup justinnhli_create_directories
	autocmd  BufNewFile  *  call <SID>LoadFiletypeTemplate()
augroup END
" open directories in terminal {{{2
if exists(':terminal')
	function s:IsDir(dir) abort
		return !empty(a:dir) && isdirectory(a:dir)
	endfunction
	augroup justinnhli_open_directories
		autocmd  VimEnter  *  silent! autocmd! FileExplorer *
		autocmd  BufEnter  *  if s:IsDir(expand('%')) | call <SID>StartTerminal(['silent! lcd ' .. expand('%:p:h')], '') | endif
	augroup END
endif

" protect large files (>10M) from sourcing and other overhead.
function s:HandleLargeFiles()
	" define large as > 10MB
	let g:LargeFile = 1024 * 1024 * 10
	" set options:
	" eventignore+=FileType (no syntax highlighting etc.; assumes FileType always on)
	" noswapfile (save copy of file)
	" bufhidden=unload (save memory when other file is viewed)
	" undolevels=-1 (no undo possible)
	if getfsize(expand('<afile>')) > g:LargeFile
		set eventignore+=FileType
		setlocal noswapfile bufhidden=unload undolevels=-1
	else
		set eventignore-=FileType
	endif
endfunction

augroup justinnhli_large_files
	autocmd!
	autocmd  BufReadPre  *  call <SID>HandleLargeFiles()
augroup END

" user functions {{{1
" UnicodeToAscii {{{2
function UnicodeToAscii()
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
	%s/\%uFB00/ff/eg " ff
	%s/\%uFB01/fi/eg " fi
	%s/\%uFB02/fl/eg " fl
	%s/\%uFB03/ffi/eg " ffi
	" specials
	%s/\%uFFFC//eg " object replacement character
endfunction

" unclassified {{{1
" unclassified {{{2
augroup justinnhli
	" keep windows equal in size
	autocmd  VimResized          *       normal! <c-w>=
	" restore cursor position
	autocmd  BufReadPost         *       if line("'\"") > 1 && line("'\"") <= line('$') | execute 'normal! g`"' | endif
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
	autocmd  WinEnter            *       if winnr('$') == 1 && getbufvar(winbufnr(winnr()), '&buftype') == 'quickfix' | quit | endif
	" bound scope of search to the original window
	autocmd  WinLeave            *       let w:search_on = &hlsearch | let w:last_search = @/
	autocmd  WinEnter            *       if exists('w:search_on') && w:search_on | let @/ = w:last_search | else | set nohlsearch | endif
	" disable spellcheck in virtual terminal
	if exists('##TermOpen')
		autocmd  TermOpen        *       setlocal nonumber nospell scrollback=-1
		autocmd  TermClose       *       call feedkeys("i")
	endif
augroup END
