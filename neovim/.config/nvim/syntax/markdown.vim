syntax keyword markdownFixme FIXME TODO
syntax match markdownFixme '(FIXME\>[^()]*)' " parenthesized FIXMEs
syntax match markdownFixme '\[FIXME\>[^]]*\]' " bracketed FIXMEs with notes
highlight link markdownFixme Todo
