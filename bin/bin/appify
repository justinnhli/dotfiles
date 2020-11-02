#!/bin/sh

# turn a shell script into a runnable MacOS app
# taken from https://mathiasbynens.be/notes/shell-script-mac-apps

APPNAME="${2:-$(basename "${1}" '.sh')}"
DIR="${APPNAME}.app/Contents/MacOS"

if [ -e "${APPNAME}.app" ]; then
	echo "${PWD}/${APPNAME}.app already exists :("
	exit 1
fi

mkdir -p "${DIR}"
cp "${1}" "${DIR}/${APPNAME}"
chmod +x "${DIR}/${APPNAME}"

echo "${PWD}/$APPNAME.app"
