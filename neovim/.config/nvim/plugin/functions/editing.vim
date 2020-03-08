function UnicodeToAscii()
	set fileformat=unix
	" newline (0x13)
	%s///eg " newline
	%s/\%u2029//eg " paragraph separator
	" space (0x20)
	%s/\%u000B/ /eg " vertical tab
	%s/\%u00A0/ /eg " no-break space
	%s/\%u00AD/ /eg " soft hyphen
	%s/\%u2002/ /eg " en space
	%s/\%u2003/ /eg " em space
	%s/\%u200A/ /eg " hair space
	%s/\%u200B/ /eg " zero width space
	%s/\%u2028/ /eg " line separator
	" double quotes (0x22)
	%s/\%u2018\%u2018/"/eg " left single quotation mark
	%s/\%u2019\%u2019/"/eg " right single quotation mark
	%s/\%u201C/"/eg " left double quotation mark
	%s/\%u201D/"/eg " right double quotation mark
	" single quotes (0x27)
	%s/\%u2018/'/eg " left single quotation mark
	%s/\%u2019/'/eg " right single quotation mark
	%s/\%u2032/'/eg " prime
	" parentheses (0x28, 0x29)
	%s/\%uFD3E/(/eg " ornate left parenthesis
	%s/\%uFD3F/)/eg " ornate right parenthesis
	" asterisk  (0x2A)
	%s/\%u2022/* /eg " bullet
	" hyphen (0x2D)
	%s/\%u2010/ - /eg " hyphen
	%s/\%u2013/ - /eg " en dash
	%s/\%u2014/ - /eg " em dash
	%s/\%u2015/ - /eg " horizontal bar
	%s/\%u2500/ - /eg " box drawings light horizontal
	" ellipsis (0x2E)
	%s/\%u2026/.../eg " horizontal ellipsis
	" ligatures
	%s/\%uFB01/fi/eg " fi
	%s/\%uFB02/fl/eg " fl
	" specials
	%s/\%uFFFC//eg " object replacement character
endfunction
