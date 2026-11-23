"""The solver: left-hand wall-following explorer (runner.py) plus loop
removal in maze_runner.shortest_path().

What the algorithm guarantees, and so what is asserted:
- It always returns a valid, non-repeating path through open cells.
- On a perfect maze (no loops) that path is the unique, hence shortest, path.
- On mazes with loops the result is valid but *not* guaranteed shortest, so
  only `len(path) >= BFS shortest` is checked there.
- It has no unreachable-goal detection (see the xfail test at the bottom).
"""
import pytest

import maze_runner
import runner as runner_mod
from maze import add_horizontal_wall, add_vertical_wall, create_maze
from maze_runner import input_validation, maze_reader, shortest_path
from mazetools import REPO_ROOT, assert_valid_path, bfs_distance, maze_from_text
from runner import create_runner, explore, forward, sense_walls, turn


def load(name):
    return maze_reader(str(REPO_ROOT / name))


class TestRunner:
    def test_turns_wrap_around_compass(self):
        r = create_runner(0, 0, "N")
        assert turn(r, "left")[2] == "W"
        assert turn(r, "right")[2] == "N"
        assert turn(turn(r, "right"), "right")[2] == "S"

    def test_forward_moves_in_facing_direction(self):
        assert forward(create_runner(1, 1, "N"))[:2] == [1, 2]
        assert forward(create_runner(1, 1, "E"))[:2] == [2, 1]
        assert forward(create_runner(1, 1, "S"))[:2] == [1, 0]
        assert forward(create_runner(1, 1, "W"))[:2] == [0, 1]

    def test_sense_walls_is_relative_to_orientation(self):
        maze = create_maze(3, 3)  # (0,0): walls S and W
        assert sense_walls(create_runner(0, 0, "N"), maze) == (True, False, False)
        assert sense_walls(create_runner(0, 0, "E"), maze) == (False, False, True)

    def test_explore_reaches_goal(self):
        maze = load("maze4.mz")
        r = create_runner(0, 0)
        moves = explore(r, maze)
        assert (r[0], r[1]) == (1, 1)
        assert set(moves) <= set("LRF")


class TestShortestPathSmallMazes:
    def test_open_2x1_corridor(self):
        assert shortest_path(load("maze1.mz")) == [(0, 0), (1, 0)]

    def test_u_shaped_maze4(self):
        assert shortest_path(load("maze4.mz")) == [(0, 0), (1, 0), (1, 1)]

    def test_hand_built_maze_with_walls(self):
        maze = create_maze(11, 5)
        maze = add_horizontal_wall(maze, 0, 1)
        maze = add_vertical_wall(maze, 1, 1)
        path = shortest_path(maze)
        assert_valid_path(maze, path, (0, 0), (10, 4))

    def test_custom_start_and_goal(self):
        maze = load("maze6.mz")
        path = shortest_path(maze, (4, 4), (0, 0))
        assert_valid_path(maze, path, (4, 4), (0, 0))

    def test_start_equals_goal(self):
        assert shortest_path(load("maze6.mz"), (2, 2), (2, 2)) == [(2, 2)]

    def test_writes_exploration_csv(self, tmp_path):
        shortest_path(load("maze4.mz"))
        lines = (tmp_path / "exploration.csv").read_text().splitlines()
        assert lines[0] == "Step,x-coordinate,y-coordinate,Actions"
        assert len(lines) > 1


class TestShortestPathSamples:
    # maze1/maze4/maze6 are perfect mazes (no loops): result must be shortest.
    @pytest.mark.parametrize("name", ["maze1.mz", "maze4.mz", "maze6.mz"])
    def test_perfect_maze_path_is_shortest(self, name):
        maze = load(name)
        goal = (len(maze[0]) - 1, len(maze) - 1)
        path = shortest_path(maze)
        assert_valid_path(maze, path, (0, 0), goal)
        assert len(path) == bfs_distance(maze, (0, 0), goal)

    # maze3/maze5 contain loops: valid, and never shorter than BFS.
    @pytest.mark.parametrize("name", ["maze3.mz", "maze5.mz"])
    def test_looped_maze_path_is_valid(self, name):
        maze = load(name)
        goal = (len(maze[0]) - 1, len(maze) - 1)
        path = shortest_path(maze)
        assert_valid_path(maze, path, (0, 0), goal)
        assert len(path) >= bfs_distance(maze, (0, 0), goal)


class TestInputValidation:
    def test_in_range_passes(self):
        assert input_validation(create_maze(3, 3), (0, 0), (2, 2)) is None

    def test_out_of_range_reports_every_problem(self):
        with pytest.raises(ValueError) as exc:
            input_validation(create_maze(3, 3), (5, 0), (0, 9))
        msg = str(exc.value)
        assert "Start position is out of range of the maze: x" in msg
        assert "Goal position is out of range of the maze: y" in msg


class _StepLimit(Exception):
    pass


@pytest.mark.xfail(strict=True, raises=_StepLimit,
                   reason="Known limitation: the wall-follower has no "
                          "unreachable-goal detection and loops forever.")
def test_unreachable_goal_is_detected(tmp_path, monkeypatch):
    # Goal (2,0) is boxed in on its own; (0,0)-(1,0) can never reach it.
    text = "#######\n#...#.#\n#######"
    maze = maze_reader(str(maze_from_text(tmp_path, text)))
    assert bfs_distance(maze, (0, 0), (2, 0)) is None

    # Bound the run so the test cannot hang: abort after 1000 moves.
    real_move, calls = runner_mod.move, [0]

    def bounded_move(r, m):
        calls[0] += 1
        if calls[0] > 1000:
            raise _StepLimit
        return real_move(r, m)

    monkeypatch.setattr(maze_runner, "move", bounded_move)
    monkeypatch.setattr(maze_runner, "display_maze", lambda *a: "")
    shortest_path(maze, (0, 0), (2, 0))
