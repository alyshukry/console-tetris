import asyncio
import curses
from dataclasses import dataclass

from client.state.board import BoardState
from game.collision import get_ghost_row
from game.constants import SHAPES
from render.colors import (
    BORDER_PAIR,
    EMPTY_PAIR,
    GAME_OVER_PAIR,
    PIECE_COLORS,
    GARBAGE_PAIR,
    setup_colors,
)
from shared.match_state import MatchState

CELL_WIDTH = 2
CELL = "██"
GHOST_CELL = "░░"


@dataclass(frozen=True)
class RenderBounds:
    min_row: int
    min_col: int
    max_row: int
    max_col: int

    @property
    def height(self) -> int:
        return self.max_row - self.min_row + 1

    @property
    def width(self) -> int:
        return self.max_col - self.min_col + 1


def draw_boards(boards, stdscr, my_id):
    screen_height, screen_width = stdscr.getmaxyx()

    top = 2
    left = 1

    ordered_boards = []

    if my_id in boards:
        ordered_boards.append((my_id, boards[my_id]))

    ordered_boards.extend(
        (player_id, board) for player_id, board in boards.items() if player_id != my_id
    )

    for _, board in ordered_boards:
        if left >= screen_width - 1:
            break

        bounds = draw_board(
            board,
            stdscr,
            top,
            left,
            board is boards.get(my_id),
            screen_height,
            screen_width,
        )

        left = bounds.max_col + 2


async def render_loop(stdscr, state):
    while True:
        stdscr.erase()

        match state.match_state:
            case MatchState.LOBBY:
                ready_text = (
                    "Press K to get ready" if not state.ready else "You are ready"
                )

                addstr_safe(stdscr, 0, 0, ready_text)
                addstr_safe(
                    stdscr,
                    1,
                    0,
                    f"{state.ready_count}/{state.player_count} players ready...",
                )

            case MatchState.COUNTDOWN:
                dots = "." * (state.countdown % 3 + 1)
                addstr_safe(
                    stdscr,
                    0,
                    0,
                    f"Starting in {state.countdown} seconds{dots}",
                )

            case MatchState.IN_GAME:
                if state.my_id in state.boards:
                    draw_boards(
                        state.boards,
                        stdscr,
                        state.my_id,
                    )
                addstr_safe(stdscr, 0, 1, f"{state.latency:.0f}ms")

            case MatchState.RESULTS:
                suffix = "s" if len(state.winners) == 1 else ""
                addstr_safe(
                    stdscr,
                    0,
                    0,
                    f"{state.winners} win{suffix} the game!",
                )

        await asyncio.sleep(0.02)


