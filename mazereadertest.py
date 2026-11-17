import pytest

from maze import get_dimensions, get_walls  # type: ignore
from maze_runner import maze_reader  # type: ignore

def test_maze_reader_maze1() -> None:
    maze = maze_reader("maze1.mz")
    assert get_dimensions(maze) == (2, 1)
    assert get_walls(maze, 0, 0) == (True, False, True, True)
    assert get_walls(maze, 1, 0) == (True, True, True, False)

def test_maze_reader_maze2() -> None:
    with pytest.raises(ValueError):
        maze_reader("maze2.mz")
