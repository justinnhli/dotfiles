function s:Tagnew(args)
	tabnew
	execute 'tag '.a:args
endfunction

function s:MoveToRelTab(n)
	let l:num_tabs = tabpagenr('$')
	let l:cur_tab = tabpagenr()
	let l:cur_win = winnr('#')
	let l:cur_buf = bufnr('%')
	let l:new_tab = a:n + l:cur_tab
	if a:n == 0 || (l:num_tabs == 1 && winnr('$') == 1)
		return
	endif
	if l:new_tab < 1
		executeute '0tabnew'
		let l:cur_tab += 1
	elseif l:new_tab > l:num_tabs
		execute 'tablast'
		execute 'tabnew'
	else
		if a:n < 0
			if l:num_tabs == tabpagenr('$')
				execute 'tabprev '.abs(a:n)
			elseif a:n != -1
				execute 'tabprev '.(abs(a:n)-1)
			endif
		else
			if l:num_tabs == tabpagenr('$')
				execute 'tabnext '.l:new_tab
			elseif a:n != 1
				execute 'tabnext '.(l:new_tab-1)
			endif
		endif
		vert botright split
	endif
	execute 'buffer '.l:cur_buf
	let l:new_tab = tabpagenr()
	execute 'tabnext '.l:cur_tab
	execute l:cur_win.'wincmd c'
	if l:new_tab > l:num_tabs
		execute 'tabnext '.(l:new_tab-1)
	else
		execute 'tabnext '.l:new_tab
	endif
	" FIXME fails when new_tab is the highest tab
endfunction

command! -nargs=1 Tagnew call <SID>Tagnew(<q-args>)
command! -nargs=1 MoveToRelTab call <SID>MoveToRelTab(<q-args>)
