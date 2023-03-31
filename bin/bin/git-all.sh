#!/bin/sh

find . -maxdepth 2 -name .git | sort | while read -r dir; do
	dir="$(dirname "$dir")"
	(
		cd "$dir" >/dev/null 2>&1
		pwd
		git "$@"
	)
	echo
done
