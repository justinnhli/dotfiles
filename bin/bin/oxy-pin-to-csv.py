#!/usr/bin/env python3

import sys
from csv import DictReader

if len(sys.argv) != 2:
    print(f'usage: {sys.argv[0]} <pin-export.csv>')
    sys.exit(1)

# account for the byte-order-mark
students = []
with open(sys.argv[1], encoding='utf-8-sig') as fd:
    for row in DictReader(fd):
        advisors = ', '.join([row['Pri. Adviser'], row['Sec. Advisor']])
        advisors = advisors.strip().strip(',')
        students.append('\n'.join([
            f'{row["Student Pref First Name"]} {row["Student Last Name"]} (advisor(s): {advisors})',
            f'    PIN: {row["PIN"]}',
            f'    1st registration time: {row["1st Date"]} {row["1st Time"]} PT',
            f'    2nd registration time: {row["2nd Date"]} {row["2nd Time"]} PT',
        ]))
for student in sorted(students):
    print(student)
