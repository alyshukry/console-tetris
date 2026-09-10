from .constants import SHAPES

def fits(cells, piece, width, height, drow, dcol, rot=None) -> bool:
    rot = piece["rot"] if rot is None else rot
    for dr, dc in SHAPES[piece["shape"]][rot]:
        row = piece["row"] + dr + drow
        col = piece["col"] + dc + dcol
        if col < 0 or col >= width or row >= height:
            return False
        if row < 0:
            continue
        if cells[row][col] != 0:
            return False
    return True

def get_ghost_row(cells, piece, width, height) -> int:
    ghost_row = 0
    while fits(cells, piece, width, height, ghost_row + 1, 0):
        ghost_row += 1
    return ghost_row