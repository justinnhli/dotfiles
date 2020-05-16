" <C-s> to write file
nnoremap  <C-s>  :update<cr>
inoremap  <C-s>  <esc>:update<cr>
xnoremap  <C-s>  <esc>:update<cr>gv

" default to very magic search
nnoremap  /      /\v
nnoremap  ?      ?\v

" easily search for selected text
xnoremap  /      y<Esc>/\V<C-r>"<cr>
xnoremap  ?      y<Esc>?\V<C-r>"<cr>

" rebind n/N to always go forwards/backwards (and turns on highlighting)
nnoremap  n      :set hlsearch<cr>/<cr>zz
nnoremap  <S-n>  :set hlsearch<cr>?<cr>zz
xnoremap  n      :set hlsearch<cr>/<cr>zz
xnoremap  <S-n>  :set hlsearch<cr>?<cr>zz

" force the use of the command line window
nnoremap  :      :<C-f>i
nnoremap  q:     :
xnoremap  :      :<C-f>i
xnoremap  q:     :

" Shift+JK for moving between quickfixes
nnoremap  <S-j>  :cnext<cr>
nnoremap  <S-k>  :cprevious<cr>
