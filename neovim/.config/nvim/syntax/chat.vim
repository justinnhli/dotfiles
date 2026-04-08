
syntax match date '^[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}$'
highlight default link date Title

" highlight other people first
syntax match other '^\s*\([^) ][^)]\{-\}[^:]\{-\}\)\?[[:alnum:])]:\( \|$\)'
highlight default link other Identifier

" overwrite that highlighting with myself
syntax match me '^\s*\([^) ][^)]\{-\}[^:]\{-\}\)\?\<[Mm]e\>: \( \|$\)'
syntax match me '^\s*\([^) ][^)]\{-\}[^:]\{-\}\)\?Justin\( (\?Ning Hui)\?\)\?\( Li\)\?\( (he/him)\)\?:\( \|$\)'
syntax match me '^\s*\([^) ][^)]\{-\}[^:]\{-\}\)\?justinnhli\(@[a-z.]*\)\?\( (he/him)\)\?:\( \|$\)'
syntax match me '^\s*\([^) ][^)]\{-\}[^:]\{-\}\)\?ninghui48@gmail.com\( (he/him)\)\?:\( \|$\)'
syntax match me '^\s*\([^) ][^)]\{-\}[^:]\{-\}\)\?ninghui96\( (he/him)\)\?:\( \|$\)'
highlight default link me Constant
