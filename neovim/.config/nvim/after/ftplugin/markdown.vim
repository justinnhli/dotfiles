nnoremap  <buffer>  gO  :lexpr system('grep -Hn "^#" ' . shellescape(expand('%:p')))<cr>
