syntax match n2tComment '//.*'
syntax region n2tComment start='/\*' end='*/'
highlight link n2tComment Comment

syntax keyword n2tKeyword CHIP IN OUT PARTS
highlight link n2tKeyword Keyword

syntax match n2tFunction '[A-Z][0-9A-Za-z]\+\ze('
highlight link n2tFunction Function

syntax match n2tIdentifier '\<[a-z]\+\ze='
highlight link n2tIdentifier Identifier

syntax match n2tNumber '-\?\<[0-9]\+\>'
syntax match n2tNumber '\<0b[0-9]\+\>'
syntax match n2tNumber '\<0x[0-9A-F]\+\>'
highlight link n2tNumber Constant

syntax keyword n2tTodo FIXME
highlight link n2tTodo Todo
