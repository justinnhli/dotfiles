#!/bin/bash

PACKAGES_PATH="$HOME/git/dotfiles/packages/.local/share/packages/"

case "$1" in
"brew")
	if which brew >/dev/null 2>&1; then
		comm \
			"$PACKAGES_PATH/brew" \
			<(set-difference.sh <(brew leaves) <(brew list --cask))
	else
		echo "cannot find \`brew\` command"
		exit 1
	fi;;
"brew-cask")
	if which brew >/dev/null 2>&1; then
		comm \
			"$PACKAGES_PATH/brew-cask" \
			<(brew list --cask)
	else
		echo "cannot find \`brew\` command"
		exit 1
	fi;;
"brew-taps")
	if which brew >/dev/null 2>&1; then
		comm \
			"$PACKAGES_PATH/brew-tap" \
			<(brew tap)
	else
		echo "cannot find \`brew\` command"
		exit 1
	fi;;
"npm")
	if which npm >/dev/null 2>&1; then
		comm \
			"$PACKAGES_PATH/npm" \
			<(npm list --global --parseable --depth=0 | grep node_modules | while read -r module; do basename "$module"; done | sort | uniq)
	else
		echo "cannot find \`npm\` command"
		exit 1
	fi;;
"pikaur")
	if which pikaur >/dev/null 2>&1; then
		comm \
			"$PACKAGES_PATH/pikaur" \
			<(pacman -Qemq)
	else
		echo "cannot find \`pikaur\` command"
		exit 1
	fi;;
"pacman")
	if which pacman >/dev/null 2>&1; then
		comm \
			<(sort "$PACKAGES_PATH/pacman") \
			<( \
				( \
					set-difference.sh <(pacman -Qenq) <( (pacman -Qgq base-devel texlive-most && pacman -Slq core ) | sort | uniq) && \
					echo base-devel && \
					echo texlive-most \
				) | sort
			)
	else
		echo "cannot find \`pacman\` command"
		exit 1
	fi;;
"pip")
	comm \
		"$PACKAGES_PATH/pip" \
		<(python3 -m pip list --not-required --format=freeze | sed 's/=.*//' | sort);;

*)
	echo "$(basename "$0")" "$(grep '^"[a-z-]*")$' "$0" | sort | sed 's/^"\(.*\)")/\1/' | tr '\n' '|' | sed 's/|$//')";;
esac
