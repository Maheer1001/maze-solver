"""Setup check: proves a fresh checkout + venv is hooked together.

1. The project modules import with only the standard library + pytest.
2. The real CLI entry point (`python maze_runner.py <maze>`) runs end to end
   in a subprocess on a bundled sample maze, and its output files validate
   against an independent BFS check. The program is terminal-only (no GUI
   window), so nothing needs to be skipped or stubbed.
"""
import ast
import importlib
import subprocess
import sys

import pytest

from maze_runner import maze_reader
from mazetools import REPO_ROOT, assert_valid_path, bfs_distance


@pytest.mark.parametrize("module", ["maze", "runner", "maze_runner"])
def test_project_modules_import(module):
    importlib.import_module(module)


def test_python_version_supported():
    # runner.py uses `match` and `int | str` annotations.
    assert sys.version_info >= (3, 10)


def run_cli(cwd, *args):
    return subprocess.run(
        [sys.executable, str(REPO_ROOT / "maze_runner.py"), *args],
        cwd=cwd, capture_output=True, text=True, timeout=120)


def read_stats(path):
    stats = {}
    for line in path.read_text().splitlines():
        key, _, value = line.partition(": ")
        stats[key] = value
    return stats


def test_cli_solves_sample_maze_end_to_end(tmp_path):
    maze_file = REPO_ROOT / "maze6.mz"
    result = run_cli(tmp_path, str(maze_file))
    assert result.returncode == 0, result.stderr

    stats = read_stats(tmp_path / "statistics.txt")
    path = ast.literal_eval(stats["Shortest path"])
    maze = maze_reader(str(maze_file))
    assert_valid_path(maze, path, (0, 0), (4, 4))
    assert int(stats["Shortest path length"]) == len(path)
    assert len(path) == bfs_distance(maze, (0, 0), (4, 4))  # perfect maze

    csv_lines = (tmp_path / "exploration.csv").read_text().splitlines()
    assert csv_lines[0] == "Step,x-coordinate,y-coordinate,Actions"
    assert len(csv_lines) - 1 == int(stats["Exploration steps"])


def test_cli_accepts_start_and_goal(tmp_path):
    result = run_cli(tmp_path, "--starting", "0,0", "--goal", "4,4",
                     str(REPO_ROOT / "maze3.mz"))
    assert result.returncode == 0, result.stderr
    path = ast.literal_eval(
        read_stats(tmp_path / "statistics.txt")["Shortest path"])
    assert_valid_path(maze_reader(str(REPO_ROOT / "maze3.mz")),
                      path, (0, 0), (4, 4))


def test_cli_reports_out_of_range_goal(tmp_path):
    result = run_cli(tmp_path, "--goal", "9,9", str(REPO_ROOT / "maze1.mz"))
    assert "Goal position is out of range" in result.stdout
    assert not (tmp_path / "statistics.txt").exists()


def test_cli_reports_missing_file(tmp_path):
    result = run_cli(tmp_path, str(tmp_path / "nope.mz"))
    assert "File not found" in result.stdout
