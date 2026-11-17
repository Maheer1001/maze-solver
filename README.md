# Maze Explorer

A Python maze runner. It loads a maze from a file, explores it with a wall-following runner, and finds the shortest path between two cells, then writes the exploration log and path statistics to disk.

> Coursework for the University of Southampton Year 1 Programming module (2024–25).

## Modules

- `maze.py` represents the maze as a grid of cells, each with `N/E/S/W` wall flags. It can create mazes, add horizontal and vertical walls, and query dimensions and walls.
- `runner.py` is a runner with a position and orientation. It can turn, move forward, sense walls and explore a maze.
- `maze_runner.py` is the command-line entry point. It parses maze files, validates input, searches for the shortest path, and writes `exploration.csv` and `statistics.txt`.

## Run

```bash
python maze_runner.py maze1.mz
python maze_runner.py --starting "0,0" --goal "4,4" maze3.mz
```

The default start is `(0,0)` and the default goal is the opposite corner. `maze1.mz`, `maze3.mz` to `maze6.mz` are sample mazes from 2×1 up to 100×50. `maze2.mz` is deliberately malformed, for the error-handling test.

## Tests

```bash
pip install pytest
pytest mazetest.py mazereadertest.py shortestpathtest.py
```
