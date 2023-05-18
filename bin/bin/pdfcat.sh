#!/bin/sh

usage() {
    echo "Usage: $(basename "$0") outputFile inputFile1[first,last] ..."
    exit "$1"
}

E_BADARGS=65

if [ $# -lt 2 ]; then
    usage $E_BADARGS
fi

outputFile=$1
shift 1
cmd="gs -q -sPAPERSIZE=letter -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -sOutputFile='$outputFile'"
for inputFile in "$@"; do
    pages="$(echo "$inputFile" | grep -o '\[[0-9]\+,[0-9]\+\]')"
    if [ "$pages" = '' ]; then
        cmd="$cmd '$inputFile'"
    else
        inputFile="$(echo "$inputFile" | sed 's/\[[0-9]*,[0-9]*\]$//')"
        first="$(echo "$pages" | grep -o '[0-9]\+,' | sed 's/,//')"
        last="$(echo "$pages" | grep -o ',[0-9]\+' | sed 's/,//')"
        cmd="$cmd -dFirstPage=$first -dLastPage=$last '$inputFile'"
    fi
done

echo "$cmd"
eval "$cmd"
