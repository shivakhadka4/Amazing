"""Terminal maze viewer (the subject's Terminal-ASCII visual).

Launched by a_maze_ing.py, or run on its own:
    python3 tui.py                 # reads config.txt
    python3 tui.py my_config.txt

Controls (typed at the menu):
    1  Re-generate a new maze
    2  Show / Hide the shortest path
    3  Rotate the wall colours
    4  Quit
"""

import sys
from typing import Any, Dict, Optional, Set

from config_parser import parse_config
from mazegen import MazeGenerator

RESET = "\033[0m"
WHITE = "\033[47m"
PATH_FG = "\033[34;47m"
LOGO = "\033[105m"
ENTRY = "\033[42m"
EXIT = "\033[41m"

WALL_PALETTE = ["30", "34", "31", "35", "90"]
STEP = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}

HEAVY = {
    (0, 0, 0, 0): " ",
    (0, 0, 1, 1): "━",
    (1, 1, 0, 0): "┃",
    (0, 1, 0, 1): "┏",
    (0, 1, 1, 0): "┓",
    (1, 0, 0, 1): "┗",
    (1, 0, 1, 0): "┛",
    (1, 1, 0, 1): "┣",
    (1, 1, 1, 0): "┫",
    (0, 1, 1, 1): "┳",
    (1, 0, 1, 1): "┻",
    (1, 1, 1, 1): "╋",
    (1, 0, 0, 0): "┃",
    (0, 1, 0, 0): "┃",
    (0, 0, 1, 0): "━",
    (0, 0, 0, 1): "━",
}
LIGHT = {
    (0, 0, 1, 1): "─",
    (1, 1, 0, 0): "│",
    (0, 1, 0, 1): "┌",
    (0, 1, 1, 0): "┐",
    (1, 0, 0, 1): "└",
    (1, 0, 1, 0): "┘",
    (1, 1, 0, 1): "├",
    (1, 1, 1, 0): "┤",
    (0, 1, 1, 1): "┬",
    (1, 0, 1, 1): "┴",
    (1, 1, 1, 1): "┼",
    (1, 0, 0, 0): "│",
    (0, 1, 0, 0): "│",
    (0, 0, 1, 0): "─",
    (0, 0, 0, 1): "─",
    (0, 0, 0, 0): " ",
}


def _fully(c: Dict[str, Any]) -> bool:
    return bool(c["N"] and c["E"] and c["S"] and c["W"])


def render(
        gen: MazeGenerator, show_path: bool = True, wall_fg: str = "30"
        ) -> str:
    grid = gen.get_grid()
    h, w = gen.height, gen.width
    rows, cols = 2 * h + 1, 2 * w + 1

    wall = [[False] * cols for _ in range(rows)]
    for y in range(h):
        for x in range(w):
            cell = grid[y][x]
            cy, cx = 2 * y + 1, 2 * x + 1
            for dr, dc in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
                wall[cy + dr][cx + dc] = True
            if cell["N"]:
                wall[cy - 1][cx] = True
            if cell["S"]:
                wall[cy + 1][cx] = True
            if cell["W"]:
                wall[cy][cx - 1] = True
            if cell["E"]:
                wall[cy][cx + 1] = True

    conn: Dict[Any, Set[str]] = {}
    if show_path:
        px, py = gen.entry
        for s in gen.get_solution():
            dx, dy = STEP[s]
            nx, ny = px + dx, py + dy
            conn.setdefault((px, py), set()).add(s)
            conn.setdefault((nx, ny), set()).add(
                {"N": "S", "S": "N", "E": "W", "W": "E"}[s]
            )
            px, py = nx, ny

    def is42(x: int, y: int) -> bool:
        return 0 <= x < w and 0 <= y < h and _fully(grid[y][x])

    wcol = "\033[" + wall_fg + ";47m"

    def heavy(r: int, c: int) -> str:
        up = wall[r - 1][c] if r > 0 else False
        dn = wall[r + 1][c] if r < rows - 1 else False
        lf = wall[r][c - 1] if c > 0 else False
        rt = wall[r][c + 1] if c < cols - 1 else False
        return wcol + HEAVY[(int(up), int(dn), int(lf), int(rt))] + RESET

    logo = LOGO + " " + RESET
    white = WHITE + " " + RESET

    def pathline(d: Set[str]) -> str:
        key = (int("N" in d), int("S" in d), int("W" in d), int("E" in d))
        return PATH_FG + LIGHT[key] + RESET

    out = []
    for r in range(rows):
        s = ""
        for c in range(cols):
            er, ec = (r % 2 == 0), (c % 2 == 0)
            x, y = c // 2, r // 2
            if er and ec:
                if wall[r][c]:
                    s += heavy(r, c)
                elif (
                    is42(x - 1, y - 1)
                    and is42(x, y - 1)
                    and is42(x - 1, y)
                    and is42(x, y)
                ):
                    s += logo
                else:
                    s += white
            elif er and not ec:
                uy, dyy = r // 2 - 1, r // 2
                if wall[r][c]:
                    if is42(x, uy) and is42(x, dyy):
                        s += logo * 3
                    else:
                        s += heavy(r, c) * 3
                else:
                    on = (x, uy) in conn and "S" in conn.get((x, uy), set())
                    mid = PATH_FG + "│" + RESET if on else white
                    s += white + mid + white
            elif not er and ec:
                lx, rx = c // 2 - 1, c // 2
                if wall[r][c]:
                    if is42(lx, y) and is42(rx, y):
                        s += logo
                    else:
                        s += heavy(r, c)
                else:
                    on = (lx, y) in conn and "E" in conn.get((lx, y), set())
                    s += PATH_FG + "─" + RESET if on else white
            else:
                if is42(x, y):
                    s += logo * 3
                elif (x, y) == gen.entry:
                    s += ENTRY + "   " + RESET
                elif (x, y) == gen.exit:
                    s += EXIT + "   " + RESET
                elif (x, y) in conn:
                    d = conn[(x, y)]
                    s += PATH_FG + "─" + RESET if "W" in d else white
                    s += pathline(d)
                    s += PATH_FG + "─" + RESET if "E" in d else white
                else:
                    s += white * 3
        out.append(s)
    return "\n".join(out)


def build_maze(
        config: Dict[str, Any], randomize: bool = False
        ) -> MazeGenerator:
    cfg = dict(config)
    if randomize:
        cfg["SEED"] = None
    gen = MazeGenerator.from_config(cfg)
    gen.generate()
    return gen


def run(
        config: Dict[str, Any], initial: Optional[MazeGenerator] = None
        ) -> None:
    gen = initial if initial is not None else build_maze(config)
    show_path = True
    wall_i = 0
    while True:
        print("\033[2J\033[H", end="")
        print(render(gen, show_path, WALL_PALETTE[wall_i]))
        print()
        print("=== A-Maze-ing ===")
        print("1. Re-generate a new maze")
        print("2. Show / Hide the shortest path")
        print("3. Rotate the wall colours")
        print("4. Quit")
        choice = input("Choice? (1-4): ").strip()
        if choice == "1":
            gen = build_maze(config, randomize=True)
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            wall_i = (wall_i + 1) % len(WALL_PALETTE)
        elif choice == "4":
            break


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "config.txt"
    run(parse_config(path))
