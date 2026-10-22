*This project has been created as part of the 42 curriculum by srouhi, shkhadka.*

# A-Maze-ing

A Python maze generator that reads a configuration file, builds a random (but reproducible) maze, writes it to a file in hexadecimal format, and shows it in an interactive viewer.

## Description

The goal of A-Maze-ing is to generate valid mazes from a simple `KEY=VALUE` config file, display them, and package the generation logic as a reusable Python module (`mazegen`) that can be installed with `pip` in future projects.

The generator supports two modes:

- **Perfect maze** (`PERFECT=True`): exactly one path between any two cells — no loops.
- **Playable board** (`PERFECT=False`): a Pac-Man-style board with loops, few dead-ends, and every corridor reachable.

In both modes, a **"42"** is drawn in the centre of the maze using fully closed cells. If the maze is too small to fit it (smaller than 9 × 7), the pattern is skipped and a warning is printed.

### Features

- Configurable size, entry, exit, output file and mode
- Reproducible generation with an optional `SEED`
- Shortest path solver (Breadth-First Search)
- Hexadecimal output file, checked with the provided `maze_analyzer.py`
- Two viewers:
  - **Graphical window** (tkinter) — opened by default by `a_maze_ing.py`
  - **Terminal ASCII viewer** (`tui.py`) with coloured walls
- Interactive controls: regenerate, show/hide path, change wall colour, quit

## Instructions

### Requirements

- Python 3.10 or newer
- `tkinter` (for the graphical viewer — included with most Python installs; on Debian/Ubuntu: `sudo apt install python3-tk`)
- `flake8` and `mypy` (only for linting)

### Installation

Install the `mazegen` package in editable mode:

```bash
make install        # same as: python3 -m pip install -e .
```

### Running

```bash
make run            # same as: python3 a_maze_ing.py config.txt
```

This generates the maze, writes it to `OUTPUT_FILE`, and opens the graphical viewer.

To use the terminal viewer instead:

```bash
python3 tui.py config.txt
```

### Controls

| Graphical viewer (`gui.py`) | Terminal viewer (`tui.py`) | Action |
|-----------------------------|----------------------------|--------|
| `R`                         | `1`                        | Re-generate a new maze |
| `Space` / `P`               | `2`                        | Show / hide the shortest path |
| `C`                         | `3`                        | Change the wall colour |
| `Esc` / `Q`                 | `4`                        | Quit |

### Checking the output

```bash
python3 maze_analyzer.py maze_output.txt
```

The analyzer checks that shared walls are coherent and reports whether the maze is perfect or a playable board.

### Other Makefile rules

| Command            | Description |
|--------------------|-------------|
| `make gui`         | Open the graphical viewer only |
| `make debug`       | Run the program under `pdb` |
| `make lint`        | Run `flake8` and `mypy` |
| `make lint-strict` | Run `flake8` and `mypy --strict` |
| `make clean`       | Remove caches and build files |

### Building the `mazegen` package

The reusable module is shipped as `mazegen-0.1.0-py3-none-any.whl` at the root of the repository. To rebuild it from source:

```bash
python3 -m venv venv
source venv/bin/activate
pip install build
python3 -m build            # creates dist/mazegen-0.1.0-py3-none-any.whl and .tar.gz
```

Install it in another project with:

```bash
pip install mazegen-0.1.0-py3-none-any.whl
```

## Configuration File Format

One `KEY=VALUE` pair per line. Lines starting with `#` are comments and are ignored. A default `config.txt` is included in the repository.

| Key           | Required | Description                          | Example                  |
|---------------|----------|--------------------------------------|--------------------------|
| `WIDTH`       | yes      | Number of columns                    | `WIDTH=20`               |
| `HEIGHT`      | yes      | Number of rows                       | `HEIGHT=15`              |
| `ENTRY`       | yes      | Entry cell `x,y`                     | `ENTRY=0,0`              |
| `EXIT`        | yes      | Exit cell `x,y`                      | `EXIT=19,14`             |
| `OUTPUT_FILE` | yes      | Output file name                     | `OUTPUT_FILE=maze_output.txt` |
| `PERFECT`     | yes      | `True` or `False`                    | `PERFECT=True`           |
| `SEED`        | no       | Seed for reproducible mazes          | `SEED=1337`              |

Coordinates start at `0,0` in the top-left corner. Entry and exit must be different and inside the maze.

Example (`config.txt`):

```
# A-Maze-ing default configuration
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze_output.txt
PERFECT=True
# SEED=1337
```

If the file is missing, a key is missing, or a value is invalid, the program prints a clear error message and exits instead of crashing.

## Output File Format

Each cell is written as **one hexadecimal digit**. Each bit is a wall, and a bit set to `1` means the wall is **closed**:

| Bit     | Value | Direction |
|---------|-------|-----------|
| 0 (LSB) | 1     | North     |
| 1       | 2     | East      |
| 2       | 4     | South     |
| 3       | 8     | West      |

Examples: `F` (1111) = all four walls closed (used for the "42" cells). `5` (0101) = North and South closed, East and West open — a horizontal corridor.

The file contains the grid row by row, then an empty line, then the entry, the exit, and the shortest path using `N`, `E`, `S`, `W`:

```
D55395513D5139551153
D53AC796C396AE93AC3A
...

0,0
19,14
EEESSSWWWSEEESEESWSS...
```

## Maze Generation Algorithm

