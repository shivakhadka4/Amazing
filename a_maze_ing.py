"""A-Maze-ing — main program.

Usage:
    python3 a_maze_ing.py config.txt

Reads the config, generates the maze, writes the output file, and opens
the graphical viewer.
"""

import sys
from config_parser import parse_config
from mazegen import MazeGenerator
import tui


def write_output(gen: MazeGenerator, path: str) -> None:
    """Write the maze in the subject's format:
    the hex grid, a blank line, then entry, exit and the shortest path."""
    grid = gen.get_grid()
    lines = []
    for y in range(gen.height):
        row = ""
        for x in range(gen.width):
            c = grid[y][x]
            val = (
                (1 if c["N"] else 0) << 0
                | (1 if c["E"] else 0) << 1
                | (1 if c["S"] else 0) << 2
                | (1 if c["W"] else 0) << 3
            )
            row += format(val, "X")
        lines.append(row)
    lines.append("")  # blank line
    lines.append(f"{gen.entry[0]},{gen.entry[1]}")  # entry x,y
    lines.append(f"{gen.exit[0]},{gen.exit[1]}")  # exit x,y
    lines.append(gen.get_solution())  # shortest path N/E/S/W
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        sys.exit(1)
    try:
        config = parse_config(sys.argv[1])
        gen = MazeGenerator.from_config(config)
        gen.generate()
        write_output(gen, config["OUTPUT_FILE"])
        print(f"Maze saved to {config['OUTPUT_FILE']}")
        tui.run(config, initial=gen)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
