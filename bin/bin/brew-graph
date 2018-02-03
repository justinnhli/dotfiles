#!/bin/sh

echo "digraph {"
brew list | while read -r src; do
	echo "	\"$src\""
done
brew leaves | sed 's#.*/##' | while read -r src; do
	echo "	\"$src\" [style=filled, shape=box, fillcolor=\"#73D216\"]"
done
brew list | while read -r src; do
	brew uses --installed "$src" | while read -r dest; do
		echo "	\"$(echo "$src" | sed 's#.*/##')\" -> \"$(echo "$dest" | sed 's#.*/##')\""
	done
done
echo "}"
