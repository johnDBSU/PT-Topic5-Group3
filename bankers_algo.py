"""Banker's Algorithm logic. Nothing here prints or reads input, so the
console and GUI versions share it. `log` is a list that collects the trace."""
from bankers_io import fmt, format_state

GRANT, WAIT, ERROR = 'GRANT', 'WAIT', 'ERROR'


def check_totals(total, alloc):
    """Return an error message, or None if the allocation fits in Total."""
    for r in range(len(total)):
        used = sum(row[r] for row in alloc)
        if used > total[r]:
            return 'R%d: allocated %d exceeds total %d' % (r, used, total[r])
    return None


def check_max(total, alloc, maxim):
    """Return an error message, or None if Allocation <= Max <= Total."""
    for p in range(len(alloc)):
        for r in range(len(total)):
            if maxim[p][r] < alloc[p][r]:
                return 'P%d R%d: Max %d is below Allocation %d' % (p, r, maxim[p][r], alloc[p][r])
            if maxim[p][r] > total[r]:
                return 'P%d R%d: Max %d exceeds Total %d' % (p, r, maxim[p][r], total[r])
    return None


def derive(total, alloc, maxim):
    """Return (need, avail)."""
    need = [[x - a for x, a in zip(mx, al)] for mx, al in zip(maxim, alloc)]
    avail = [total[r] - sum(row[r] for row in alloc) for r in range(len(total))]
    return need, avail


def safety(need, alloc, avail, log):
    """Return (is_safe, sequence)."""
    n = len(need)
    m = len(avail)
    work = avail[:]
    done = [False] * n
    seq = []
    log.append('\nWork = %s Finish = %s' % (fmt(work), done))
    step = 0
    while not all(done):
        step += 1
        log.append('step %d' % step)
        pick = -1
        for p in range(n):
            if done[p]:
                continue
            ok = all(need[p][r] <= work[r] for r in range(m))
            log.append('  P%d Need %s <= Work %s ? %s' % (p, fmt(need[p]), fmt(work), 'yes' if ok else 'no'))
            if ok:
                pick = p
                break
        if pick < 0:
            break
        old = work[:]
        work = [work[r] + alloc[pick][r] for r in range(m)]
        done[pick] = True
        seq.append(pick)
        log.append('  Work %s + %s = %s, Finish[%d] = True' % (fmt(old), fmt(alloc[pick]), fmt(work), pick))
    log.append('Finish = %s Work = %s' % (done, fmt(work)))
    if all(done):
        log.append('SAFE: ' + ' -> '.join('P%d' % p for p in seq))
        return True, seq
    log.append('UNSAFE STATE, blocked: %s' % [p for p in range(n) if not done[p]])
    return False, seq


def check_request(pid, req, total, alloc, maxim, log):
    """Return (status, alloc). alloc changes only when status is GRANT."""
    need, avail = derive(total, alloc, maxim)
    m = len(total)
    ok = all(req[r] <= need[pid][r] for r in range(m))
    log.append('Request <= Need: %s <= %s ? %s' % (fmt(req), fmt(need[pid]), ok))
    if not ok:
        log.append('ERROR: request exceeds the maximum claim')
        return ERROR, alloc
    ok = all(req[r] <= avail[r] for r in range(m))
    log.append('Request <= Available: %s <= %s ? %s' % (fmt(req), fmt(avail), ok))
    if not ok:
        log.append('WAIT: not enough Available')
        return WAIT, alloc
    new_alloc = [row[:] for row in alloc]
    for r in range(m):
        new_alloc[pid][r] += req[r]
    new_need, new_avail = derive(total, new_alloc, maxim)
    log.append(format_state('Tentative state', total, new_alloc, maxim, new_need, new_avail))
    if safety(new_need, new_alloc, new_avail, log)[0]:
        log.append('GRANT')
        return GRANT, new_alloc
    log.append('WAIT: unsafe, rolled back')
    return WAIT, alloc


def release(pid, rel, alloc, log):
    """Return (ok, alloc)."""
    if any(x > a for x, a in zip(rel, alloc[pid])):
        log.append('ERROR: P%d cannot release more than it holds %s' % (pid, fmt(alloc[pid])))
        return False, alloc
    new_alloc = [row[:] for row in alloc]
    new_alloc[pid] = [a - x for a, x in zip(alloc[pid], rel)]
    log.append('P%d released %s' % (pid, fmt(rel)))
    return True, new_alloc
