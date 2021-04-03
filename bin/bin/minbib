#!/bin/sh

grep -o 'cite\([Ap]\)\?{[^}]*}' $@ | sed 's/.*{//; s/}//;' | grep -o '[^,]\+' | sed 's/^ *//; s/ *$//;' | sort -u | while read line; do
	sed -n "/{$line,/,/^$/p" ~/pim/library.bib
done
