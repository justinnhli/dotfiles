function BuildTabLine()
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

function GetGitBranch()
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
