syntax match n2tComment '//.*'
syntax region n2tComment start='/\*' end='*/'
highlight link n2tComment Comment

syntax match n2tFunction ';\zsJMP'
syntax match n2tFunction ';\zsJEQ'
syntax match n2tFunction ';\zsJNE'
syntax match n2tFunction ';\zsJLT'
syntax match n2tFunction ';\zsJLE'
syntax match n2tFunction ';\zsJGT'
syntax match n2tFunction ';\zsJGE'
highlight link n2tFunction Function

syntax match n2tLabel '@\@1<=\zsHLT\>'
syntax match n2tLabel '@\@1<=\zs[A-Z][A-Z_]*' 
syntax match n2tLabel '(\zs[A-Z][A-Z_]*\ze)' 
highlight link n2tLabel Label

syntax match n2tKeyword '@\@1<=\zsR0\?[1-9]\>'
syntax match n2tKeyword '@\@1<=\zsR1[0-5]\>'
syntax match n2tKeyword '@\@1<=\zsKBD\>'
syntax match n2tKeyword '@\@1<=\zsSCREEN\>'
highlight link n2tKeyword Keyword

syntax match n2tNumber '@\@1<=-\?\<[0-9]\+\>'
syntax match n2tNumber '@\@1<=0b[0-9]\+\>'
syntax match n2tNumber '\<0x[0-9A-F]\+\>'
highlight link n2tNumber Number

syntax keyword n2tTodo FIXME
highlight link n2tTodo Todo
