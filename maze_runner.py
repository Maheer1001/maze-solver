import argparse
from typing import List, Tuple, Optional, Dict
from runner import create_runner, display_maze, get_x, get_y, move
from maze import get_dimensions
runner_path = []


def csv_writing(path: List[Tuple[int, int]],
                sequence: str) -> None:
    with open("exploration.csv", 'w') as file:
        file.write("Step,x-coordinate,y-coordinate,Actions\n")
        actions = []
        current_action = ""
        for action in sequence:
            current_action += str(action)
            if action == "F":
                actions.append(current_action)
                current_action = ""
        for i in range(len(actions)):
            file.write(f"{i + 1},{path[i][0]},{path[i][1]},{actions[i]}\n")
    return None


def txt_writing(maze_name: str, path: List[Tuple[int, int]],
                shortest_path_found: List[Tuple[int, int]]) -> None:
    exploration_steps = len(path) - 1
    path_length = len(shortest_path_found)
    score = exploration_steps / 4 + path_length
    with open("statistics.txt", 'w') as file:
        file.write(f"Input file name: {maze_name}\n")
        file.write(f"Score: {score}\n")
        file.write(f"Exploration steps: {exploration_steps}\n")
        file.write(f"Shortest path: {shortest_path_found}\n")
        file.write(f"Shortest path length: {path_length}\n")
    return None


def shortest_path(maze, starting: Optional[Tuple[int, int]] = None,
                  goal: Optional[Tuple[int, int]] = None) \
                  -> List[Tuple[int, int]]:
    global runner_path
    runner_path = []
    total_moves = ""
    if starting is None:
        starting = (0, 0)
    if goal is None:
        goal = get_dimensions(maze)
        goal = (goal[0] - 1, goal[1] - 1)
    runner = create_runner(starting[0], starting[1])
    print(display_maze(runner, maze))
    while goal != (get_x(runner), get_y(runner)):
        runner_path.append((get_x(runner), get_y(runner)))
        movement = move(runner, maze)
        total_moves = total_moves + movement[1]
        print(display_maze(runner, maze))
    csv_writing(runner_path, total_moves)
    runner_path.append(goal)
    seen = []
    optimised_path = []
    for item in runner_path:
        if item in seen:
            start_index = optimised_path.index(item)
            optimised_path = optimised_path[:start_index + 1]
        else:
            optimised_path.append(item)
            seen.append(item)
    print(optimised_path)
    return optimised_path


def str_to_list(maze_str: str) -> List[List[Dict[str, bool]]]:
    lines = maze_str.splitlines()
    height = (len(lines) - 1) // 2
    width = (len(lines[0]) - 1) // 2
    maze = []
    for row_index in range(height):
        row = []
        for col_index in range(width):
            cell = {
                "N": lines[row_index * 2][col_index * 2 + 1] == "#",
                "E": lines[row_index * 2 + 1][col_index * 2 + 2] == "#",
                "S": lines[row_index * 2 + 2][col_index * 2 + 1] == "#",
                "W": lines[row_index * 2 + 1][col_index * 2] == "#",
            }
            row.append(cell)
        maze.append(row)
    return maze


def maze_reader(maze_file: str) -> List[List[Dict[str, bool]]]:
    try:
        lines = []
        with open(maze_file, 'r') as file:
            for line in file:
                lines.append(line.rstrip('\n'))
        if len(lines) < 3 or len(lines[0]) < 3:
            raise ValueError("Maze too small")
        width = len(lines[0])
        if lines[0] != '#' * width or lines[-1] != '#' * width:
            raise ValueError("Maze not encapsulated")
        for line in lines:
            if len(line) != width or line[0] != '#' or line[-1] != '#':
                raise ValueError("Invalid row")
            for cell in range(1, width - 1):
                if line[cell] not in ('.', '#'):
                    raise ValueError("Invalid cell")
        maze = "\n".join(lines)
        return str_to_list(maze)
    except OSError:
        raise IOError(" ")


def input_validation(maze: List[List[Dict[str, bool]]],
                     start: Tuple[int, int], goal: Tuple[int, int]) -> None:
    maze_bounds = get_dimensions(maze)
    cord_bounds = (maze_bounds[0] - 1, maze_bounds[1] - 1)
    plane = ["x", "y"]
    errors = []
    for i in range(2):
        axis = plane[i]
        if goal[i] > cord_bounds[i]:
            errors.append(f"Goal position is out of range of the maze: "
                          f"{axis} input too big.")
        if start[i] > cord_bounds[i]:
            errors.append(f"Start position is out of range of the maze: "
                          f"{axis} input too big.")
    if errors:
        raise ValueError("\n".join(errors))
    return None


def main():
    parser = (argparse.ArgumentParser
              (description="ECS Maze Runner"))
    try:
        parser.add_argument("--starting", type=str,
                            help="The starting position, e.g., '2, 1'")
        parser.add_argument("--goal", type=str,
                            help="The goal position, e.g., '4, 5'")
        parser.add_argument("maze", type=str,
                            help="The name of the maze file, e.g., maze1.mz")
        args = parser.parse_args()
        for arg in [args.starting, args.goal]:
            if arg is not None:
                if len(arg.replace(" ", "").replace(",", "")) > 2:
                    raise ValueError("Input must be in the format 'x,y'"
                                     "where they are positive integers")
                if not arg.replace(" ", "").replace(",", "").isdigit():
                    raise ValueError("Input must be in the format 'x,y' "
                                     "where they are positive integers")
    except ValueError as e:
        print(f"Not a valid input type: {e}")
        return
    try:
        maze = maze_reader(args.maze)
    except IOError:
        print("IOError: File not found")
        return
    if args.starting is not None:
        starting = tuple(map(int, args.starting.split(',')))
    else:
        starting = (0, 0)
    if args.goal is not None:
        goal = tuple(map(int, args.goal.split(',')))
    else:
        maze_bounds = get_dimensions(maze)
        goal = (maze_bounds[0] - 1, maze_bounds[1] - 1)
    try:
        input_validation(maze, starting, goal)
    except ValueError as e:
        print(f"Errors:\n{e}")
        return None
    optimised_path = shortest_path(maze, starting, goal)
    txt_writing(args.maze, runner_path, optimised_path)


if __name__ == "__main__":
    main()


