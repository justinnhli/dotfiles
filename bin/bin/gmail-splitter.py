#!/usr/bin/env python3

import re
import sys
from collections import namedtuple
from datetime import datetime
from textwrap import indent

Person = namedtuple('Person', ('name', 'email'))
Email = namedtuple('Email', ('date', 'sender', 'recipients', 'subject', 'text'))

def read_all_inputs(files):
    if files:
        result = []
        for file in files:
            with open(file, "r") as fd:
                result.append(fd.read())
        return "".join(result)
    elif not sys.stdin.isatty():
        return sys.stdin.read()
    else:
        return ""

def parse_email(lines, subject):
    match = re.match('([^<>]*) <([^<>]*@[^<>]*)>(.*)', lines[0])
    sender = Person(match.group(1), match.group(2))
    date_str = match.group(3).strip()
    date = datetime.strptime(date_str, '%a, %b %d, %Y at %I:%M %p')
    recipients = []
    for offset in range(1, 4):
        if lines[offset][:3] not in ('To:', 'Cc:', 'Bcc'):
            continue
        field, addressees = lines[offset].split(':', maxsplit=1)
        assert field in ('To', 'Cc', 'Bcc')
        recipients = addressees.strip()
    text_start = 2
    while True:
        if lines[text_start].startswith('Cc:') or lines[text_start].startswith('Bcc:'):
            text_start += 1
        else:
            break
    text = '\n'.join(line.rstrip() for line in lines[text_start:] if line.strip() not in ('', '[Quoted text hidden]'))
    return Email(date, sender, recipients, subject, text)

def format_emails(text):
    emails = []
    subject = ''
    lines = text.splitlines()
    subject = lines[1]
    num_emails = int(lines[2].split()[0])
    email_num = 0
    email_start = None
    for line_num, line in enumerate(lines[3:], start=3):
        if line.startswith('To: '):
            if email_start is not None:
                match = re.match('(.*) <([^<>]*@[^<>]*)>(.*)', lines[email_start])
                if not match:
                    continue
                email_lines = lines[email_start:line_num-1]
                emails.append(parse_email(email_lines, subject))
                email_num += 1
                if email_num == num_emails:
                    break
            email_start = line_num - 1
    if email_num != num_emails:
        email_lines = lines[email_start:]
        emails.append(parse_email(email_lines, subject))
    if len(emails) != num_emails:
        print('WARNING: Gmail lists {} emails, but I found {}'.format(num_emails, len(emails)))
    for email in emails:
        print(email.date.strftime('%Y-%m-%d'))
        print(indent(email.text, '\t'))

def main():
    text = read_all_inputs(sys.argv[1:]).strip()
    format_emails(text)

if __name__ == '__main__':
    main()
