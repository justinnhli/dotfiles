#!/usr/bin/env python3

from types import SimpleNamespace
import tkinter as tk

class Timer():

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Timer')
        # parameters
        self.time = 4 * 60
        self.interval = 1
        # variables
        self.widgets = SimpleNamespace()
        self.time_input_var = tk.StringVar()
        self.time_input_var.trace(
            'w',
            (lambda name, index, mode: self.time_input_callback()),
        )
        self.timing = False
        self.create_widgets()
        self.time_input_var.set(self.time_str)
        self.root.mainloop()

    def create_widgets(self):
        textbox = tk.Entry(self.root, textvariable=self.time_input_var, width=10, justify='center')
        textbox.grid(row=0, column=0)
        self.widgets.textbox = textbox

        start_button = tk.Button(self.root, text='Start', command=self.start_timer)
        start_button.grid(row=0, column=1)
        self.widgets.start_button = start_button

        stop_button = tk.Button(self.root, text='Stop', state='disabled', command=self.stop_timer)
        stop_button.grid(row=0, column=2)
        self.widgets.stop_button = stop_button

        label = tk.Label(self.root, text=self.time_str, font=('Helvetica', 96))
        label.grid(row=1, columnspan=3)
        self.widgets.label = label

    @property
    def time_str(self):
        return f'{self.time // 60}:{self.time % 60:02d}'

    def time_input_callback(self):
        time_input = self.widgets.textbox.get()
        parts = time_input.split(':')
        parts = (3 - len(parts)) * ['0'] + parts
        try:
            self.time = (60**2) * int(parts[0]) + 60 * int(parts[1]) + int(parts[2])
        except ValueError:
            pass
        self.widgets.label['text'] = self.time_str

    def start_timer(self):
        self.time_input_callback()
        self.timing = True
        self.widgets.start_button['state'] = 'disabled'
        self.widgets.stop_button['state'] = 'normal'
        self.widgets.textbox['state'] = 'disabled'
        self.root.after(self.interval * 1000, self.step)

    def step(self):
        if not self.timing:
            return
        if self.time > 0 and self.widgets.label['fg'] != '#A40000':
            self.time -= self.interval
        else:
            self.time += self.interval
            self.widgets.label['fg'] = '#A40000'
        self.widgets.label['text'] = self.time_str
        self.root.after(self.interval * 1000, self.step)

    def stop_timer(self):
        self.timing = False
        self.widgets.start_button['state'] = 'normal'
        self.widgets.stop_button['state'] = 'disabled'
        self.widgets.textbox['state'] = 'normal'
        self.widgets.label['fg'] = '#000000'
        self.time_input_callback()

Timer()
