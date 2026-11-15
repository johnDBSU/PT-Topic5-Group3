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


def show(title, total, alloc, maxim, need, avail):
    print('\n' + title)
    print('Total     ', fmt(total))
    print('Allocation')
    for i, row in enumerate(alloc):
        print('  P%d %s' % (i, fmt(row)))
    print('Max')
    for i, row in enumerate(maxim):
        print('  P%d %s' % (i, fmt(row)))
    print('Need')
    for i, row in enumerate(need):
        print('  P%d %s' % (i, fmt(row)))
    print('Available ', fmt(avail))
