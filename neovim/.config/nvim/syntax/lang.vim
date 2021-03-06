syntax keyword literal true false
syntax match literal '\<[0-9]\+\>'
syntax match literal '"[^"]*"'
highlight default link literal Number

syntax keyword keyword if else while ret print
syntax keyword keyword var int func class obj nextgroup=name,upper skipwhite
highlight default link keyword Keyword

syntax match comment '#.*' contains=fixme
highlight default link comment Comment

syntax keyword fixme TODO FIXME contained
highlight default link fixme Todo

syntax match name '\h\w*' contained
highlight default link name Title

syntax match upper '\h\u\+\w*\h'
highlight default link upper Special

syntax spell notoplevel
