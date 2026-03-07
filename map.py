# -*- coding: utf-8 -*-
"""
map.py — World grid construction, movement, and map rendering.

Grid convention: grid[y][x]
  y=0 is the top row, y=4 is the bottom row.
  x=0 is the left column, x=4 is the right column.
  Camp is at (x=2, y=2).

Movement:
  W = up    (y - 1)
  S = down  (y + 1)
  A = left  (x - 1)
  D = right (x + 1)
"""

from models import Tile, World, Player, TILE_SYMBOLS

# Pre-defined Amazon Rainforest layout.
# Each string is a tile_type used as the key into TILE_SYMBOLS.
GRID_LAYOUT: list = [
    ["Forest",       "Dense Jungle", "River",   "Dense Jungle", "Forest"],
    ["Dense Jungle", "Forest",       "River",   "Forest",       "Dense Jungle"],
    ["Clearing",     "Forest",       "Camp",    "Forest",       "Clearing"],
    ["Dense Jungle", "River",        "Forest",  "River",        "Dense Jungle"],
    ["Forest",       "Clearing",     "Forest",  "Clearing",     "Forest"],
]

# Direction -> (dx, dy)
_DIRECTION_MAP: dict = {
    "W": (0, -1),
    "S": (0,  1),
    "A": (-1, 0),
    "D": ( 1, 0),
}


def build_world() -> World:
    """Construct the 5x5 World from GRID_LAYOUT.
    Camp tile (2, 2) starts as explored. All others start unexplored.
    """
    grid = []
    for y, row in enumerate(GRID_LAYOUT):
        tile_row = []
        for x, tile_type in enumerate(row):
            explored = (x == 2 and y == 2)   # only camp starts revealed
            tile_row.append(Tile(tile_type=tile_type, explored=explored))
        grid.append(tile_row)
    return World(grid=grid)


def get_tile(world: World, x: int, y: int) -> Tile:
    """Return the Tile at column x, row y.  grid[y][x] ordering."""
    return world.grid[y][x]


def is_in_bounds(x: int, y: int, world: World) -> bool:
    """Return True if (x, y) is within the grid boundaries."""
    return 0 <= x < world.width and 0 <= y < world.height


def move(player: Player, world: World, direction: str) -> bool:
    """Attempt to move the player one step in direction ('W','A','S','D').

    Returns True on success (player position updated, tile marked explored).
    Returns False if the move would go out of bounds (player unchanged).
    Does NOT deduct food — engine.py handles that.
    """
    direction = direction.upper()
    if direction not in _DIRECTION_MAP:
        return False

    dx, dy = _DIRECTION_MAP[direction]
    new_x = player.x + dx
    new_y = player.y + dy

    if not is_in_bounds(new_x, new_y, world):
        return False

    player.x = new_x
    player.y = new_y
    world.grid[new_y][new_x].explored = True
    return True


def render_map(world: World, player: Player) -> str:
    """Return a multi-line string of the 5x5 grid, ready to print.

    Unexplored tiles show TILE_SYMBOLS["Unknown"].
    The player's current position shows player.avatar.
    Explored tiles show their tile-type symbol.
    """
    lines = []
    for y, row in enumerate(world.grid):
        cells = []
        for x, tile in enumerate(row):
            if x == player.x and y == player.y:
                cells.append(player.avatar)
            elif not tile.explored:
                cells.append(TILE_SYMBOLS["Unknown"])
            else:
                cells.append(TILE_SYMBOLS.get(tile.tile_type, "?"))
        lines.append("  ".join(cells))
    return "\n".join(lines)
