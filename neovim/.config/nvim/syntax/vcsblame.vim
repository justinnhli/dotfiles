
syntax match commit '^[^ ]*'
highlight default link commit Title

syntax match date '[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\} [0-9]\{2\}:[0-9]\{2\}:[0-9]\{2\}$'
highlight default link date Identifier
