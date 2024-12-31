#!/usr/bin/env python3

from datetime import timedelta, datetime, time
from textwrap import dedent, indent

WEEKDAYS = {
    'Monday': 'M',
    'Tuesday': 'T',
    'Wednesday': 'W',
    'Thursday': 'RH',
    'Friday': 'F',
    'Saturday': 'U',
    'Sunday': '',
}
WEEKDAY_CODES = dict(
    (code, name)
    for name, codes in WEEKDAYS.items()
    for code in codes
)

START_HOUR = 8
END_HOUR = 19


class Meeting:

    def __init__(self, times, title, location):
        self.weekdays, self.time = times.split()
        self.weekdays = list(self.weekdays)
        self.start_time, self.end_time = self.time.split('-')
        self.start_time = time(int(self.start_time[0:2]), int(self.start_time[3:5]))
        self.end_time = time(int(self.end_time[0:2]), int(self.end_time[3:5]))
        self.title = title
        self.location = location

    def generate_html(self):
        divs = []
        for day in self.weekdays:
            weekday = WEEKDAY_CODES[day]
            time = self.start_time.strftime('time%H%M')
            duration = (
                (60 * self.end_time.hour + self.end_time.minute)
                - (60 * self.start_time.hour + self.start_time.minute)
            )
            divs.append(dedent(f'''
                <div class="event {weekday.lower()} {time} duration{duration:03d}">
                    <div class="description">
                        {self.time}<br>
                        {self.title}<br>
                        {self.location}
                    </div>
                </div>
            ''').strip())
        return divs


def print_styles(week_start=-1, minute_height=1.5, day_width=150):
    # precalculate
    col_header_height = minute_height * 100 // 2
    event_width = day_width - 5
    # initialize styles
    lines = [
        *dedent(f'''
            <style>
                div {{position:absolute;}}
                .grid {{background-color:#FFFFFF; border:dotted 1px #808080; width:{day_width}px;}}
                .event {{background-color:#FFFFFF; border:solid 1px #000000; font-size:smaller; overflow:hidden; width:{event_width}px;}}
                .description {{padding:0.5ex; white-space: nowrap;}}
                .header {{align-items:center; display:flex; font-weight:bold; justify-content:center;}}
                .col-header {{height:{col_header_height}px; top:0; width:{day_width}px;}}
                .row-header {{left:0; width:1in;}}
        ''').strip().splitlines()
    ]
    # print weekday (horizontal) offsets
    for index in range(len(WEEKDAYS)):
        weekday = list(WEEKDAYS.keys())[(index + week_start) % 7]
        left = 100 + index * 150
        lines.append(f'    .{weekday.lower()} {{left:{left:d}px;}}')
    # print time (vertical) offsets
    for hour in range(START_HOUR, END_HOUR):
        for minute in range(0, 60, 5):
            time = 100 * hour + minute
            top = int(col_header_height + (60 * (hour - START_HOUR) + minute) )
            lines.append(f'    .time{time:04d} {{top:{top:d}px;}}')
    # print duration lengths
    for duration in range(5, (END_HOUR - START_HOUR) * 60):
        lines.append(f'    .duration{duration:03d} {{height:{duration:d}px;}}')
    lines.append('</style>')
    print(indent('\n'.join(lines), '    ', (lambda line: not line.startswith('<'))))


def print_grid(resolution=60, civilian_time=False):
    if resolution < 5 or resolution % 5 != 0:
        raise ValueError(f'grid resolution of {resolution} minutes is a multiple of 5')
    week_start = datetime.strptime(datetime.now().strftime('%Y-%m-%d'), '%Y-%m-%d')
    week_start -= timedelta(week_start.weekday() + 1)
    # print column labels
    for weekday in WEEKDAYS:
        print(f'<div class="header col-header {weekday.lower()}">{weekday.upper()}</div>')
    # print row labels
    cur_time = datetime.now().replace(hour=START_HOUR, minute=0)
    while cur_time.hour < END_HOUR:
        military_time = cur_time.strftime('%H%M')
        if not civilian_time:
            display_time = cur_time.strftime('%H:%M')
        elif cur_time.hour == 12 and cur_time.minute == 0:
            display_time = 'noon'
        else:
            display_time = cur_time.strftime('%I:%M %p').strip('0')
        print(dedent(f'''
            <div class="header row-header time{military_time} duration{resolution:03d}">
                {display_time.upper()}
            </div>
        ''').strip())
        cur_time += timedelta(minutes=resolution)
    # print grid
    for days_offset, weekday in enumerate(WEEKDAYS):
        cur_time = datetime.now().replace(hour=START_HOUR, minute=0)
        while cur_time.hour < END_HOUR:
            classes = []
            classes.append('grid')
            classes.append(weekday.lower())
            classes.append(cur_time.strftime('time%H%M'))
            classes.append(f'duration{resolution:03d}')
            classes = ' '.join(classes)
            print(f'<div class="{classes}"></div>')
            cur_time += timedelta(minutes=resolution)


def print_meetings(schedule):
    for meeting in schedule:
        for div in meeting.generate_html():
            print(div)


def main():
    schedule = [
        Meeting('MWF 09:35-10:30', 'Practicum in CS', 'Mosher 3'),
        Meeting('TR 10:05-11:30', 'CS Junior Seminar', 'Mosher 3'),
        Meeting('W 12:00-13:00', 'Office Hours', 'Swan B102'),
        Meeting('R 13:00-14:00', 'Office Hours', 'Swan B102'),
        Meeting('F 14:00-15:00', 'Office Hours', 'Swan B102'),
        Meeting('H 11:30-13:00', 'Reserved for Meetings', ''),
        Meeting('F 08:30-09:30', 'Reserved for Meetings', ''),
        Meeting('F 12:50-13:40', 'Reserved for Meetings', ''),
    ]
    print_styles()
    print('<h1>Justin Li (justinnhli@oxy.edu)</h1>')
    print('<div>')
    print_grid(civilian_time=True)
    print_meetings(schedule)
    print('</div>')


if __name__ == '__main__':
    main()
