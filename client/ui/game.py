import asyncio

from client.ui.board import draw_board
from client.ui.curses import addstr_safe
from shared.room_state import RoomState


async def render_loop(stdscr, state):
    while True:
        stdscr.erase()

        match state.room_state:
            case RoomState.LOBBY:
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

            case RoomState.COUNTDOWN:
                dots = "." * (state.countdown % 3 + 1)
                addstr_safe(
                    stdscr,
                    0,
                    0,
                    f"Starting in {state.countdown} seconds{dots}",
                )

            case RoomState.IN_GAME:
                if state.my_id in state.boards:
                    draw_boards(
                        state.boards,
                        stdscr,
                        state.my_id,
                    )
                addstr_safe(stdscr, 0, 1, f"{state.latency:.0f}ms")

            case RoomState.RESULTS:
                suffix = "s" if len(state.winners) == 1 else ""
                addstr_safe(
                    stdscr,
                    0,
                    0,
                    f"{state.winners} win{suffix} the game!",
                )

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
