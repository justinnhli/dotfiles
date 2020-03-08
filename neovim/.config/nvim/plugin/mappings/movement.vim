function s:IndentTextObject(updown, inout, visual)
	if a:visual
		normal!gv
	endif
	let l:line_num = line('.')
	let l:step = (a:updown > 0 ? 1 : -1)
	let l:src_indent = indent(l:line_num)
	let l:dest_indent = l:src_indent + (a:inout * &tabstop)
	if dest_indent < 0
		let l:dest_indent = 0
	endif
	let l:cur_indent = indent(l:line_num)
	let l:line_num += l:step
	while 1 <= l:line_num && l:line_num <= line('$')
		let l:cur_indent = indent(l:line_num)
		if l:cur_indent < l:src_indent || l:cur_indent == l:dest_indent
			if a:visual && l:step == 1
				let l:line_num -= 1
			end
			call cursor(l:line_num, 0)
			return
		endif
		let l:line_num += l:step
	endwhile
endfunction

" bash/emacs home/end commands
nnoremap  <C-a>  ^
nnoremap  <C-e>  $
cnoremap  <C-a>  <Home>
cnoremap  <C-e>  <End>
inoremap  <C-a>  <Home>
inoremap  <C-e>  <End>
vnoremap  <C-a>  <Home>
vnoremap  <C-e>  <End>

" jump to previous/next line with less/same/more indentation
nnoremap  <silent>  [,  :<C-u>call <SID>IndentTextObject(-1, -1, 0)<cr>
nnoremap  <silent>  [.  :<C-u>call <SID>IndentTextObject(-1, 0, 0)<cr>
nnoremap  <silent>  [/  :<C-u>call <SID>IndentTextObject(-1, 1, 0)<cr>
nnoremap  <silent>  ],  :<C-u>call <SID>IndentTextObject(1, -1, 0)<cr>
nnoremap  <silent>  ].  :<C-u>call <SID>IndentTextObject(1, 0, 0)<cr>
nnoremap  <silent>  ]/  :<C-u>call <SID>IndentTextObject(1, 1, 0)<cr>
onoremap  <silent>  [,  :<C-u>call <SID>IndentTextObject(-1, -1, 0)<cr>
onoremap  <silent>  [.  :<C-u>call <SID>IndentTextObject(-1, 0, 0)<cr>
onoremap  <silent>  [/  :<C-u>call <SID>IndentTextObject(-1, 1, 0)<cr>
onoremap  <silent>  ],  :<C-u>call <SID>IndentTextObject(1, -1, 0)<cr>
onoremap  <silent>  ].  :<C-u>call <SID>IndentTextObject(1, 0, 0)<cr>
onoremap  <silent>  ]/  :<C-u>call <SID>IndentTextObject(1, 1, 0)<cr>
vnoremap  <silent>  [,  <esc>:call <SID>IndentTextObject(-1, -1, 1)<cr><esc>gv
vnoremap  <silent>  [.  <esc>:call <SID>IndentTextObject(-1, 0, 1)<cr><esc>gv
vnoremap  <silent>  [/  <esc>:call <SID>IndentTextObject(-1, 1, 1)<cr><esc>gv
vnoremap  <silent>  ],  <esc>:call <SID>IndentTextObject(1, -1, 1)<cr><esc>gv
vnoremap  <silent>  ].  <esc>:call <SID>IndentTextObject(1, 0, 1)<cr><esc>gv
vnoremap  <silent>  ]/  <esc>:call <SID>IndentTextObject(1, 0, 1)<cr><esc>gv
