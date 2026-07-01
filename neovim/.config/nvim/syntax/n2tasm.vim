
syntax keyword n2tKeyword MOV
syntax keyword n2tKeyword ADD SUB MUL DIV
syntax keyword n2tKeyword AND OR NOT
syntax keyword n2tKeyword JMP JEQ JNE JGT JGE JLT JLE
syntax keyword n2tKeyword PUS POP CAL RET
syntax keyword n2tKeyword HLT
highlight link n2tKeyword Keyword

syntax region n2tMemory start='\[' end='\]'
highlight link n2tMemory Special


syntax keyword n2tRegister R2 R02 R3 R03 R4 R04 R5 R05 R6 R06 R7 R07 R8 R08 R9 R09 R10 R11 R12 R13 R14 R15
highlight link n2tRegister Identifier


syntax match n2tNumber '\<[0-9]\+\>'
syntax match n2tNumber '\<0x[0-9A-F]\+\>'
highlight link n2tNumber Number

syntax match n2tLabel '@\@1<=\zsHLT\>'
syntax match n2tLabel '@\@1<=\zs[A-Z][A-Z_]*' 
syntax match n2tLabel '(\zs[A-Z][A-Z_]*\ze)' 
highlight link n2tLabel Label

