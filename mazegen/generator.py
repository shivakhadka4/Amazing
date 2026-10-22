import random
from collections import deque
from typing import Dict, Any, List, Tuple, Optional


class MazeGenerator:
    """Generate a maze and (optionally) solve it.

    This class is the reusable core of the project. It knows nothing about
    config files or the rest of the app — you give it plain parameters and
    it gives you back the maze structure and a solution path. That makes it
    safe to import into any future project.

    Two ways to create one:

        # 1) Directly, with your own parameters:
        gen = MazeGenerator(width=20, height=15, entry=(0, 0),
                            exit=(19, 14), perfect=True, seed=42)

        # 2) From a parsed config dict (used by this project's main.py):
        gen = MazeGenerator.from_config(config)

    Then:

        gen.generate()             # builds the maze
        grid = gen.get_grid()      # the maze structure
        path = gen.get_solution()  # e.g. "SSEESSW..." (shortest path)
        gen.save_to_file()         # optional: write it to OUTPUT_FILE
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit: Tuple[int, int],
        perfect: bool = False,
        output_file: str = "maze_output.txt",
        seed: Optional[int] = None,
    ) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.perfect = perfect
        self.output_file = output_file
        self.seed = seed

        if self.seed is not None:
            random.seed(self.seed)

        self.grid = [
            [
                {"N": True, "E": True, "S": True, "W": True, "visited": False}
                for _ in range(self.width)
            ]
            for _ in range(self.height)
        ]
        self.solution: Optional[str] = None
        self._pattern: set[Tuple[int, int]] = set()

        self._apply_42_pattern()

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "MazeGenerator":
        """Build a MazeGenerator from a parsed config dict.

        See config_parser for the dict shape.
        """
        return cls(
            width=config["WIDTH"],
            height=config["HEIGHT"],
            entry=config["ENTRY"],
            exit=config["EXIT"],
            perfect=config["PERFECT"],
            output_file=config["OUTPUT_FILE"],
            seed=config.get("SEED", None),
        )

    def get_grid(self) -> List[List[Dict[str, Any]]]:
        """Return the maze structure (call generate() first)."""
        return self.grid

    def get_solution(self) -> str:
        """Return the shortest-path solution (computed once, then cached)."""
        if self.solution is None:
            self.solution = self.solve_shortest_path()
        return self.solution

    def _apply_42_pattern(self) -> None:
        # The "42" is drawn by fully-closed cells (1 = a closed wall cell).
        bitmap = [
            "1010111",
            "1010001",
            "1110111",
            "0010100",
            "0010111",
        ]
        ph = len(bitmap)
        pw = len(bitmap[0])
        if self.width < pw + 2 or self.height < ph + 2:
            print("Warning: Maze size is too small to fit the '42' pattern.")
            return

        start_x = (self.width - pw) // 2
        start_y = (self.height - ph) // 2
        for row in range(ph):
            for col in range(pw):
                if bitmap[row][col] == "1":
                    cell = self.grid[start_y + row][start_x + col]
                    cell["N"] = True
                    cell["E"] = True
                    cell["S"] = True
                    cell["W"] = True
                    # mark visited so generate() carves *around* it,
                    # leaving these cells fully closed to form the "42"
                    cell["visited"] = True
                    self._pattern.add((start_x + col, start_y + row))

    def generate(self) -> None:
        stack = []
        start_x, start_y = 0, 0
        self.grid[start_y][start_x]["visited"] = True
        stack.append((start_x, start_y))

        while stack:
            cx, cy = stack[-1]
            neighbors = self._get_Unvisited_neighbors(cx, cy)

            if neighbors:
                nx, ny, direction = random.choice(neighbors)
                self._remove_walls(cx, cy, nx, ny, direction)
                self.grid[ny][nx]["visited"] = True
                stack.append((nx, ny))
            else:
                stack.pop()

        if not self.perfect:
            self._create_loops()

    def _get_Unvisited_neighbors(
            self, x: int, y: int
            ) -> List[Tuple[int, int, str]]:
        neighbors = []
        directions = [
            (0, -1, "N", "S"),
            (1, 0, "E", "W"),
            (0, 1, "S", "N"),
            (-1, 0, "W", "E"),
        ]

        for dx, dy, diri, _ in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if not self.grid[ny][nx]["visited"]:
                    neighbors.append((nx, ny, diri))

        return neighbors

    def _remove_walls(
            self, x1: int, y1: int, x2: int, y2: int, direction: str
            ) -> None:
        if direction == "N":
            self.grid[y1][x1]["N"] = False
            self.grid[y2][x2]["S"] = False
        elif direction == "S":
            self.grid[y1][x1]["S"] = False
            self.grid[y2][x2]["N"] = False
        elif direction == "E":
            self.grid[y1][x1]["E"] = False
            self.grid[y2][x2]["W"] = False
        elif direction == "W":
            self.grid[y1][x1]["W"] = False
            self.grid[y2][x2]["E"] = False

    _DIRS = [(0, -1, "N"), (1, 0, "E"), (0, 1, "S"), (-1, 0, "W")]

    def _neighbours(self, x: int, y: int) -> List[Tuple[int, int, str]]:
        out = []
        for dx, dy, d in self._DIRS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                out.append((nx, ny, d))
        return out

    def _open_sides(self, x: int, y: int) -> List[str]:
        return [d for d in ("N", "E", "S", "W") if not self.grid[y][x][d]]

    def _add_walls(
            self, x1: int, y1: int, x2: int, y2: int, direction: str
            ) -> None:
        if direction == "N":
            self.grid[y1][x1]["N"] = True
            self.grid[y2][x2]["S"] = True
        elif direction == "S":
            self.grid[y1][x1]["S"] = True
            self.grid[y2][x2]["N"] = True
        elif direction == "E":
            self.grid[y1][x1]["E"] = True
            self.grid[y2][x2]["W"] = True
        elif direction == "W":
            self.grid[y1][x1]["W"] = True
            self.grid[y2][x2]["E"] = True

    def _block_open(self, bx: int, by: int) -> bool:
        for j in range(by, by + 3):
            for i in range(bx, bx + 3):
                if (i, j) in self._pattern:
                    return False
        for j in range(by, by + 3):
            for i in range(bx, bx + 3):
                c = self.grid[j][i]
                if i < bx + 2 and c["E"]:
                    return False
                if j < by + 2 and c["S"]:
                    return False
        return True

    def _creates_3x3_near(self, x: int, y: int) -> bool:
        for by in range(max(0, y - 2), min(self.height - 3, y) + 1):
            for bx in range(max(0, x - 2), min(self.width - 3, x) + 1):
                if self._block_open(bx, by):
                    return True
        return False

    def _reachable(self) -> set[Tuple[int, int]]:
        start = self.entry
        if start in self._pattern:
            return set()
        seen = {start}
        queue = deque([start])
        while queue:
            x, y = queue.popleft()
            for nx, ny, d in self._neighbours(x, y):
                if (nx, ny) in self._pattern:
                    continue
                if not self.grid[y][x][d] and (nx, ny) not in seen:
                    seen.add((nx, ny))
                    queue.append((nx, ny))
        return seen

    def _braid(self) -> None:
        # Remove dead-ends (cells with <=1 opening) by opening another wall,
        # which turns the single-path maze into a looped, playable board.
        cells = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if (x, y) not in self._pattern
        ]
        random.shuffle(cells)
        for x, y in cells:
            if len(self._open_sides(x, y)) > 1:
                continue
            cands = [
                (nx, ny, d)
                for nx, ny, d in self._neighbours(x, y)
                if (nx, ny) not in self._pattern and self.grid[y][x][d]
            ]
            random.shuffle(cands)
            for nx, ny, d in cands:
                self._remove_walls(x, y, nx, ny, d)
                if self._creates_3x3_near(x, y):
                    self._add_walls(x, y, nx, ny, d)
                else:
                    break

    def _connect_all(self) -> None:
        # Make sure every non-"42" cell is reachable from the entry.
        for _ in range(self.width * self.height):
            reach = self._reachable()
            target = None
            for y in range(self.height):
                for x in range(self.width):
                    if (x, y) not in self._pattern and (x, y) not in reach:
                        target = (x, y)
                        break
                if target:
                    break
            if target is None:
                return
            x, y = target
            prefer = [
                (nx, ny, d)
                for nx, ny, d in self._neighbours(x, y)
                if (nx, ny) not in self._pattern
                and (nx, ny) in reach
                and self.grid[y][x][d]
            ]
            other = [
                (nx, ny, d)
                for nx, ny, d in self._neighbours(x, y)
                if (nx, ny) not in self._pattern and self.grid[y][x][d]
            ]
            pick = prefer or other
            if not pick:
                return
            nx, ny, d = random.choice(pick)
            self._remove_walls(x, y, nx, ny, d)

    def _create_loops(self) -> None:
        self._braid()
        self._connect_all()

    def solve_shortest_path(self) -> str:
        queue = deque([(self.entry[0], self.entry[1], "")])
        visited = {self.entry}

        while queue:
            x, y, path = queue.popleft()

            if (x, y) == self.exit:
                return path

            directions = [
                (0, -1, "N", "N"),
                (1, 0, "E", "E"),
                (0, 1, "S", "S"),
                (-1, 0, "W", "W"),
            ]

            for dx, dy, diri, char in directions:
                if not self.grid[y][x][diri]:
                    nx, ny = x + dx, y + dy
                    if (
                        0 <= nx < self.width
                        and 0 <= ny < self.height
                        and (nx, ny) not in visited
                    ):
                        visited.add((nx, ny))
                        queue.append((nx, ny, path + char))

        return ""

    def save_to_file(self) -> None:
        with open(self.output_file, "w", encoding="utf-8") as f:
            for y in range(self.height):
                row_hex = []
                for x in range(self.width):
                    cell = self.grid[y][x]
                    val = (
                        (1 if cell["N"] else 0) << 0
                        | (1 if cell["E"] else 0) << 1
                        | (1 if cell["S"] else 0) << 2
                        | (1 if cell["W"] else 0) << 3
                    )
                    row_hex.append(format(val, "X"))
                f.write("".join(row_hex) + "\n")
