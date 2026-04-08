syntax match hdlComment '//.*'
syntax region hdlComment start='/\*' end='*/'
highlight link hdlComment Comment

syntax keyword hdlKeyword CHIP IN OUT PARTS
highlight link hdlKeyword Keyword

syntax match hdlFunction '[A-Z][0-9A-Za-z]\+\ze('
highlight link hdlFunction Function

syntax match hdlIdentifier '\<[a-z]\+\ze='
highlight link hdlIdentifier Identifier

syntax match hdlConstant '\<[0-9]\+\>'
highlight link hdlConstant Constant

syntax keyword hdlTodo FIXME
highlight link hdlTodo Todo

