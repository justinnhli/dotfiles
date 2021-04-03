#!/usr/bin/env python3

"""A CLI version of Dave Seah's Compact Calendar."""

from calendar import monthrange
from datetime import date, datetime, timedelta
from argparse import ArgumentParser, ArgumentTypeError

ONE_DAY = timedelta(days=1)


def str_to_date(string, start=True):
    """Parse an ISO-like string to a datetime.date object.

    Arguments:
        string (str): The string.
        start (bool): Whether to return the start or end of the period.
            Defaults to True.

    Returns:
        date: The date described by the string

    Raises:
        ArgumentTypeError: If the string is not in YYYY[-MM[-DD]] format
    """
    try:
        if len(string) == 4:
            result = datetime.strptime(string, '%Y').date()
            if not start:
                result = result.replace(month=12, day=31)
            return result
        if len(string) == 7:
            result = datetime.strptime(string, '%Y-%m').date()
            if not start:
                result = result.replace(
                    day=monthrange(result.year, result.month)[1]
                )
            return result
        if len(string) == 10:
            return datetime.strptime(string, '%Y-%m-%d').date()
        raise ArgumentTypeError(
            f'argument "{string}" should be in format YYYY[-MM[-DD]]'
        )
    except ValueError as err:
        raise ArgumentTypeError from err


def parse_args(args):
    """Parse the start and end date CLI arguments to datetime.date objects.

    Arguments:
        args (Namespace): The command line arguments.

    Returns:
        Tuple[date, date, date]: The start date, end date, and marker date.

    Raises:
        ArgumentTypeError: If the end date is earlier than the start date.
    """
    start, end = args.start, args.end
    today = date.today()
    if args.no_marker:
        mark_date = None
    else:
        mark_date = today
    if end is None:
        if start is None:
            start_date = today - 28 * ONE_DAY
            end_date = today + 28 * ONE_DAY
        elif len(start) == 10:
            anchor = str_to_date(start)
            end_date = anchor + 28 * ONE_DAY
            start_date = anchor - 28 * ONE_DAY
            mark_date = anchor
        else:
            start_date = str_to_date(start)
            end_date = str_to_date(start, start=False)
    else:
        start_date = str_to_date(start, start=True)
        end_date = str_to_date(end, start=False)
    if end_date < start_date:
        raise ArgumentTypeError(' '.join([
            f'start date must be before end date,',
            f'but got {start_date} and {end_date}',
        ]))
    return start_date, end_date, mark_date


def print_calendar(start_date, end_date, mark_date=None):
    """Print a compact calendar.

    Arguments:
        start_date (date): The start date.
        end_date (date): The end date.
        mark_date (date): The date to mark. Defaults to None.
    """
    curr_date = start_date - ((start_date.weekday() + 1) % 7) * ONE_DAY
    print(' Su Mo Tu We Th Fr Sa')
    while curr_date <= end_date:
        output = ' '.join(
            f'{(curr_date + (i * ONE_DAY)).day: >2d}'
            for i in range(7)
        )
        output = f' {output} '
        if mark_date and 0 <= (mark_date - curr_date).days <= 7:
            output = output.replace(f' {mark_date.day: >2d} ', f'[{mark_date.day: >2d}]')
        curr_date += 7 * ONE_DAY
        if (curr_date - start_date).days <= 7 or curr_date.day <= 7:
            output += curr_date.strftime('%b %Y')
        print(output)


def main():
    """Run the CLI program."""
    arg_parser = ArgumentParser()
    arg_parser.add_argument('start', nargs='?', help='start date')
    arg_parser.add_argument('end', nargs='?', help='end date')
    arg_parser.add_argument('--no-marker', action='store_true', help='hide today marker')
    args = arg_parser.parse_args()
    print_calendar(*parse_args(args))


if __name__ == '__main__':
    main()
