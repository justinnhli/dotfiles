
syntax match date '^[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}$'
highlight default link date Title

" highlight other people first
syntax match other '^\([^) ][^)]\{-\}[^:]\{-\}\)\?[[:alnum:])]:\( \|$\)'
highlight default link other Identifier

" overwrite that highlighting with myself
syntax match me '^\([^) ][^)]\{-\}[^:]\{-\}\)\?Justin (Ning Hui) Li \( (he/him)\)?:\( \|$\)'
syntax match me '^\([^) ][^)]\{-\}[^:]\{-\}\)\?Justin Li\( (he/him)\)\?:\( \|$\)'
syntax match me '^\([^) ][^)]\{-\}[^:]\{-\}\)\?Justin Ning Hui Li \( (he/him)\)?:\( \|$\)'
syntax match me '^\([^) ][^)]\{-\}[^:]\{-\}\)\?Justin \( (he/him)\)?:\( \|$\)'
syntax match me '^\([^) ][^)]\{-\}[^:]\{-\}\)\?\<[mM]e\>: \( \|$\)'
syntax match me '^\([^) ][^)]\{-\}[^:]\{-\}\)\?justinnhli \( (he/him)\)?:\( \|$\)'
syntax match me '^\([^) ][^)]\{-\}[^:]\{-\}\)\?justinnhli@chat.facebook.com[^:]\{-\} \( (he/him)\)?:\( \|$\)'
syntax match me '^\([^) ][^)]\{-\}[^:]\{-\}\)\?justinnhli@gmail.com/.\{-\} \( (he/him)\)?:\( \|$\)'
syntax match me '^\([^) ][^)]\{-\}[^:]\{-\}\)\?ninghui48@gmail.com \( (he/him)\)?:\( \|$\)'
syntax match me '^\([^) ][^)]\{-\}[^:]\{-\}\)\?ninghui96 \( (he/him)\)?:\( \|$\)'
highlight default link me Constant
