#!/usr/bin/env python3

# taken from
# https://docs.python.org/3/library/readline.html?highlight=readline#example

import atexit
import os
try:
    import readline
except ImportError:
    exit()

histfile = os.path.join(
    os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config')),
    'python',
    '.python_history',
)

try:
    readline.read_history_file(histfile)
    h_len = readline.get_current_history_length()
except FileNotFoundError:
    open(histfile, 'wb').close()
    h_len = 0

def save(prev_h_len, histfile):
    new_h_len = readline.get_current_history_length()
    readline.set_history_length(1000)
    if hasattr(readline, 'append_history_file'):
        readline.append_history_file(new_h_len - prev_h_len, histfile)

atexit.register(save, h_len, histfile)
