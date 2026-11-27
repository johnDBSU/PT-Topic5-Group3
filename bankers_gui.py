import os
import sys
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

# Make sibling imports work when Python runs in isolated mode.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bankers_algo import (ERROR, GRANT, check_max, check_request, check_totals,
                          derive, release, safety)
from bankers_io import fmt, format_state

LIMIT = 10  # largest table the window is designed for
GREEN, ORANGE, RED, BLACK = '#176b2c', '#9a5b00', '#b00020', '#000000'


class BankersApp:
    def __init__(self, root):
        self.root = root
        root.title("Banker's Algorithm")
        self.n = tk.StringVar(value='5')
        self.m = tk.StringVar(value='3')

        top = ttk.Frame(root, padding=8)
        top.pack(fill='x')
        for text, var in (('Processes', self.n), ('Resources', self.m)):
            ttk.Label(top, text=text).pack(side='left')
            ttk.Spinbox(top, from_=1, to=LIMIT, textvariable=var, width=4).pack(side='left', padx=(4, 12))
        ttk.Button(top, text='Create tables', command=self.create_tables).pack(side='left')
        ttk.Button(top, text='Load example', command=self.load_example).pack(side='left', padx=6)

        self.tables = ttk.Frame(root, padding=8)
        self.tables.pack(fill='x')

        controls = ttk.Frame(root, padding=8)
        controls.pack(fill='x')
        self.start_button = ttk.Button(controls, text='Check safety', command=self.check_safety)
        self.start_button.grid(row=0, column=0, sticky='w')
        self.reset_button = ttk.Button(controls, text='Edit / reset', command=self.reset)
        self.reset_button.grid(row=0, column=1, sticky='w', padx=6)
        ttk.Label(controls, text='Process').grid(row=1, column=0, sticky='e', pady=6)
        self.process = ttk.Combobox(controls, state='readonly', width=6)
        self.process.grid(row=1, column=1, sticky='w', padx=6)
        self.vector = ttk.Frame(controls)
        self.vector.grid(row=1, column=2)
        self.request_button = ttk.Button(controls, text='Request', command=self.request)
        self.request_button.grid(row=1, column=3, padx=6)
        self.release_button = ttk.Button(controls, text='Release', command=self.release)
        self.release_button.grid(row=1, column=4)

        self.status = tk.Label(root, anchor='w', padx=8, font=('TkDefaultFont', 11, 'bold'))
        self.status.pack(fill='x')
        self.log = ScrolledText(root, height=16, width=80, font='TkFixedFont', state='disabled')
        self.log.pack(fill='both', expand=True, padx=8, pady=8)

        self.create_tables()

    # ---- building the tables ----
    def create_tables(self):
        try:
            n, m = int(self.n.get()), int(self.m.get())
            if not (1 <= n <= LIMIT and 1 <= m <= LIMIT):
                raise ValueError
        except ValueError:
            self.set_status('ERROR: processes and resources must be 1 to %d' % LIMIT, RED)
            return
        self.size = (n, m)
        for frame in (self.tables, self.vector):
            for child in frame.winfo_children():
                child.destroy()
        self.total = self.grid_block('Total', 0, 0, 1, m, [''])[0]
        names = ['P%d' % p for p in range(n)]
        self.alloc = self.grid_block('Allocation', 1, 0, n, m, names)
        self.maxim = self.grid_block('Max', 1, 1, n, m, names)
        self.need = self.grid_block('Need', 1, 2, n, m, names, readonly=True)
        self.avail = self.grid_block('Available', 0, 1, 1, m, [''], readonly=True)[0]
        self.amount = []
        for r in range(m):
            entry = ttk.Entry(self.vector, width=4, justify='center')
            entry.insert(0, '0')
            entry.pack(side='left', padx=1)
            self.amount.append(entry)
        self.process['values'] = names
        self.process.current(0)
        self.state = None
        self.set_running(False)
        self.set_status('Enter Total, Allocation and Max, then press Check safety.', BLACK)

    def grid_block(self, title, row, col, n, m, names, readonly=False):
        box = ttk.LabelFrame(self.tables, text=title, padding=4)
        box.grid(row=row, column=col, padx=4, pady=4, sticky='nw')
        for r in range(m):
            ttk.Label(box, text='R%d' % r).grid(row=0, column=r + 1)
        cells = []
        for p in range(n):
            ttk.Label(box, text=names[p]).grid(row=p + 1, column=0, padx=2)
            line = []
            for r in range(m):
                entry = ttk.Entry(box, width=4, justify='center')
                entry.grid(row=p + 1, column=r + 1, padx=1, pady=1)
                if readonly:
                    entry.state(['readonly'])
                line.append(entry)
            cells.append(line)
        return cells

    def load_example(self):
        self.n.set('5')
        self.m.set('3')
        self.create_tables()
        self.fill(self.total, [10, 5, 7])
        for cells, rows in ((self.alloc, ['010', '200', '302', '211', '002']),
                            (self.maxim, ['753', '322', '902', '222', '433'])):
            for line, digits in zip(cells, rows):
                self.fill(line, digits)

    # ---- helpers ----
    @staticmethod
    def fill(cells, values):
        for entry, value in zip(cells, values):
            locked = entry.instate(['readonly'])
            entry.state(['!readonly'])
            entry.delete(0, 'end')
            entry.insert(0, str(value))
            if locked:
                entry.state(['readonly'])

    def read_row(self, cells, name):
        values = []
        for r, entry in enumerate(cells):
            text = entry.get().strip()
            try:
                value = int(text)
                if value < 0:
                    raise ValueError
            except ValueError:
                entry.focus_set()
                self.set_status('ERROR: %s R%d must be a whole number, 0 or more' % (name, r), RED)
                return None
            values.append(value)
        return values

    def read_matrix(self, cells, name):
        rows = []
        for p, line in enumerate(cells):
            row = self.read_row(line, '%s P%d' % (name, p))
            if row is None:
                return None
            rows.append(row)
        return rows

    def set_status(self, text, color):
        self.status.config(text=text, fg=color)

    def write(self, lines):
        self.log.config(state='normal')
        self.log.insert('end', '\n'.join(lines) + '\n')
        self.log.config(state='disabled')
        self.log.see('end')

    def set_running(self, running):
        """Lock the inputs while a state is loaded, so the tables stay truthful."""
        for line in [self.total] + self.alloc + self.maxim:
            for entry in line:
                entry.state(['readonly' if running else '!readonly'])
        for button in (self.request_button, self.release_button):
            button.state(['!disabled' if running else 'disabled'])

    def refresh(self):
        total, alloc, maxim = self.state
        need, avail = derive(total, alloc, maxim)
        for cells, rows in ((self.alloc, alloc), (self.need, need)):
            for line, row in zip(cells, rows):
                self.fill(line, row)
        self.fill(self.avail, avail)

    # ---- actions ----
    def check_safety(self):
        if self.state is None:
            total = self.read_row(self.total, 'Total')
            if total is None:
                return
            alloc = self.read_matrix(self.alloc, 'Allocation')
            if alloc is None:
                return
            maxim = self.read_matrix(self.maxim, 'Max')
            if maxim is None:
                return
            error = check_totals(total, alloc) or check_max(total, alloc, maxim)
            if error:
                self.set_status('ERROR: ' + error, RED)
                return
            self.state = (total, alloc, maxim)
            self.initial = alloc
            self.set_running(True)
        total, alloc, maxim = self.state
        need, avail = derive(total, alloc, maxim)
        self.refresh()
        log = [format_state('Current state', total, alloc, maxim, need, avail)]
        safe, seq = safety(need, alloc, avail, log)
        self.write(log)
        if safe:
            self.set_status('SAFE: ' + ' -> '.join('P%d' % p for p in seq), GREEN)
        else:
            self.set_status('UNSAFE: no safe sequence exists', RED)

    def action_input(self):
        amount = self.read_row(self.amount, 'Request/Release')
        return self.process.current(), amount

    def request(self):
        pid, req = self.action_input()
        if req is None:
            return
        total, alloc, maxim = self.state
        log = ['\n--- P%d requests %s ---' % (pid, fmt(req))]
        status, alloc = check_request(pid, req, total, alloc, maxim, log)
        self.state = (total, alloc, maxim)
        self.refresh()
        self.write(log)
        color = {GRANT: GREEN, ERROR: RED}.get(status, ORANGE)
        self.set_status(log[-1], color)

    def release(self):
        pid, rel = self.action_input()
        if rel is None:
            return
        total, alloc, maxim = self.state
        log = ['']
        ok, alloc = release(pid, rel, alloc, log)
        self.state = (total, alloc, maxim)
        self.refresh()
        self.write(log)
        self.set_status(log[-1], GREEN if ok else RED)

    def reset(self):
        """Go back to the starting values so they can be edited."""
        if self.state is None:
            return
        self.state = None
        self.set_running(False)
        for line, row in zip(self.alloc, self.initial):
            self.fill(line, row)
        for line in self.need + [self.avail]:
            self.fill(line, [''] * len(line))
        self.set_status('Edit the values, then press Check safety.', BLACK)


def main():
    root = tk.Tk()
    BankersApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
