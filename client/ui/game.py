import asyncio

from client.state.client import ClientState
from client.ui.board import draw_board
from client.ui.curses import addstr_safe
from client.ui.menu import draw_menu
from shared.room_state import RoomState


async def render_loop(stdscr, state: ClientState):
    while True:
        stdscr.clear()
        player_state = state.player_state
        if player_state is not None and player_state.room_state == RoomState.IN_GAME:
            if player_state.my_id in player_state.boards:
                draw_boards(
                    player_state.boards,
                    stdscr,
                    player_state.my_id,
                )
            addstr_safe(stdscr, 0, 1, f"{player_state.latency:.0f}ms")
        else:
            draw_menu(stdscr, state)

        stdscr.refresh()
        await asyncio.sleep(0.02)


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
