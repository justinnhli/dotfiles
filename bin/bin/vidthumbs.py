#!/usr/bin/env python3

"""A script to create a thumbnail grid for a video."""

from argparse import ArgumentParser
from pathlib import Path
from subprocess import run


def video_length(path):
    # type: (Path) -> float
    """Determine the length of the video, in seconds.

    Parameters:
        path (Path): The path of the video file.

    Returns:
        float: The length of the video, in seconds

    Raises:
        ValueError: If the output of ffprobe fails to parse.
    """
    process = run(['ffprobe', str(path), '-show_format', '-v', 'quiet'], capture_output=True, check=True)
    for line in process.stdout.decode('utf-8').splitlines():
        if line.startswith('duration'):
            return float(line.split('=')[1])
    raise ValueError()


def create_thumbnail_grid(path, overwrite=False):
    # type: (Path, bool) -> None
    """Create a thumbnail grid of a video.

    Parameters:
        path (Path): The path of the video file.
        overwrite (bool): Whether to overwrite an existing image.
            Defaults to False.
    """
    length = video_length(path)
    frequency = int(length) // 16
    img_path = path.parent.joinpath(path.stem + '.png')
    if img_path.exists() and not overwrite:
        return
    run(
        [
            'ffmpeg',
            '-i', str(path),
            '-vf', f'fps=1/{frequency},scale=-1:120,tile=4x4',
            str(img_path),
        ],
        check=False,
    )


def main():
    # type: () -> None
    """Provide a CLI entry point."""
    arg_parser = ArgumentParser(description='create a thumbnail grid of videos')
    arg_parser.add_argument('paths', type=Path, nargs='+', help='video file(s) to process')
    arg_parser.add_argument('--overwrite', action='store_true', help='regenerate thumbnails')
    args = arg_parser.parse_args()
    processed = set()
    for path in args.paths:
        path = path.expanduser().resolve()
        if path in processed:
            continue
        processed.add(path)
        create_thumbnail_grid(path, overwrite=args.overwrite)


if __name__ == '__main__':
    main()
