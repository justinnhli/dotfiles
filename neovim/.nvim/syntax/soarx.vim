setlocal iskeyword+=-
setlocal expandtab

" syntax highlighting {

syn keyword flag FIXME TODO ERROR XXX contained
syn match comment "#.*$" contains=flag,@Spell
syn region commentBlock start="^#.*\n#" end="^#.*\n\(#\)\@!" fold contains=flag,@Spell

syn region rule matchgroup=rule start="^[gs]p {" end="}" fold contains=ruleName,ruleDoc
syn match ruleName "{\@<=[[:alnum:]*_-]\+" contained skipwhite skipnl nextgroup=ruleType,ruleDoc,condact
syn match ruleType ":\(o-support\|i-support\|chunk\|default\|monitor\|interrupt\|template\)" contained skipwhite skipnl nextgroup=condact
syn match ruleDoc '"[^"]*"' contained skipwhite skipnl nextgroup=condact

syn region condact matchgroup=plain start="(\(state\|\^\|<\)\@=" end=")" contained keepend extend transparent skipwhite skipnl nextgroup=condact,condactGroup,ruleArrow contains=state,variable,attribute,symbol
syn region condactGroup matchgroup=plain start="-\?{" end="}" contained keepend extend transparent skipwhite skipnl nextgroup=condact,condactGroup contains=condact
syn match ruleArrow "-->" contained skipwhite skipnl nextgroup=condact,condactGroup

syn match attribute "-\?\^[^ {)]\+" contained skipwhite skipnl nextgroup=variable,symbol contains=disjunction,tests,variable
syn match variable "<[[:alnum:]-]\+>" contained
syn match symbol "[[:alnum:]][[:alnum:]_-]*" contained
syn match symbol "|[^|]*|" contained

syn region disjunction matchgroup=disjunction start="<<" end=">>" contained contains=symbol
syn region tests matchgroup=tests start="{" end="}" contained contains=relation,variable,symbol

" state must be defined after symbols
syn match state "state" contained

hi def link rule Statement
hi def link ruleArrow Statement
hi def link ruleName Identifier
hi def link ruleType Special
hi def link ruleDoc Special

hi def link condact Type
hi def link state Statement

hi def link attribute Type
hi def link symbol Constant
hi def link variable PreProc

hi def link disjunction Error
hi def link tests Error

hi def link flag Error
hi def link plain Normal
" }

setlocal foldmethod=syntax
