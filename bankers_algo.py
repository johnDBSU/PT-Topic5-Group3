from bankers_io import fmt, show


def safety(need, alloc, avail):
    n = len(need)
    m = len(avail)
    work = avail[:]
    done = [False] * n
    seq = []
    print('\nWork =', fmt(work), 'Finish =', done)
    step = 0
    while not all(done):
        step += 1
        print('step', step)
        pick = -1
        for p in range(n):
            if done[p]:
                continue
            ok = all(need[p][r] <= work[r] for r in range(m))
            print('  P%d Need %s <= Work %s ? %s' % (p, fmt(need[p]), fmt(work), 'yes' if ok else 'no'))
            if ok:
                pick = p
                break
        if pick < 0:
            break
        old = work[:]
        work = [work[r] + alloc[pick][r] for r in range(m)]
        done[pick] = True
        seq.append(pick)
        print('  Work %s + %s = %s, Finish[%d] = True' % (fmt(old), fmt(alloc[pick]), fmt(work), pick))
    print('Finish =', done, 'Work =', fmt(work))
    if all(done):
        print('SAFE:', ' -> '.join('P%d' % p for p in seq))
        return True
    print('UNSAFE STATE, blocked:', [p for p in range(n) if not done[p]])
    return False


def check_request(pid, req, total, alloc, need, avail, maxim):
    m = len(avail)
    ok = all(req[r] <= need[pid][r] for r in range(m))
    print('Request <= Need:', fmt(req), '<=', fmt(need[pid]), '?', ok)
    if not ok:
        print('WAIT: exceeds Need')
        return alloc, need, avail
    ok = all(req[r] <= avail[r] for r in range(m))
    print('Request <= Available:', fmt(req), '<=', fmt(avail), '?', ok)
    if not ok:
        print('WAIT: not enough Available')
        return alloc, need, avail
    new_alloc = [row[:] for row in alloc]
    for r in range(m):
        new_alloc[pid][r] += req[r]
    new_need = [[maxim[p][r] - new_alloc[p][r] for r in range(m)] for p in range(len(alloc))]
    new_avail = [avail[r] - req[r] for r in range(m)]
    show('Tentative state', total, new_alloc, maxim, new_need, new_avail)
    if safety(new_need, new_alloc, new_avail):
        print('GRANT')
        return new_alloc, new_need, new_avail
    print('WAIT: unsafe, rolled back')
    return alloc, need, avail
