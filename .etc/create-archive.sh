#!/bin/bash

read -r -d '' paths <<EOF
/etc/fstab 
/etc/locale.conf
/etc/pacman.conf 
/etc/resolv.conf.head
/var/spool/cron/justinnhli
EOF

cd "$(dirname "${BASH_SOURCE[0]}")" || exit
find . -mindepth 1 -maxdepth 1 -type d -exec rm -rf '{}' ';'
echo "$paths" | while read -r path; do
	mkdir -p "$(dirname "$path" | sed 's#^/##')"
	cp "$path" "$(echo "$path" | sed 's#^/##')"
done
