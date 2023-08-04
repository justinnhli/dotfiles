#!/usr/bin/env python3
"""Convert Gmail conversation print content to a journal-suitable format."""

import re
from sys import stdin
from argparse import ArgumentParser, FileType
from collections import namedtuple
from datetime import datetime
from textwrap import indent

SIGNATURE = '''
 ___ Justin (Ning Hui) Li
(o,o) Comp-Sci & Cog-Sci
/)  ) Occidental College
-"-"- http://justinnhli.com/
'''.strip('\n')

Person = namedtuple('Person', ('name', 'email'))
Email = namedtuple('Email', ('date', 'sender', 'recipients', 'subject', 'text'))


def parse_email(lines, subject):
    # type: (list[str], str) -> Email
    """Parse a string into an Email."""
    match = re.match('([^<>]*) <([^<>]*@[^<>]*)>(.*)', lines[0])
    sender_name = match.group(1)
    if sender_name == 'Justin (Ning Hui) Li':
        sender_name = 'Justin Li'
    sender = Person(sender_name, match.group(2))
    date_str = match.group(3).strip()
    date = datetime.strptime(date_str, '%a, %b %d, %Y at %I:%M %p')
    recipients = []
    for line in lines[1:4]:
        if line[:3] not in ('To:', 'Cc:', 'Bcc'):
            continue
        field, addressees = line.split(':', maxsplit=1)
        assert field in ('To', 'Cc', 'Bcc')
        recipients = addressees.strip()
    text_start = 2
    while True:
        if lines[text_start].startswith('Cc:') or lines[text_start].startswith('Bcc:'):
            text_start += 1
        else:
            break
    lines = [
        line.rstrip() for line in lines[text_start:]
        if line.strip() not in ('', '[Quoted text hidden]')
    ]
    text = '\n'.join(lines)
    if text.endswith(SIGNATURE):
        text = text[:-len(SIGNATURE)].strip()
    return Email(date, sender, recipients, subject, text)


def format_emails(text):
    # type: (str) -> None
    """Print out emails one by one."""
    emails = []
    subject = ''
    lines = text.strip().splitlines()
    subject = lines[1]
    num_emails = int(lines[2].split()[0])
    email_num = 0
    email_start = None
    for line_num, line in enumerate(lines[3:], start=3):
        if line.startswith('To: '):
            if email_start is not None:
                match = re.match('(.*) <([^<>]*@[^<>]*)>(.*)', lines[email_start])
                if not match:
                    num_emails -= 1
                    email_start = None
                    continue
                email_lines = lines[email_start:line_num - 1]
                emails.append(parse_email(email_lines, subject))
                email_num += 1
                if email_num == num_emails:
                    break
            email_start = line_num - 1
    if email_num != num_emails:
        email_lines = lines[email_start:]
        emails.append(parse_email(email_lines, subject))
    if len(emails) != num_emails:
        print(f'WARNING: Gmail lists {num_emails} emails, but I found {len(emails)}')
        print()
    for email in emails:
        print(f'{email.date.strftime("%Y-%m-%d")} ({email.sender.name})')
        print(indent(email.text, '\t'))


def main():
    # type: () -> None
    """Provide a CLI entry point."""
    arg_parser = ArgumentParser()
    arg_parser.add_argument('inputfile', nargs='?', type=FileType('r'), default=stdin)
    args = arg_parser.parse_args()
    format_emails(args.inputfile.read())


if __name__ == '__main__':
    main()
