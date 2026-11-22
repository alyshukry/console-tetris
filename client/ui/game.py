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
ROW_GAP = 0
NEXT_ROWS = 2  # tallest piece at rotation 0 is 2 cells high
NEXT_WIDTH = 4 * CELL_WIDTH  # the I piece is 4 cells wide, in characters


def board_size(board: BoardState) -> tuple[int, int]:
    return board.height + 2, board.width * CELL_WIDTH + 2


def mini_size(board: BoardState) -> tuple[int, int]:
    return (board.height + 1) // 2 + 2, board.width + 2


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


def draw_cell(stdscr, top, left, r, c, glyph, pair):
    if r < 0:  # above the visible board
        return
    addstr_safe(stdscr, top + r, left + c * CELL_WIDTH, glyph, curses.color_pair(pair))


def draw_piece(stdscr, top, left, piece: Piece, row: int, glyph: str, pair: int):
    for dr, dc in SHAPES[piece.shape][piece.rot]:
        draw_cell(stdscr, top, left, row + dr, piece.col + dc, glyph, pair)


def draw_board(stdscr, board: BoardState, row: int, col: int):
    draw_frame(stdscr, row, col, *board_size(board))
    top, left = row + 1, col + 1  # interior origin

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


def pair_grid(board: BoardState) -> list[list[int | None]]:
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
    addstr_safe(stdscr, row + mini_size(board)[0], col, board.username[:12])


def draw_game(stdscr, boards: dict[int, BoardState], my_id: int):
    screen_h, screen_w = stdscr.getmaxyx()
    mine = boards[my_id]
    minis = [b for pid, b in boards.items() if pid != my_id]

    main_h, board_w = board_size(mine)
    main_w = NEXT_WIDTH + BOARD_GAP + board_w

    # minis: as many columns as fit beside the main board, the rest wrap into new rows
    cols = rows = grid_w = grid_h = 0
    if minis:
        mini_h, mini_w = mini_size(minis[0])
        slot_w = mini_w + BOARD_GAP
        slot_h = mini_h + 1 + ROW_GAP  # +1 for the username label
        free_w = screen_w - main_w - BOARD_GAP
        cols = max(1, min(len(minis), (free_w + BOARD_GAP) // slot_w))
        rows = -(-len(minis) // cols)
        grid_w = cols * slot_w - BOARD_GAP
        grid_h = rows * slot_h - ROW_GAP

    total_w = main_w + (BOARD_GAP + grid_w if minis else 0)
    total_h = max(main_h, grid_h)
    left = max((screen_w - total_w) // 2, 0)
    top = max((screen_h - total_h) // 2, 0)

    main_top = top + (total_h - main_h) // 2
    draw_next(stdscr, mine, main_top + 1, left)
    draw_board(stdscr, mine, main_top, left + NEXT_WIDTH + BOARD_GAP)

    grid_left = left + main_w + BOARD_GAP
    grid_top = top + (total_h - grid_h) // 2
    for i, board in enumerate(minis):
        r, c = divmod(i, cols)
        draw_mini_board(stdscr, board, grid_top + r * slot_h, grid_left + c * slot_w)
