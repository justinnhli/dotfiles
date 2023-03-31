#!/bin/sh

current="$(sort "$1")"
shift 1
for f in "$@"; do
	subtract="$(sort "$f")"
	current="$( ( echo "$current" && echo "$subtract" && echo "$subtract" ) | sort | uniq -u)"
done
echo "$current"
