#!/bin/sh

grep -o 'cite\([Ap]\)\?{[^}]*}' "$@" | sed 's/.*{//; s/}//;' | grep -o '[^,]\+' | sed 's/^ *//; s/ *$//;' | sort -u | while read -r line; do
	sed -n "/{$line,/,/^$/p" ~/Dropbox/pim/library.bib
done
