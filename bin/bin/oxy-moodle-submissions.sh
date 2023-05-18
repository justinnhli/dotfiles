#!/bin/bash

if [ $# -ne 2 ]; then
    echo "usage: $0 <zipfile> <dirname>"
    exit 1
fi

set -e

realpath() {
    # $1 : relative filename
    echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
}

# unzip into destination directory
zipfile="$(realpath "$1")"
dest="$(realpath "$2")"
mkdir -p "$dest"
cd "$dest"
unzip -q "$zipfile"

# rename the directories to be student names
find . -maxdepth 1 -type d -name '*_*' | while read -r f; do
    filename="$(basename "$f")"
    student="$(echo "$filename" | sed 's/_.*//; s/ /-/g;' | tr '[:upper:]' '[:lower:]')"
    mv "$filename" "$student"
done

# if every student submits a single file, get rid of the directories
if [ "$(find . -mindepth 2 -type f | wc -l)" -eq "$(find . -mindepth 1 -maxdepth 1 -type d | wc -l)" ]; then
    find . -mindepth 2 -type f | while read -r line; do
	student="$(echo "$line" | sed 's#^\./##; s#/.*##;')"
	ext="${line##*.}"
	new_file="$(echo "$student.$ext" | tr '[:upper:]' '[:lower:]')"
	mv "$line" "$new_file"
	rmdir "$student"
    done
fi

# list files and exit
find "$dest" -type f | sort
