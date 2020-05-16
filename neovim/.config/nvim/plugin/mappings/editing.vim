" stay in visual mode after tabbing
xnoremap  <tab>          >gv
xnoremap  <S-tab>        <gv
xnoremap  >              >gv
xnoremap  <              <gv

" select previously pasted text
nnoremap  gp             `[v`]

" jump to the end of pasted text
nnoremap  p              p`]

" make Y behave like other capitals
nnoremap  Y              y$

" rebind undo/redo traverse the undo tree instead of the undo stack
nnoremap  u              g-
nnoremap  <C-r>          g+


function! s:FormatTable()
	:'<,'>s/  \+/	/eg
	:silent '<,'>!column -ts '	'
endfunction

function! s:FormatColumns()
	:'<,'>s/  \+/	/eg
endfunction


" miscellaneous leader mappings
nnoremap  <leader>a         ggVG
nnoremap  <leader>f         q:ivimgrep //g **/*<esc>Fg<left>i
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
