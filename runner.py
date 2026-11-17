from typing import Tuple, Optional
from maze import get_walls, get_dimensions


def create_runner(x: int = 0, y: int = 0,
                  orientation: str = "N") -> list[int | str]:
    return [x, y, orientation]


def get_x(runner) -> int:
    return runner[0]


def get_y(runner) -> int:
    return runner[1]


def get_orientation(runner) -> str:
    return runner[2]


def turn(runner,
         direction: str) -> list[int, int, str]:
    compass_directions = ["N", "E", "S", "W"]
    orientation = get_orientation(runner)
    list_index = compass_directions.index(orientation)
    if direction.lower() == "left":
        list_index = (list_index - 1) % 4
    elif direction.lower() == "right":
        list_index = (list_index + 1) % 4
    runner[2] = compass_directions[list_index]
    return runner


def forward(runner) -> list[int, int, str]:
    orientation = get_orientation(runner)
    x_position = get_x(runner)
    y_position = get_y(runner)
    match orientation:
        case "N":
            runner[1] = y_position + 1
        case "E":
            runner[0] = x_position + 1
        case "S":
            runner[1] = y_position - 1
        case "W":
            runner[0] = x_position - 1
    return runner


def sense_walls(runner,
                maze) -> Tuple[bool, bool, bool]:
    compass_directions = ["N", "E", "S", "W"]
    orientation = get_orientation(runner)
    list_index = compass_directions.index(orientation)
    left = (list_index - 1) % 4
    right = (list_index + 1) % 4
    runner_x = get_x(runner)
    runner_y = get_y(runner)
    current_cell = get_walls(maze, runner_x, runner_y)
    return current_cell[left], current_cell[list_index], current_cell[right]


def go_straight(runner,
                maze) -> list[int, int, str]:
    wall_in_front = sense_walls(runner, maze)[1]
    if not wall_in_front:
        runner = forward(runner)
    else:
        raise ValueError
    return runner


def move(runner,
         maze) -> Tuple[list[int, int, str], str]:
    walls_detected = sense_walls(runner, maze)
    sequence = ""
    if not walls_detected[0]:
        sequence = sequence + "LF"
        runner = turn(runner, "left")
        runner = go_straight(runner, maze)
    elif not walls_detected[1]:
        sequence = sequence + "F"
        runner = go_straight(runner, maze)
    elif not walls_detected[2]:
        sequence = sequence + "RF"
        runner = turn(runner, "right")
        runner = go_straight(runner, maze)
    else:
        sequence = sequence + "RRF"
        runner = turn(runner, "right")
        runner = turn(runner, "right")
        runner = go_straight(runner, maze)
    return runner, sequence


def explore(runner, maze,
            goal: Optional[Tuple[int, int]] = None) -> str:
    total_moves = ""
    if goal is None:
        goal = get_dimensions(maze)
        goal = (goal[0] - 1, goal[1] - 1)
    while goal != (get_x(runner), get_y(runner)):
        movement = move(runner, maze)
        total_moves = total_moves + movement[1]
        print(display_maze(runner, maze))
    return total_moves

"""
Graphical display for the maze, 
displays the maze and the runners position in the maze
runner depicted by ^>v< depending on its orientation
will actively show runner solving maze showing each move 
by updating the runners position throughout program duration
not a real time animation but acts as a GUI
"""
def display_maze(runner, maze) -> str:
    display = []
    orientation = get_orientation(runner)
    x_position = get_x(runner)
    y_position = get_y(runner)
    runner_symbol = {"N": "^", "E": ">", "S": "v", "W": "<"}[orientation]
    for row_index, row in enumerate(maze):
        wall_line = "#"
        for cell in row:
            wall_line += "#" if cell["N"] else "."
            wall_line += "#"
        display.append(wall_line)
        path_line = "#"
        for col_index, cell in enumerate(row):
            if (col_index,
                len(maze) - row_index - 1) == (x_position,
                                               y_position):
                path_line += runner_symbol
            else:
                path_line += "."
            path_line += "#" if cell["E"] else "."
        display.append(path_line)
    bottom_border = "#" * (2 * len(maze[0]) + 1)
    display.append(bottom_border)
    gap = "-" * (2 * len(maze[0]) + 1)
    display.append(gap)
    return "\n".join(display)
