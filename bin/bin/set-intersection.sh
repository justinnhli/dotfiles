#!/bin/sh

sort "$@" | uniq -c | grep "^ *$# " | sed 's/^ *[0-9]* *//;' | sort
