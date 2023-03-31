#!/usr/bin/env python3
"""OCR images using (py)tesseract."""

from argparse import ArgumentParser
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory

try:
    import pytesseract
    from PIL import Image
except (ModuleNotFoundError, ImportError) as err:

    def run_with_venv(venv):
        # type: (str) -> None
        """Run this script in a virtual environment.

        Parameters:
            venv (str): The virtual environment to use.

        Raises:
            FileNotFoundError: If the virtual environment does not exist.
            ImportError: If the virtual environment does not contain the necessary packages.
        """
        # pylint: disable = ungrouped-imports, reimported, redefined-outer-name, import-outside-toplevel
        import sys
        from os import environ, execv
        from pathlib import Path
        venv_python = Path(environ['PYTHON_VENV_HOME'], venv, 'bin', 'python3').expanduser()
        if not venv_python.exists():
            raise FileNotFoundError(f'could not find venv "{venv}" at executable {venv_python}')
        if sys.executable == str(venv_python):
            raise ImportError(f'no module {err.name} in venv "{venv}" ({venv_python})')
        execv(str(venv_python), [str(venv_python), *sys.argv])

    run_with_venv('pdfocr')


def ocr_directory(path, lang='eng', verbose=False):
    # type: (Path, str, bool) -> str
    """Convert a directory of images to text."""
    suffixes = ['png', 'jpg', 'jpeg', 'gif', 'tiff']
    image_paths = [] # type: list[Path]
    for suffix in suffixes:
        image_paths.extend(path.glob(f'*.{suffix}'))
    image_paths = sorted(image_paths)
    result = []
    for index, image_path in enumerate(image_paths, start=1):
        if verbose:
            print(f'processing page {index} of {len(image_paths)}')
        result.append(ocr_image_file(image_path, lang=lang, verbose=verbose))
    return '\n'.join(result)


def ocr_image_file(path, lang='eng', verbose=False):
    # type: (Path, str, bool) -> str
    """Convert an image to text."""
    if verbose:
        print(f'tesseract {path}')
    return pytesseract.image_to_string(Image.open(str(path)), lang=lang)


def ocr_pdf_file(path, lang='eng', verbose=False):
    # type: (Path, str, bool) -> str
    """Convert an PDF file to text."""
    with TemporaryDirectory() as temp_dir:
        cmd = [
            'gs',
            '-q',
            '-dQUIET',
            '-dPARANOIDSAFER',
            '-dBATCH',
            '-dNOPAUSE',
            '-dNOPROMPT',
            '-sDEVICE=png16m',
            '-dTextAlphaBits=4',
            '-dGraphicsAlphaBits=4',
            '-r300x300',
            '-sOutputFile="page%03d.png"',
            str(path),
        ]
        if verbose:
            print(' '.join(cmd))
        run(
            cmd,
            cwd=temp_dir,
            check=True,
        )
        return ocr_directory(Path(temp_dir), lang=lang, verbose=verbose)


def ocr(path, lang='eng', verbose=False):
    # type: (Path, str, bool) -> None
    """Print the detected text from an image."""
    if path.is_dir():
        print(ocr_directory(path, lang, verbose))
    elif path.suffix == '.pdf':
        print(ocr_pdf_file(path, lang, verbose))
    else:
        print(ocr_image_file(path, lang, verbose))


def main():
    # type: () -> None
    """Provide a CLI entry point."""
    arg_parser = ArgumentParser()
    arg_parser.add_argument('paths', nargs='+', type=Path, help='file or directory to convert')
    arg_parser.add_argument('--lang', default='eng', help='language of the file (default=eng)')
    args = arg_parser.parse_args()
    supported_languages = pytesseract.get_languages()
    if args.lang not in supported_languages:
        arg_parser.error(' '.join([
            f'unrecognized language "{args.lang}".',
            f'Supported languages: {", ".join(supported_languages)}',
        ]))
    for path in args.paths:
        ocr(path.expanduser().resolve(), lang=args.lang, verbose=True)


if __name__ == '__main__':
    main()
