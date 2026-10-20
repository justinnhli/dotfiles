syntax match n2tComment '//.*'
highlight link n2tComment Comment

syntax keyword n2tKeyword MOV
syntax keyword n2tKeyword ADD SUB
syntax keyword n2tKeyword AND OR NOT
syntax keyword n2tKeyword JMP JEQ JNE JGT JGE JLT JLE
syntax keyword n2tKeyword PUSH POP CALL RET
syntax keyword n2tKeyword HLT
highlight link n2tKeyword Keyword

syntax region n2tMemory start='\[' end='\]' contains=n2tRegister
highlight link n2tMemory Special

syntax keyword n2tRegister FP SP
syntax keyword n2tRegister R2 R02
syntax keyword n2tRegister R3 R03
syntax keyword n2tRegister R4 R04
syntax keyword n2tRegister R5 R05
syntax keyword n2tRegister R6 R06
syntax keyword n2tRegister R7 R07
syntax keyword n2tRegister R8 R08
syntax keyword n2tRegister R9 R09
syntax keyword n2tRegister R10 R11 R12 R13 R14 R15
highlight link n2tRegister Identifier

syntax match n2tNumber '\<[0-9]\+\>'
syntax match n2tNumber '\<0x[0-9A-F]\+\>'
highlight link n2tNumber Number

syntax match n2tLabel '(\zs[A-Z][[0-9A-Z_]*\ze)' 
highlight link n2tLabel Label

