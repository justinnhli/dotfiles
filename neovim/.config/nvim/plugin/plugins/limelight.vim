function! s:EnterLimelight()
	if &filetype ==# 'journal'
		let g:limelight_bop = '^.'
		let g:limelight_eop = '\ze\n'
	endif
	Limelight
endfunction

function! s:LeaveLimelight()
	if &filetype ==# 'journal'
		if exists('g:limelight_bop')
			unlet g:limelight_bop
		endif
		if exists('g:limelight_eop')
			unlet g:limelight_eop
		endif
	endif
	Limelight!
endfunction

augroup justinnhli_limelight
	autocmd!
	autocmd User GoyoEnter call <SID>EnterLimelight()
	autocmd User GoyoLeave call <SID>LeaveLimelight()
augroup END
