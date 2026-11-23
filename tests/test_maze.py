"""Maze construction (maze.py) and loading from .mz files (maze_reader)."""
import pytest

from maze import (add_horizontal_wall, add_vertical_wall, create_maze,
                  get_dimensions, get_walls)
from maze_runner import maze_reader, str_to_list
from mazetools import REPO_ROOT, maze_from_text


class TestCreateMaze:
    def test_dimensions(self):
        assert get_dimensions(create_maze(7, 3)) == (7, 3)

    def test_default_is_5_by_5(self):
        assert get_dimensions(create_maze()) == (5, 5)

    def test_only_the_outer_border_has_walls(self):
        maze = create_maze(3, 3)
        assert get_walls(maze, 1, 1) == (False, False, False, False)
        assert get_walls(maze, 0, 0) == (False, False, True, True)   # SW corner
        assert get_walls(maze, 2, 2) == (True, True, False, False)   # NE corner

    def test_single_cell_is_fully_enclosed(self):
        assert get_walls(create_maze(1, 1), 0, 0) == (True, True, True, True)

    def test_horizontal_wall_is_two_sided(self):
        maze = add_horizontal_wall(create_maze(4, 4), 2, 1)
        # Wall on line y=1 sits between (2,0) and (2,1).
        assert get_walls(maze, 2, 0)[0] is True   # N of lower cell
        assert get_walls(maze, 2, 1)[2] is True   # S of upper cell

    def test_vertical_wall_is_two_sided(self):
        maze = add_vertical_wall(create_maze(4, 4), 1, 2)
        # Wall on line x=2 sits between (1,1) and (2,1).
        assert get_walls(maze, 1, 1)[1] is True   # E of left cell
        assert get_walls(maze, 2, 1)[3] is True   # W of right cell


class TestMazeReader:
    def test_reads_sample_maze1(self):
        maze = maze_reader(str(REPO_ROOT / "maze1.mz"))
        assert get_dimensions(maze) == (2, 1)
        assert get_walls(maze, 0, 0) == (True, False, True, True)
        assert get_walls(maze, 1, 0) == (True, True, True, False)

    @pytest.mark.parametrize("name, dims", [
        ("maze1.mz", (2, 1)),
        ("maze3.mz", (11, 5)),
        ("maze4.mz", (2, 2)),
        ("maze5.mz", (100, 50)),
        ("maze6.mz", (5, 5)),
    ])
    def test_all_valid_samples_load(self, name, dims):
        assert get_dimensions(maze_reader(str(REPO_ROOT / name))) == dims

    def test_malformed_sample_maze2_rejected(self):
        with pytest.raises(ValueError, match="Invalid row"):
            maze_reader(str(REPO_ROOT / "maze2.mz"))

    def test_text_round_trip_matches_reader(self, tmp_path):
        text = "#####\n#.#.#\n#.#.#\n#...#\n#####"
        from_file = maze_reader(str(maze_from_text(tmp_path, text)))
        assert from_file == str_to_list(text)

    def test_missing_file_raises_ioerror(self, tmp_path):
        with pytest.raises(IOError):
            maze_reader(str(tmp_path / "does-not-exist.mz"))

    @pytest.mark.parametrize("text, message", [
        ("##\n##", "Maze too small"),
        ("#####\n#...#\n##.##", "Maze not encapsulated"),
        ("#####\n#...\n#####", "Invalid row"),
        ("#####\n#.x.#\n#####", "Invalid cell"),
    ])
    def test_invalid_mazes_rejected(self, tmp_path, text, message):
        with pytest.raises(ValueError, match=message):
            maze_reader(str(maze_from_text(tmp_path, text)))
