import os
import sys

# Make sibling imports work when Python runs in isolated mode.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bankers_algo import check_max, check_request, check_totals, derive, release, safety
from bankers_io import format_state, read_int, read_vec


def report(title, total, alloc, maxim, check_safety=False):
    need, avail = derive(total, alloc, maxim)
    print(format_state(title, total, alloc, maxim, need, avail))
    if check_safety:
        log = []
        safety(need, alloc, avail, log)
        print('\n'.join(log))


def main():
    print("Banker's Algorithm")
    n = read_int('Processes: ', 1)
    m = read_int('Resources: ', 1)
    while True:
        total = read_vec('Total: ', m)
        alloc = [read_vec('Allocation P%d: ' % p, m) for p in range(n)]
        error = check_totals(total, alloc)
        if not error:
            break
        print('  %s, re-enter' % error)
    while True:
        maxim = [read_vec('Max P%d: ' % p, m) for p in range(n)]
        error = check_max(total, alloc, maxim)
        if not error:
            break
        print('  %s, re-enter' % error)
    report('Initial state', total, alloc, maxim, check_safety=True)
    while True:
        cmd = input('\n[r]equest re[l]ease [s]how [q]uit: ').strip().lower()
        if cmd == 'q':
            break
        if cmd == 's':
            report('Current state', total, alloc, maxim, check_safety=True)
        elif cmd in ('r', 'l'):
            p = read_int('Process: ', 0, n - 1)
            log = []
            if cmd == 'r':
                req = read_vec('Request for P%d: ' % p, m)
                alloc = check_request(p, req, total, alloc, maxim, log)[1]
            else:
                rel = read_vec('Release from P%d: ' % p, m)
                alloc = release(p, rel, alloc, log)[1]
            print('\n'.join(log))
            report('Current state', total, alloc, maxim)
        else:
            print('  unknown command')


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print('\nExiting.')
