let g:colorscheme = 'iceberg'
try
	exec 'colorscheme '.g:colorscheme
catch
	colorscheme default
endtry
