from mazegen import MazeGenerator


def test_grid_dimensions() -> None:
    gen = MazeGenerator(
        width=10, height=8, entry=(0, 0), exit=(9, 7), perfect=True, seed=42
    )
    gen.generate()
    grid = gen.get_grid()

    assert len(grid) == 8  # 8 rows
    assert len(grid[0]) == 10  # 10 columns in the first row


def test_same_seed_same_maze() -> None:
    gen1 = MazeGenerator(
        width=10, height=8, entry=(0, 0), exit=(9, 7), perfect=True, seed=42
    )
    gen1.generate()

    gen2 = MazeGenerator(
        width=10, height=8, entry=(0, 0), exit=(9, 7), perfect=True, seed=42
    )
    gen2.generate()

    assert gen1.get_solution() == gen2.get_solution()


def test_wall_coherence() -> None:
    gen = MazeGenerator(
        width=10, height=8, entry=(0, 0), exit=(9, 7), perfect=True, seed=42
    )
    gen.generate()
    grid = gen.get_grid()

    for y in range(gen.height):
        for x in range(gen.width):
            cell = grid[y][x]
            if not cell["E"]:  # this cell open to the east?
                assert not grid[y][x + 1]["W"]  # right neighbour open west
            if not cell["S"]:  # this cell open to the south?
                assert not grid[y + 1][x]["N"]  # neighbour below open north


def test_perfect_maze_has_no_loops() -> None:
    gen = MazeGenerator(
        width=10, height=8, entry=(0, 0), exit=(9, 7), perfect=True, seed=42
    )
    gen.generate()
    grid = gen.get_grid()

    passages = 0
    for y in range(gen.height):
        for x in range(gen.width):
            if not grid[y][x]["E"]:  # open to the east = one passage
                passages += 1
            if not grid[y][x]["S"]:  # open to the south = one passage
                passages += 1

    cells = gen.width * gen.height  # N
    assert passages == cells - 1  # a perfect maze has exactly N-1
