"""Independent helpers the tests use to check the solver's output.

These deliberately don't reuse the solver's own logic: BFS here is the
reference "shortest path" the wall-follower result is compared against.
"""
from collections import deque
from pathlib import Path

from maze import get_dimensions, get_walls

REPO_ROOT = Path(__file__).resolve().parent.parent

# Step on the grid for each wall direction (y grows northwards).
STEPS = {"N": (0, 1), "E": (1, 0), "S": (0, -1), "W": (-1, 0)}


def open_neighbours(maze, cell):
    x, y = cell
    north, east, south, west = get_walls(maze, x, y)
    walls = {"N": north, "E": east, "S": south, "W": west}
    for direction, (dx, dy) in STEPS.items():
        if not walls[direction]:
            yield (x + dx, y + dy)


def bfs_distance(maze, start, goal):
    """Number of cells on a shortest start->goal path, or None if unreachable."""
    queue = deque([(start, 1)])
    seen = {start}
    while queue:
        cell, length = queue.popleft()
        if cell == goal:
            return length
        for nxt in open_neighbours(maze, cell):
            if nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, length + 1))
    return None


def assert_valid_path(maze, path, start, goal):
    """Path starts/ends right, stays in bounds, never repeats a cell and
    never walks through a wall."""
    width, height = get_dimensions(maze)
    assert path, "path is empty"
    assert path[0] == start
    assert path[-1] == goal
    assert len(set(path)) == len(path), "path revisits a cell"
    for x, y in path:
        assert 0 <= x < width and 0 <= y < height, f"{(x, y)} out of bounds"
    for here, nxt in zip(path, path[1:]):
        assert nxt in set(open_neighbours(maze, here)), (
            f"illegal step {here} -> {nxt} (not adjacent or through a wall)")


def maze_from_text(tmp_path, text, name="test.mz"):
    """Write maze text to a file so it can go through maze_reader."""
    path = tmp_path / name
    path.write_text(text.strip("\n") + "\n")
    return path
