"""Graphical maze viewer (tkinter window).

Launched by a_maze_ing.py, or run on its own:
    python3 gui.py                 # reads config.txt
    python3 gui.py my_config.txt

Controls:
    R          new maze
    Space / P  show / hide the path
    C          change the wall colour
    Esc / Q    quit
"""

import sys
import tkinter as tk
from typing import Any, Dict, Optional
from config_parser import parse_config
from mazegen import MazeGenerator

CELL = 28
PAD = 20

FOUR_COLOR = "purple"  # the "4"
TWO_COLOR = "purple"  # the "2"
WALL_PALETTE = ["blue", "green", "orange", "white", "magenta"]

STEP = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}


def build_maze(
        config: Dict[str, Any], randomize: bool = False
        ) -> MazeGenerator:
    cfg = dict(config)
    if randomize:
        cfg["SEED"] = None
    gen = MazeGenerator.from_config(cfg)
    gen.generate()
    return gen


def print_menu() -> None:
    print("\n=== A-Maze-ing ===")
    print("R      : Re-generate a new maze")
    print("Space  : Show / Hide the shortest path")
    print("C      : Change the wall colour")
    print("Esc/Q  : Quit")


def run(
        config: Dict[str, Any], initial: Optional[MazeGenerator] = None
        ) -> None:
    state: Dict[str, Any] = {
        "gen": initial if initial is not None else build_maze(config),
        "show_path": True,
        "wall_i": 0,
    }

    gen0 = state["gen"]
    width_px = gen0.width * CELL + 2 * PAD
    height_px = gen0.height * CELL + 2 * PAD + 24

    root = tk.Tk()
    root.title("My Maze Viewer")
    canvas = tk.Canvas(root, width=width_px, height=height_px, bg="black")
    canvas.pack()

    def draw() -> None:
        canvas.delete("all")
        gen = state["gen"]
        grid = gen.get_grid()
        wall_color = WALL_PALETTE[state["wall_i"]]

        for y in range(gen.height):
            for x in range(gen.width):
                c = grid[y][x]
                if c["N"] and c["E"] and c["S"] and c["W"]:
                    color = FOUR_COLOR if x < gen.width // 2 else TWO_COLOR
                    x0 = PAD + x * CELL
                    y0 = PAD + y * CELL
                    canvas.create_rectangle(
                        x0, y0, x0 + CELL, y0 + CELL, fill=color, outline=""
                    )

        for (cx, cy), color in ((gen.entry, "green"), (gen.exit, "red")):
            x0 = PAD + cx * CELL
            y0 = PAD + cy * CELL
            canvas.create_rectangle(
                x0, y0, x0 + CELL, y0 + CELL, fill=color, outline=""
            )

        for y in range(gen.height):
            for x in range(gen.width):
                cell = grid[y][x]
                x0 = PAD + x * CELL
                y0 = PAD + y * CELL
                x1 = x0 + CELL
                y1 = y0 + CELL
                if cell["N"]:
                    canvas.create_line(
                        x0, y0, x1, y0, fill=wall_color, width=3
                        )
                if cell["S"]:
                    canvas.create_line(
                        x0, y1, x1, y1, fill=wall_color, width=3
                        )
                if cell["W"]:
                    canvas.create_line(
                        x0, y0, x0, y1, fill=wall_color, width=3
                        )
                if cell["E"]:
                    canvas.create_line(
                        x1, y0, x1, y1, fill=wall_color, width=3
                        )

        if state["show_path"]:
            solution = gen.get_solution()
            if solution:
                x, y = gen.entry
                pts = [(
                    PAD + x * CELL + CELL // 2, PAD + y * CELL + CELL // 2
                    )]
                for step in solution:
                    dx, dy = STEP[step]
                    x, y = x + dx, y + dy
                    pts.append((
                        PAD + x * CELL + CELL // 2, PAD + y * CELL + CELL // 2
                        ))
                flat = [n for p in pts for n in p]
                canvas.create_line(*flat, fill="red", width=4)

        canvas.create_text(
            PAD,
            height_px - 12,
            anchor="w",
            fill="white",
            text="R: new maze"
                 "    Space: show/hide path    C: wall colour    Esc: quit",
        )

    def regenerate(event: Any) -> None:
        state["gen"] = build_maze(config, randomize=True)
        print("New maze generated.")
        draw()

    def toggle_path(event: Any) -> None:
        state["show_path"] = not state["show_path"]
        print("Path shown." if state["show_path"] else "Path hidden.")
        draw()

    def cycle_colour(event: Any) -> None:
        state["wall_i"] = (state["wall_i"] + 1) % len(WALL_PALETTE)
        print("Wall colour:", WALL_PALETTE[state["wall_i"]])
        draw()

    root.bind("<r>", regenerate)
    root.bind("<space>", toggle_path)
    root.bind("<p>", toggle_path)
    root.bind("<c>", cycle_colour)
    root.bind("<Escape>", lambda e: root.destroy())
    root.bind("<q>", lambda e: root.destroy())

    print_menu()
    draw()
    root.mainloop()


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "config.txt"
    run(parse_config(path))
