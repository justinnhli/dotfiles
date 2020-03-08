" <C-s> to write file
nnoremap <C-s> :update<cr>
inoremap <C-s> <esc>:update<cr>
vnoremap <C-s> <esc>:update<cr>gv

" stay in visual mode after tabbing
vnoremap  <tab>    >gv
vnoremap  <S-tab>  <gv
vnoremap  >        >gv
vnoremap  <        <gv

" select previously pasted text
nnoremap  gp       `[v`]

" jump to the end of pasted text
nnoremap  p        p`]

" make Y behave like other capitals
nnoremap  Y        y$

" rebind undo/redo traverse the undo tree instead of the undo stack
nnoremap  u        g-
nnoremap  <C-r>    g+
