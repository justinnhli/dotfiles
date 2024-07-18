#!/bin/bash

set -euo pipefail

if ! ollama ps >/dev/null 2>&1; then
	ollama serve >/dev/null 2>&1 &
	sleep 3
fi
ollama run phi3 "$@"
