
syntax match date '^[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}$'
highlight default link date Title

" highlight other people first
syntax match other '^\([^) ][^)]\{-\}[^:]\{-\}\)\?[[:alnum:])]:\( \|$\)'
highlight default link other Identifier

" overwrite that highlighting with myself
syntax match me '^\([^) ][^)]\{-\}[^:]\{-\}\)\?Justin (Ning Hui) Li:\( \|$\)'
syntax match me '^\([^) ][^)]\{-\}[^:]\{-\}\)\?Justin Li:\( \|$\)'
syntax match me '^\([^) ][^)]\{-\}[^:]\{-\}\)\?Justin Ning Hui Li:\( \|$\)'
syntax match me '^\([^) ][^)]\{-\}[^:]\{-\}\)\?Justin:\( \|$\)'
syntax match me '^\([^) ][^)]\{-\}[^:]\{-\}\)\?\<[mM]e\>: \( \|$\)'
syntax match me '^\([^) ][^)]\{-\}[^:]\{-\}\)\?justinnhli:\( \|$\)'
syntax match me '^\([^) ][^)]\{-\}[^:]\{-\}\)\?justinnhli@chat.facebook.com[^:]\{-\}:\( \|$\)'
syntax match me '^\([^) ][^)]\{-\}[^:]\{-\}\)\?justinnhli@gmail.com/.\{-\}:\( \|$\)'
syntax match me '^\([^) ][^)]\{-\}[^:]\{-\}\)\?ninghui48@gmail.com:\( \|$\)'
syntax match me '^\([^) ][^)]\{-\}[^:]\{-\}\)\?ninghui96:\( \|$\)'
highlight default link me Constant
