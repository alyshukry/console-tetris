import curses

from client.state.game import BoardState
from client.ui.colors import BORDER_PAIR, GAME_OVER_PAIR, GARBAGE_PAIR, PIECE_COLORS
from client.ui.curses import addstr_safe
from game.collision import get_ghost_row
from game.constants import SHAPES
from game.piece import Piece

CELL_WIDTH = 2
CELL = "██"
GHOST_CELL = "░░"
BOARD_GAP = 2
BOARD_TOP = 0  # row 0 is the latency, row 1 the "NEXT" label
NEXT_ROWS = 2  # tallest piece at rotation 0 is 2 cells high
NEXT_WIDTH = 4 * CELL_WIDTH  # the I piece is 4 cells wide, in characters


# ---------- sizes ----------


def board_size(board: BoardState) -> tuple[int, int]:
    """(height, width) in terminal characters, border included."""
    return board.height + 2, board.width * CELL_WIDTH + 2


def mini_size(board: BoardState) -> tuple[int, int]:
    """Same, for the small version (2 cells stacked per character)."""
    return (board.height + 1) // 2 + 2, board.width + 2


# ---------- shared helpers ----------


def cell_pair(board: BoardState, cell) -> int:
    if board.game_over:
        return GAME_OVER_PAIR
    return GARBAGE_PAIR if cell == "X" else PIECE_COLORS[cell]


def draw_frame(stdscr, row: int, col: int, height: int, width: int):
    pair = curses.color_pair(BORDER_PAIR)
    addstr_safe(stdscr, row, col, "▄" * width, pair)
    for r in range(1, height - 1):
        addstr_safe(stdscr, row + r, col, "█", pair)
        addstr_safe(stdscr, row + r, col + width - 1, "█", pair)
    addstr_safe(stdscr, row + height - 1, col, "▀" * width, pair)


# ---------- full-size board (mine) ----------


def draw_cell(stdscr, top, left, r, c, glyph, pair):
    """Draw one cell at board coords (r, c). top/left = board interior origin."""
    if r < 0:  # above the visible board
        return
    addstr_safe(stdscr, top + r, left + c * CELL_WIDTH, glyph, curses.color_pair(pair))


def draw_piece(stdscr, top, left, piece: Piece, row: int, glyph: str, pair: int):
    for dr, dc in SHAPES[piece.shape][piece.rot]:
        draw_cell(stdscr, top, left, row + dr, piece.col + dc, glyph, pair)


def draw_board(stdscr, board: BoardState, row: int, col: int):
    draw_frame(stdscr, row, col, *board_size(board))
    top, left = row + 1, col + 1  # interior origin

    # settled cells
    for r, line in enumerate(board.cells):
        for c, cell in enumerate(line):
            if cell in (0, None):
                continue
            draw_cell(stdscr, top, left, r, c, CELL, cell_pair(board, cell))

    # ghost, then the active piece on top
    piece = board.piece
    if board.game_over:
        pair = GAME_OVER_PAIR
    else:
        pair = PIECE_COLORS[piece.shape]
        ghost_row = piece.row + get_ghost_row(
            board.cells, piece, board.width, board.height
        )
        draw_piece(stdscr, top, left, piece, ghost_row, GHOST_CELL, pair)
    draw_piece(stdscr, top, left, piece, piece.row, CELL, pair)


def draw_next(stdscr, board: BoardState, row: int, col: int):
    addstr_safe(stdscr, row, col + 1, "NEXT")

    shape = board.next_piece.shape
    pair = curses.color_pair(GAME_OVER_PAIR if board.game_over else PIECE_COLORS[shape])
    cells = SHAPES[shape][0]

    # bounding box of the shape, so we can center it
    min_r = min(dr for dr, _ in cells)
    min_c = min(dc for _, dc in cells)
    height = max(dr for dr, _ in cells) - min_r + 1
    width = (max(dc for _, dc in cells) - min_c + 1) * CELL_WIDTH  # in characters

    top = row + 2 + (NEXT_ROWS - height) // 2
    left = col + (NEXT_WIDTH - width) // 2
    for dr, dc in cells:
        addstr_safe(
            stdscr,
            top + dr - min_r,
            left + (dc - min_c) * CELL_WIDTH,
            CELL,
            pair,
        )


# ---------- mini board (other players) ----------


def pair_grid(board: BoardState) -> list[list[int | None]]:
    """Color pair per cell (None = empty): settled cells plus the active piece."""
    grid = [
        [None if cell in (0, None) else cell_pair(board, cell) for cell in line]
        for line in board.cells
    ]
    piece = board.piece
    pair = GAME_OVER_PAIR if board.game_over else PIECE_COLORS[piece.shape]
    for dr, dc in SHAPES[piece.shape][piece.rot]:
        r, c = piece.row + dr, piece.col + dc
        if 0 <= r < board.height and 0 <= c < board.width:
            grid[r][c] = pair
    return grid


def draw_mini_board(stdscr, board: BoardState, row: int, col: int):
    draw_frame(stdscr, row, col, *mini_size(board))
    grid = pair_grid(board)
    empty = [None] * board.width

    # each terminal row shows two board rows: upper half ▀, lower half ▄
    for i in range(0, board.height, 2):
        upper = grid[i]
        lower = grid[i + 1] if i + 1 < board.height else empty
        for c in range(board.width):
            top, bottom = upper[c], lower[c]
            if top is None and bottom is None:
                continue
            if top is not None and bottom is not None:
                glyph = "█"
            elif top is not None:
                glyph = "▀"
            else:
                glyph = "▄"
            pair = top if top is not None else bottom
            addstr_safe(
                stdscr,
                row + 1 + i // 2,
                col + 1 + c,
                glyph,
                curses.color_pair(pair if pair is not None else 0),
            )
    addstr_safe(stdscr, mini_size(board)[0], col, board.username[:12])


# ---------- layout ----------


def draw_boards(stdscr, boards: dict[int, BoardState], my_id: int):
    _, screen_width = stdscr.getmaxyx()
    ordered = sorted(boards.items(), key=lambda item: item[0] != my_id)

    col = 1
    for player_id, board in ordered:
        if col >= screen_width:
            break
        if player_id == my_id:
            draw_next(stdscr, board, BOARD_TOP + 1, col)
            col += NEXT_WIDTH + BOARD_GAP
            draw_board(stdscr, board, BOARD_TOP, col)
            col += board_size(board)[1] + BOARD_GAP
        else:
            draw_mini_board(stdscr, board, BOARD_TOP, col)
            col += mini_size(board)[1] + BOARD_GAP
