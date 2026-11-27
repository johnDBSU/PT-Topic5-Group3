# Banker's Algorithm

A deadlock avoidance simulator written in Python, with a console version and a GUI version.

*Topic 5 - Group 3*

Enter the system's resources and each process's allocation and maximum claim. The program checks whether the state is safe, then decides whether each new request can be granted. Every step of the safety check is shown.

## Requirements

- Python 3 (tested with 3.12)
- Tkinter for the GUI version; no external libraries

## Run

From the project folder:

```bash
python bankers_gui.py   # GUI version
python bankers.py       # console version
```

## Controls

### GUI

| Control | Action |
|---|---|
| `Create tables` | Build empty tables for the chosen number of processes and resources (1 - 10 each) |
| `Load example` | Fill in a 5-process, 3-resource example |
| `Check safety` | Validate the values and run the safety algorithm |
| `Request` | Ask for resources for the selected process |
| `Release` | Return resources held by the selected process |
| `Edit / reset` | Unlock the tables and restore the starting allocation |

`Request` and `Release` are enabled after a successful `Check safety`.

### Console

| Input | Action |
|---|---|
| `r` | Request resources |
| `l` | Release resources |
| `s` | Show the current state and run the safety check |
| `q` | Quit |

Enter each row as numbers separated by spaces or commas, such as `10 5 7`.

## How it works

1. Enter Total, Allocation and Max.
2. The program checks that allocations do not exceed Total, and that Allocation <= Max <= Total.
3. It computes `Need = Max - Allocation` and `Available = Total - sum of Allocation`.
4. The safety algorithm looks for an order in which every process can finish.
5. A request is tried on a temporary copy of the state and kept only if that state is safe.

## Request results

| Result | Meaning |
|---|---|
| `GRANT` | The request fits and the new state is safe |
| `WAIT` | Not enough Available, or granting it would make the state unsafe |
| `ERROR` | The request exceeds the process's Need |

## Example

Total is `10 5 7`.

| Process | Allocation | Max | Need |
|---|---|---|---|
| P0 | 0 1 0 | 7 5 3 | 7 4 3 |
| P1 | 2 0 0 | 3 2 2 | 1 2 2 |
| P2 | 3 0 2 | 9 0 2 | 6 0 0 |
| P3 | 2 1 1 | 2 2 2 | 0 1 1 |
| P4 | 0 0 2 | 4 3 3 | 4 3 1 |

Available is `3 3 2`. The state is safe: `P1 -> P3 -> P0 -> P2 -> P4`.

Try these requests in order:

| Process | Request | Result |
|---|---|---|
| P1 | 1 0 2 | `GRANT` |
| P4 | 3 3 0 | `WAIT` - not enough Available |
| P0 | 0 2 0 | `WAIT` - unsafe, rolled back |
| P3 | 5 0 0 | `ERROR` - exceeds Need |

## Project structure

| File | Responsibility |
|---|---|
| `bankers.py` | Console entry point and menu |
| `bankers_gui.py` | Tkinter window, input tables and trace log |
| `bankers_algo.py` | Validation, safety algorithm, request and release |
| `bankers_io.py` | Console input and state formatting |

## Concepts in use

- **Deadlock avoidance** - a request is granted only if the system stays in a safe state.
- **Safety algorithm** - uses Work and Finish to find a safe sequence.
- **Resource-request algorithm** - checks Need, then Available, then safety.
- **Separation of concerns** - both versions share the same algorithm code.

## Notes

- No build step or installation of packages is needed.
- Processes and resources are numbered from 0 (`P0`, `R0`).
- The GUI does not scroll, so large tables may not fit on a small screen.
