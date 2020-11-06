syntax keyword literal true false
syntax match literal '\<[0-9]\+\>'
syntax match literal '"[^"]*"'
highlight default link literal Number

syntax keyword keyword var class func if while ret print str int bool true false
highlight default link keyword Keyword

syntax match comment '#.*'
highlight default link comment Comment
