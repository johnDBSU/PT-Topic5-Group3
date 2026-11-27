def fmt(v):
    return '(' + ' '.join(str(x) for x in v) + ')'


def read_int(prompt, low, high=None):
    while True:
        try:
            x = int(input(prompt))
        except ValueError:
            print('  enter an integer')
            continue
        if x < low or (high is not None and x > high):
            print('  enter a value in range')
            continue
        return x


def read_vec(prompt, size):
    while True:
        parts = input(prompt).replace(',', ' ').split()
        if len(parts) != size:
            print('  need', size, 'values')
            continue
        try:
            v = [int(p) for p in parts]
        except ValueError:
            print('  integers only')
            continue
        if min(v) < 0:
            print('  no negatives')
            continue
        return v


def format_state(title, total, alloc, maxim, need, avail):
    """One row per process: Allocation, Max and Need side by side."""
    width = max(12, len(fmt(total)) + 2, *(len(fmt(row)) + 2 for row in maxim))
    row_fmt = '  %-5s' + ('%%-%ds' % width) * 3
    lines = ['\n' + title, 'Total     ' + fmt(total),
             row_fmt % ('', 'Allocation', 'Max', 'Need')]
    for i in range(len(alloc)):
        lines.append(row_fmt % ('P%d' % i, fmt(alloc[i]), fmt(maxim[i]), fmt(need[i])))
    lines.append('Available ' + fmt(avail))
    return '\n'.join(line.rstrip() for line in lines)
