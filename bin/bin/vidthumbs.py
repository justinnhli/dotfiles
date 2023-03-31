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


def image_path(video_path):
    # type: (Path) -> Path
    """Create the thumbnail image filepath.

    Parameters:
        video_path (Path): The path of the video file.

    Returns:
        Path: The path of the thumbnail image file.
    """
    return video_path.parent.joinpath(video_path.stem + '.png')


def create_thumbnail_grid(path, scale=120):
    # type: (Path, int) -> None
    """Create a thumbnail grid of a video.

    Parameters:
        path (Path): The path of the video file.
        scale (int): The scale of the images.
    """
    length = video_length(path)
    frequency = int(length) // 16
    run(
        [
            'ffmpeg',
            '-i', str(path),
            '-loglevel', 'error',
            '-vf', f'fps=1/{frequency},scale=-1:{scale},tile=4x4',
            str(image_path(path)),
        ],
        check=False,
    )


def main():
    # type: () -> None
    """Provide a CLI entry point."""
    arg_parser = ArgumentParser(description='create a thumbnail grid of videos')
    arg_parser.add_argument('paths', metavar='path', type=Path, nargs='+', help='video file(s) to process')
    arg_parser.add_argument('--overwrite', action='store_true', help='regenerate thumbnails')
    arg_parser.add_argument('--scale', type=int, default=120, help='thumbnail scale (default:120)')
    args = arg_parser.parse_args()
    to_process = set()
    for path in args.paths:
        path = path.expanduser().resolve()
        if not path.exists():
            continue
        if path in to_process:
            continue
        if image_path(path).exists() and not args.overwrite:
            continue
        to_process.add(path)
    for i, path in enumerate(sorted(to_process), start=1):
        print(f'({i}/{len(to_process)}) {path}')
        create_thumbnail_grid(path, scale=args.scale)


if __name__ == '__main__':
    main()