def fill_rect(
    stdscr,
    top,
    left,
    bottom,
    right,
    color_pair,
    cell=CELL,
):
    screen_height, screen_width = stdscr.getmaxyx()

    top = max(top, 0)
    bottom = min(bottom, screen_height - 1)

    left_char = max(left * CELL_WIDTH, 0)
    right_char = min(
        (right + 1) * CELL_WIDTH,
        screen_width,
    )

    if top > bottom or left_char >= right_char:
        return

    text = cell * ((right_char - left_char) // CELL_WIDTH)

    for row in range(top, bottom + 1):
        try:
            addstr_safe(
                stdscr,
                row,
                left_char,
                text,
                curses.color_pair(color_pair),
            )
        except curses.error:
            pass


def draw_board(
    board: BoardState,
    stdscr,
    top: int,
    left: int,
    show_next: bool,
    screen_height: int,
    screen_width: int,
) -> RenderBounds:
    board_bottom = top + board.height - 1
    board_right = left + board.width - 1

    min_row = top - 1
    max_row = board_bottom + 1
    min_col = left - 1
    max_col = board_right + 1

    if min_row >= screen_height or min_col >= screen_width:
        return RenderBounds(
            min_row,
            min_col,
            max_row,
            max_col,
        )

    fill_rect(
        stdscr,
        top,
        left,
        board_bottom,
        board_right,
        EMPTY_PAIR,
    )

    draw_border(
        board,
        stdscr,
        top,
        left,
    )

    if show_next:
        preview_top = top + 2
        preview_left = board_right + 3
        preview_bottom = top + 6
        preview_right = preview_left + 5

        fill_rect(
            stdscr,
            preview_top,
            preview_left,
            preview_bottom,
            preview_right,
            EMPTY_PAIR,
        )

        draw_piece(
            board,
            stdscr,
            top,
            left,
            board.next_piece.shape,
            4,
            board.width + 4,
            0,
        )

        addstr_safe(
            stdscr,
            top + 1,
            preview_left * CELL_WIDTH,
            "NEXT PIECE:",
        )

        max_col = max(
            max_col,
            preview_right,
        )
        max_row = max(
            max_row,
            preview_bottom,
        )

    if not board.game_over:
        draw_ghost(
            board,
            stdscr,
            top,
            left,
        )

    piece = board.piece

    draw_piece(
        board,
        stdscr,
        top,
        left,
        piece.shape,
        piece.row,
        piece.col,
        piece.rot,
    )

    game_over_pair = GAME_OVER_PAIR if board.game_over else None

    for row in range(board.height):
        for col in range(board.width):
            cell = board.cells[row][col]

            if cell in (0, None):
                continue

            if game_over_pair:
                pair = game_over_pair
            elif cell == "X":
                pair = GARBAGE_PAIR
            else:
                pair = PIECE_COLORS[cell]

            addstr_safe(
                stdscr,
                top + row,
                (left + col) * CELL_WIDTH,
                CELL,
                curses.color_pair(pair),
            )

    return RenderBounds(
        min_row,
        min_col,
        max_row,
        max_col,
    )


def draw_piece(
    board,
    stdscr,
    top,
    left,
    shape,
    row,
    col,
    rot,
):
    pair = GAME_OVER_PAIR if board.game_over else PIECE_COLORS[shape]

    for dr, dc in SHAPES[shape][rot]:
        screen_row = top + row + dr
        screen_col = left + col + dc

        if screen_row <= top - 1:
            continue

        addstr_safe(
            stdscr,
            screen_row,
            screen_col * CELL_WIDTH,
            CELL,
            curses.color_pair(pair),
        )


def draw_ghost(
    board,
    stdscr,
    top,
    left,
):
    ghost_row = get_ghost_row(
        board.cells,
        board.piece,
        board.width,
        board.height,
    )

    piece = board.piece
    pair = PIECE_COLORS[piece.shape]

    for dr, dc in SHAPES[piece.shape][piece.rot]:
        addstr_safe(
            stdscr,
            top + piece.row + ghost_row + dr,
            (left + piece.col + dc) * CELL_WIDTH,
            GHOST_CELL,
            curses.color_pair(pair),
        )


def draw_border(
    board,
    stdscr,
    top,
    left,
):
    border_top = top - 1
    border_left = (left - 1) * CELL_WIDTH
    border_bottom = top + board.height
    border_right = (left + board.width) * CELL_WIDTH

    pair = curses.color_pair(BORDER_PAIR)

    addstr_safe(
        stdscr,
        border_top,
        border_left,
        " ▄" + "▄" * (board.width * CELL_WIDTH) + "▄ ",
        pair,
    )

    for row in range(board.height):
        screen_row = top + row

        addstr_safe(
            stdscr,
            screen_row,
            border_left,
            " █",
            pair,
        )

        addstr_safe(
            stdscr,
            screen_row,
            border_right,
            "█ ",
            pair,
        )

    addstr_safe(
        stdscr,
        border_bottom,
        border_left,
        " ▀" + "▀" * (board.width * CELL_WIDTH) + "▀ ",
        pair,
    )


def setup_curses(stdscr):
    curses.curs_set(0)
    curses.start_color()

    stdscr.keypad(True)
    stdscr.nodelay(True)
    stdscr.timeout(50)

    setup_colors()


def addstr_safe(stdscr, row, col, text, attributes=0):
    screen_height, screen_width = stdscr.getmaxyx()

    if row < 0 or row >= screen_height:
        return

    if col < 0:
        text = text[-col:]
        col = 0

    if col >= screen_width or not text:
        return

    text = text[: screen_width - col]

    try:
        stdscr.addstr(
            row,
            col,
            text,
            attributes,
        )
    except curses.error:
        pass
