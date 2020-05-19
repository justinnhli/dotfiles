set nocompatible " neovim default

let g:python3_host_prog = $PYTHON_VENV_HOME.'/neovim/bin/python3'

if has('nvim')
	"auto-install vim-plug
	let s:plug_path = fnamemodify($MYVIMRC, ':p:h') . '/autoload/plug.vim'
	if empty(glob(s:plug_path))
		execute "silent !curl -fLo " . s:plug_path . " --create-dirs 'https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim'"
		augroup justinnhli_vimplug
			autocmd!
			autocmd VimEnter * PlugInstall --sync | source $MYVIMRC
		augroup END
	endif

	try
		call plug#begin(expand('<sfile>:p:h').'/plugged')
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
		Plug 'raimon49/requirements.txt.vim'
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
			execute '0r '.l:templates_file
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
" }

" key mappings {
	mapclear
	mapclear!
	let g:mapleader = ' '
" }

" autocommands {
	augroup justinnhli
		" filetypes
		autocmd  BufNewFile          *       call <SID>LoadFileTypeTemplate()
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
" }
