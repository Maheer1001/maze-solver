# maze-solver

A Python maze runner. It loads a maze from a file, explores it with a wall-following runner, and finds the shortest path between two cells, then writes the exploration log and path statistics to disk.

> Coursework for the University of Southampton Year 1 Programming module (2024–25).

## Modules

- `maze.py` represents the maze as a grid of cells, each with `N/E/S/W` wall flags. It can create mazes, add horizontal and vertical walls, and query dimensions and walls.
- `runner.py` is a runner with a position and orientation. It can turn, move forward, sense walls and explore a maze.
- `maze_runner.py` is the command-line entry point. It parses maze files, validates input, searches for the shortest path, and writes `exploration.csv` and `statistics.txt`.

## Prerequisites

- Python 3.10 or newer (tested with 3.13). The code uses only the standard library.
- `pytest` for the tests (listed in `requirements-dev.txt`).

No API keys or other setup are needed.

## Setup

Create a virtual environment (`.venv/` is gitignored) and install pytest.

PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements-dev.txt
```

(On Linux/macOS use `python3` and `source .venv/bin/activate`.)

## Run

```bash
python maze_runner.py maze1.mz
python maze_runner.py --starting "0,0" --goal "4,4" maze3.mz
```

It prints the maze as it is explored and the shortest path, and writes `exploration.csv` and `statistics.txt` to the current folder (both gitignored). The default start is `(0,0)` and the default goal is the opposite corner. `maze1.mz`, `maze3.mz` to `maze6.mz` are sample mazes from 2×1 up to 100×50. `maze2.mz` is deliberately malformed: running it exits with `ValueError: Invalid row`, which the reader test checks for.

## Testing

After setting up the venv, run everything from the repo root:

```bash
python -m pytest
```

Expect `51 passed, 1 xfailed`. `pytest.ini` points pytest at both `tests/` and the original coursework tests (`mazetest.py`, `mazereadertest.py`, `shortestpathtest.py`), so you don't need to name any files. Test runs write their `exploration.csv` / `statistics.txt` to temporary folders, not your checkout (apart from `shortestpathtest.py`, which writes to the repo root; both files are gitignored).

What each part proves:

- `tests/test_setup_check.py` is the "is my setup hooked together?" check. It imports every module, then runs the real entry point (`python maze_runner.py maze6.mz`, plus a `--starting/--goal` run on `maze3.mz`) in a subprocess. It checks that the path in `statistics.txt` is valid and as short as possible, and that `exploration.csv` matches it. The program only uses the terminal, so it needs no display. Run it on its own with `python -m pytest tests/test_setup_check.py`.
- `tests/test_maze.py` covers building mazes and adding walls, loading every bundled `.mz` sample, and each reader error (too small, not enclosed, bad row, bad cell, missing file).
- `tests/test_solver.py` covers the runner's turn/move/sense steps and `shortest_path` on small known mazes, custom start/goal, and start == goal. Every returned path is checked cell by cell (adjacent cells, no walls crossed, no repeats) and compared against an independent BFS. On loop-free mazes (`maze1`, `maze4`, `maze6`) it must equal the BFS shortest length. On mazes with loops (`maze3`, `maze5`) the wall-follower doesn't guarantee the shortest path, so the test only requires a valid path.
- The one `xfail` records a known limitation: if the goal can't be reached, the wall-follower loops forever instead of reporting it. The test stops the run after 1000 moves so it can't hang. If unreachable-goal detection is ever added, the test will start passing and pytest will flag the xfail as out of date.

GitHub Actions (`.github/workflows/tests.yml`) runs the same command on Linux and Windows with Python 3.10 and 3.13 for every push to `main` and every pull request.
