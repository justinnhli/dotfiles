syntax keyword n2tKeyword struct function if while let call return
highlight link n2tKeyword Keyword

syntax keyword n2tSpecial _add _sub _mul _div
syntax keyword n2tSpecial _and _or _not
syntax keyword n2tSpecial _eq _ne _gt _ge _lt _le
syntax keyword n2tSpecial _get_index _set_index
syntax keyword n2tSpecial _get_member _set_member
syntax keyword n2tSpecial _malloc _free
syntax keyword n2tSpecial _addr_of _deref 
highlight link n2tSpecial Special

syntax match n2tFunction '\<[^_][0-9A-Za-z_]*\ze('
highlight link n2tFunction Function

syntax match n2tNumber '\<[0-9]\+\>'
syntax match n2tNumber '\<0x[0-9A-F]\+\>'
highlight link n2tNumber Number

syntax match n2tComment '//.*'
syntax region n2tComment start='/\*' end='*/'
highlight link n2tComment Comment
