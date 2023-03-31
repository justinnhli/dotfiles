#!/bin/sh

E_BADARGS=65

if [ $# -ne 3 ]; then
    echo "Usage: $(basename $0) VIDEO_FILE SECONDS IMAGE_FILE"
    exit $E_BADARGS
fi

ffmpeg -i "$1" -ss "$2" -vcodec png -vframes 1 -f rawvideo "$3"
