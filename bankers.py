import os
import sys

# This machine's python312._pth runs Python in isolated mode, so the script's
# own directory is not on sys.path and sibling imports would fail.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bankers_algo import check_request, safety
from bankers_io import read_int, read_vec, show


def main():
    print("Banker's Algorithm")
    n = read_int('Processes: ', 1)
    m = read_int('Resources: ', 1)
    while True:
        total = read_vec('Total: ', m)
        alloc = [read_vec('Allocation P%d: ' % p, m) for p in range(n)]
        if all(sum(alloc[p][r] for p in range(n)) <= total[r] for r in range(m)):
            break
        print('  allocation exceeds total, re-enter')
    while True:
        maxim = [read_vec('Max P%d: ' % p, m) for p in range(n)]
        if all(alloc[p][r] <= maxim[p][r] for p in range(n) for r in range(m)):
            break
        print('  allocation exceeds max, re-enter')
    need = [[maxim[p][r] - alloc[p][r] for r in range(m)] for p in range(n)]
    avail = [total[r] - sum(alloc[p][r] for p in range(n)) for r in range(m)]
    show('Initial state', total, alloc, maxim, need, avail)
    safety(need, alloc, avail)
    while True:
        cmd = input('\n[r]equest [s]how [q]uit: ').strip().lower()
        if cmd == 'q':
            break
        if cmd == 's':
            show('Current state', total, alloc, maxim, need, avail)
            safety(need, alloc, avail)
        elif cmd == 'r':
            p = read_int('Process: ', 0, n - 1)
            req = read_vec('Request for P%d: ' % p, m)
            alloc, need, avail = check_request(p, req, total, alloc, need, avail, maxim)
            show('Current state', total, alloc, maxim, need, avail)
        else:
            print('  unknown command')


if __name__ == '__main__':
    main()