We use the **Recursive Backtracker** (implemented iteratively, as a depth-first search with a stack):

1. Start with a grid where every cell has all four walls closed.
2. Place the "42" pattern in the centre and mark those cells as visited, so the algorithm carves around them.
3. Mark the starting cell as visited and push it on the stack.
4. While the stack is not empty:
   - Look at the cell on top of the stack and list its unvisited neighbours.
   - If there is at least one, pick one at random, remove the wall between the two cells, mark it visited and push it.
   - Otherwise, pop the stack (backtrack).

The result is a **perfect maze** (a spanning tree of the grid).

When `PERFECT=False`, two extra steps turn it into a playable board:

- **Braiding:** dead-ends are opened into a neighbouring corridor, which creates loops. A wall is not removed if it would create a 3×3 open area.
- **Connectivity check:** a BFS from the entry makes sure every non-"42" cell is reachable; any isolated cell is connected.

The shortest path from entry to exit is found with **Breadth-First Search**.

## Why the Recursive Backtracker?

- It produces long, winding corridors with few branches, which makes mazes interesting to solve and nice to look at.
- It always visits every reachable cell, so the maze is fully connected.
- It naturally creates a perfect maze, which is exactly what `PERFECT=True` needs. Loops can then be added on top for the playable mode.
- It is simple to implement and to explain, and the iterative version avoids Python's recursion limit on large mazes.

## Code Reusability

All generation logic lives in the `mazegen` package (`mazegen/generator.py`) as a single class, `MazeGenerator`. It does not depend on the config file, the output file or the viewers, so it can be imported in any project.

### Basic usage

```python
from mazegen import MazeGenerator

gen = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit=(19, 14),
    perfect=True,
    seed=42,
)
gen.generate()

grid = gen.get_grid()        # the maze structure
path = gen.get_solution()    # shortest path, e.g. "EESENEEESE..."

print(grid[0][0])            # {'N': True, 'E': False, 'S': True, 'W': True, 'visited': True}
print(path)
```

You can also build it from a parsed config dictionary:

```python
gen = MazeGenerator.from_config(config)
```

### Parameters

| Parameter     | Type                   | Default             | Description |
|---------------|------------------------|---------------------|-------------|
| `width`       | `int`                  | —                   | Number of columns |
| `height`      | `int`                  | —                   | Number of rows |
| `entry`       | `tuple[int, int]`      | —                   | Entry cell `(x, y)` |
| `exit`        | `tuple[int, int]`      | —                   | Exit cell `(x, y)` |
| `perfect`     | `bool`                 | `False`             | `True` = no loops |
| `output_file` | `str`                  | `"maze_output.txt"` | Used by `save_to_file()` |
| `seed`        | `int \| None`          | `None`              | Same seed → same maze |

### Accessing the result

| Method / attribute | Returns | Description |
|--------------------|---------|-------------|
| `generate()`       | `None`  | Builds the maze |
| `get_grid()`       | `list[list[dict]]` | `grid[y][x]` is a dict with `"N"`, `"E"`, `"S"`, `"W"` → `True` if the wall is closed |
| `get_solution()`   | `str`   | Shortest path from entry to exit (`N`/`E`/`S`/`W`) |
| `save_to_file()`   | `None`  | Writes the hex grid to `output_file` |
| `width`, `height`, `entry`, `exit` | | The values you passed in |

## Team & Project Management

### Roles

- **srouhi:** core maze generation algorithm, shortest path solver (BFS), output file format.
- **shkhadka:** visual rendering (graphical and terminal viewers), colour themes, configuration parser, and the `mazegen` package structure.

### Planning and how it evolved

- **Initial plan:** config parser and core generator first, then the BFS solver and output file, then the viewer, and finally the pip-installable package.
- **How it evolved:** <!-- TODO: write what really changed. E.g. "We first built only the terminal viewer, then added a tkinter window", "The PERFECT=False mode took longer than planned because of the no-3x3 rule and dead-ends", etc. -->

### What worked well

- Splitting the work into backend (generator, solver, output) and frontend (parser, viewers) let us work in parallel.
- Keeping `MazeGenerator` independent from the rest of the app made packaging easy.
- Using `maze_analyzer.py` early helped us catch wall-coherence bugs.

### What could be improved

- Add more generation algorithms (e.g. Prim's or Kruskal's).
- Animate the generation step by step.
- Reach zero dead-ends in playable mode (the "braided" bonus).
- More unit tests (`test_maze.py`) and stricter validation of config values.

### Tools used

- Python 3.10+, `tkinter`
- `flake8` and `mypy` for linting and type checking
- `pytest` for tests (`test_maze.py`)
- `pdb` for debugging
- `setuptools` / `build` for packaging
- Git for version control

## Resources

- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Jamis Buck — Maze Generation: Recursive Backtracking](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking)
- [Spanning tree — Wikipedia](https://en.wikipedia.org/wiki/Spanning_tree)
- [Breadth-first search — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Python Packaging User Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [tkinter documentation](https://docs.python.org/3/library/tkinter.html)

### AI usage

AI tools were used for:

- **Learning:** understanding maze generation algorithms and how perfect mazes relate to spanning trees.
- **Architecture:** brainstorming how to split the project into modules.
- **Debugging and review:** finding bugs in wall removal and the connectivity check. <!-- TODO: name the exact parts -->
- **Documentation:** improving the structure and wording of this README.

All AI suggestions were reviewed, tested and understood by both team members before being used.
