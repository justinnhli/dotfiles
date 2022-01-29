#!/bin/bash

set -euo pipefail

source ~/.bashrc && cd ~/archive/ && workon archivebox && archivebox add "$@"
