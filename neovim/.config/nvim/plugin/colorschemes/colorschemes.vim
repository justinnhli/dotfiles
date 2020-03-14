let g:colorscheme = 'iceberg'
try
	execute 'colorscheme '.g:colorscheme
catch
	colorscheme default
endtry
