syntax match nonterminal '^[a-z_]\+'
highlight default link nonterminal Statement

syntax match comment '#.*' contains=fixme
highlight default link nonterminal Comment

syntax keyword fixme TODO FIXME contained
highlight default link fixme Todo

syntax match constant '[A-Z]\+'
highlight default link constant Constant

syntax match string '"[^"]*"'
syntax match string "'[^']*'"
highlight default link string String

syntax match punctuation '[|=;*+?&!()]'
highlight default link punctuation Special
