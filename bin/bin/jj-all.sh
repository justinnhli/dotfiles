#!/bin/bash

set -euo pipefail

find . -maxdepth 2 -name .jj | sort | while read -r dir; do
	dir="$(dirname "$dir")"
	(
		cd "$dir" >/dev/null 2>&1 || exit
		pwd
		jj "$@"
	)
	echo
done
