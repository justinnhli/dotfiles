#!/usr/bin/env python3
"""A basic GUI timer."""

from types import SimpleNamespace
import tkinter as tk


class Timer():
    """A basic GUI timer."""

    def __init__(self):
        # type: () -> None
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
            (lambda name, index, mode: self._time_input_callback()),
        )
        self.started = False
        self._create_widgets()
        self.time_input_var.set(self.time_str)

    def _create_widgets(self):
        # type: () -> None
        textbox = tk.Entry(self.root, textvariable=self.time_input_var, width=10, justify='center')
        textbox.grid(row=0, column=0)
        self.widgets.textbox = textbox

        start_button = tk.Button(self.root, text='Start', command=self._start_timer)
        start_button.grid(row=0, column=1)
        self.widgets.start_button = start_button

        stop_button = tk.Button(self.root, text='Stop', state='disabled', command=self._stop_timer)
        stop_button.grid(row=0, column=2)
        self.widgets.stop_button = stop_button

        label = tk.Label(self.root, text=self.time_str, font=('Helvetica', 96))
        label.grid(row=1, columnspan=3)
        self.widgets.label = label

    @property
    def time_str(self):
        # type: () -> str
        """Format the time remaining."""
        return f'{self.time // 60}:{self.time % 60:02d}'

    def _time_input_callback(self):
        # type: () -> None
        time_input = self.widgets.textbox.get()
        parts = time_input.split(':')
        parts = (3 - len(parts)) * ['0'] + parts
        try:
            self.time = (60**2) * int(parts[0]) + 60 * int(parts[1]) + int(parts[2])
        except ValueError:
            pass
        self.widgets.label['text'] = self.time_str

    def _start_timer(self):
        # type: () -> None
        self._time_input_callback()
        self.started = True
        self.widgets.start_button['state'] = 'disabled'
        self.widgets.stop_button['state'] = 'normal'
        self.widgets.textbox['state'] = 'disabled'
        self.root.after(self.interval * 1000, self._step)

    def _step(self):
        # type: () -> None
        if not self.started:
            return
        if self.time > 0 and self.widgets.label['fg'] != '#A40000':
            self.time -= self.interval
        else:
            self.time += self.interval
            self.widgets.label['fg'] = '#A40000'
        self.widgets.label['text'] = self.time_str
        self.root.after(self.interval * 1000, self._step)

    def _stop_timer(self):
        # type: () -> None
        self.started = False
        self.widgets.start_button['state'] = 'normal'
        self.widgets.stop_button['state'] = 'disabled'
        self.widgets.textbox['state'] = 'normal'
        self.widgets.label['fg'] = '#000000'
        self._time_input_callback()

    def run(self):
        # type: () -> None
        """Run the timer."""
        self.root.mainloop()


if __name__ == '__main__':
    Timer().run()
