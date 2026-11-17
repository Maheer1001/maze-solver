from typing import List, Tuple, Dict


def create_maze(width: int = 5,
                height: int = 5) -> List[List[Dict[str, bool]]]:
    maze = []
    for _ in range(height):
        cell = []
        for _ in range(width):
            cell.append({"N": False, "E": False, "S": False, "W": False})
        maze.append(cell)
    for x in range(width):
        maze[0][x]["N"] = True  # Top row
        maze[height - 1][x]["S"] = True  # Bottom row
    for y in range(height):
        maze[y][0]["W"] = True  # Left column
        maze[y][width - 1]["E"] = True  # Right column
    return maze


def add_horizontal_wall(maze: List[List[Dict[str, bool]]],
                        x_coordinate: int,
                        horizontal_line: int) -> List[List[Dict[str, bool]]]:
    height = len(maze)
    maze[height - horizontal_line - 1][x_coordinate]["S"] = True
    maze[height-horizontal_line][x_coordinate]["N"] = True
    return maze


def add_vertical_wall(maze: List[List[Dict[str, bool]]],
                      y_coordinate: int,
                      vertical_line: int) -> List[List[Dict[str, bool]]]:
    height = len(maze)
    maze[height - y_coordinate - 1][vertical_line - 1]["E"] = True
    maze[height - y_coordinate - 1][vertical_line]["W"] = True
    return maze


def get_dimensions(maze: List[List[Dict[str, bool]]]) -> Tuple[int, int]:
    height = len(maze)
    width = len(maze[0])
    return width, height


def get_walls(maze: List[List[Dict[str, bool]]],
              x_coordinate: int,
              y_coordinate: int) -> Tuple[bool, bool, bool, bool]:
    height = len(maze)
    cell = maze[height - y_coordinate - 1][x_coordinate]
    return cell["N"], cell["E"], cell["S"], cell["W"]
