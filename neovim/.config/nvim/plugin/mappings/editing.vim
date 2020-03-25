" stay in visual mode after tabbing
vnoremap  <tab>          >gv
vnoremap  <S-tab>        <gv
vnoremap  >              >gv
vnoremap  <              <gv

" select previously pasted text
nnoremap  gp             `[v`]

" jump to the end of pasted text
nnoremap  p              p`]

" make Y behave like other capitals
nnoremap  Y              y$

" rebind undo/redo traverse the undo tree instead of the undo stack
nnoremap  u              g-
nnoremap  <C-r>          g+

" miscellaneous leader mappings
nnoremap  <leader>a         ggVG
nnoremap  <leader>f         q:ivimgrep //g **/*<esc>Fg<left>i
nnoremap  <leader>o         :!open<space>
nnoremap  <leader>p         "+p
nnoremap  <leader>y         "+y
vnoremap  <leader>y         "+y
nnoremap  <leader>z         1z=
nnoremap  <leader>/         :2match IncSearch ''<left>
nnoremap  <leader>@         :<C-f>ilet @=<C-r><C-r>
nnoremap  <leader>]         <C-w><C-]><C-w>T
vnoremap  <leader>]         <C-w><C-]><C-w>T
vnoremap  <leader><bar>     :s/  \+/      /eg<cr>gv
vnoremap  <leader><bslash>  :s/  \+/   /eg<cr>:'<,'>!column -ts '      '<cr>gv
nnoremap  <leader><cr>      :make<cr>
vnoremap  <leader><cr>      y<Esc>:!<C-r>"<cr>
nnoremap  <leader>;         :lcd %:p:h<cr>
