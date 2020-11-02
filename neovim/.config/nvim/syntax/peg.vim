syntax match comment '#.*'
highlight default link nonterminal Comment

syntax match nonterminal '^[a-z_]\+'
highlight default link nonterminal Statement

syntax match constant '[A-Z]\+'
highlight default link constant Constant

syntax match string '"[^"]*"'
syntax match string "'[^']*'"
highlight default link string String

syntax match punctuation '[|=;*+?&!()]'
highlight default link punctuation Special
