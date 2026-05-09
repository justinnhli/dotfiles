" this has to be in after/ftplugin to override the default gO mapping
nnoremap  <buffer>  gO  :lexpr system('grep -Hn "^#" ' .. shellescape(expand('%:p')))<cr>
