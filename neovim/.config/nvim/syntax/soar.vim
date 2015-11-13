setlocal iskeyword+=-
setlocal expandtab
setlocal spell

" syntax highlighting {
syn region smemAdd start="^smem --add {" end="^}" transparent fold contains=@ruleFrame,conditionAction,functionCall,comment

syn region productionRule matchgroup=ruleBraces start="^[gs]p {" end="^}" transparent fold contains=@ruleFrame,conditionAction,functionCall,comment

syn keyword flag FIXME TODO ERROR XXX contained
syn match flag "^    *("
syn match comment "#.*$" contains=flag,@Spell

syn region commentBlock start="^#.*\n#" end="^#.*\n\(#\)\@!" fold contains=flag,@Spell

syn match ruleName "{\@<=[[:alnum:]*_-]\+" contained
syn match ruleType " \@<=:\(o-support\|i-support\|chunk\|default\|monitor\|interrupt\|template\)[!-~]\@!" contained
syn match ruleDoc '"[^"]*"' contained
syn match ruleArrow "^-->$" contained
syn cluster ruleFrame contains=ruleName,ruleType,ruleDoc,ruleArrow

syn region conditionAction start="(\(state\)\@=" end=")" contains=@conditionActionParts keepend extend transparent
syn region conditionAction start="(\(<\)\@=" end=")" contains=@conditionActionParts keepend extend transparent
syn region conditionAction start="(\(\^\)\@=" end=")" contains=@conditionActionParts keepend extend transparent

syn region bindingTest start="{" end="}" contained contains=symbol,variable,binaryRelation transparent
syn region negGroup start="-{" end="}" contained contains=@conditionActionParts keepend extend transparent
syn region attributeTest matchgroup=attribute start="\^{" end="}" contained contains=@roles,binaryRelation transparent
syn match preferenceRelation "\(+\|-\|=\|>\|<\)" contained
syn match binaryRelation "\(<\|>\|=\|<>\)" contained
syn region disjunctionRelation matchgroup=disjunctBookends start="<<" end=">>" transparent contains=symbol,variable
syn cluster conditionActionParts contains=@roles,conditionAction,negGroup,bindingTest,attributeTest,disjunctionRelation,functionCall,preferenceRelation,comment,stateDeclaration

syn match attribute "[ (]\@<=-\?\^[^ {)]\+" contained contains=variable,disjunctionRelation
syn match symbol "[[:alnum:]]\@<![_[:alnum:]][[:alnum:]_-]*" contained
syn match symbol "|[^|]*|" contained contains=flag,@Spell
syn match variable "<[[:alnum:]-]\+>" contained
syn match stateDeclaration "(\@<=state" contained
syn cluster roles contains=attribute,symbol,variable

syn region functionCall start="(\(state\|<\)\@!" end=")" contains=@roles,functionInvocation,functionCall contained keepend extend transparent
syn match functionInvocation "(\@<=[a-z+*/-]" contains=functionName contained
syn keyword functionName abs atan2 cmd concat cos crlf div exec float halt ifeq int interrupt make-constant-symbol mod sqrt sin timestamp write contained
syn match functionName #+\|-\|*\|/# contained

hi def link ruleBraces Statement
hi def link ruleName Identifier
hi def link ruleType Statement
hi def link ruleDoc Comment
hi def link ruleArrow Statement
hi def link stateDeclaration Statement
hi def link attribute Type
hi def link binaryRelation Statement
hi def link preferenceRelation Statement
hi disjunctBookends ctermfg=LightGrey
hi def link symbol Constant
hi def link variable PreProc
hi def link functionName Statement
hi comment ctermfg=LightGrey
hi commentBlock ctermfg=LightGrey
"hi def link comment Comment
"hi def link commentBlock Comment
hi def link flag Error
" }

setlocal foldmethod=syntax
