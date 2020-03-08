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

" key mappings {
	mapclear
	mapclear!
	let g:mapleader = ' '

	" disable the default leader
	nnoremap \ <nop>

	" buffer management {
		nnoremap  <leader>e    :e<space>
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
	" netrw
	let g:netrw_browse_split = 3
	let g:netrw_liststyle = 3
	let g:netrw_list_hide = '\.swp$,\.un\~$'
	let g:netrw_winsize = 50
	" undotree
	nnoremap  <leader><leader>u     :UndotreeToggle<cr>
" }
