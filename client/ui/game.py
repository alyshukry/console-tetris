import asyncio

from client.ui.menu import draw_menu

from client.state.client import ClientState, Screen
from client.ui.board import draw_board
from client.ui.curses import addstr_safe
from shared.room_state import RoomState


async def render_loop(stdscr, state: ClientState):
    while True:
        stdscr.clear()

        match state.screen:
            case Screen.MENU:
                draw_menu(stdscr, state.menu_state)
            case Screen.ROOM:
                player_state = state.require_player_state()
                match player_state.room_state:
                    case RoomState.LOBBY:
                        ready_text = (
                            "Press K to get ready" if not player_state.ready else "You are ready"
                        )
        
                        addstr_safe(stdscr, 0, 0, ready_text)
                        addstr_safe(
                            stdscr,
                            1,
                            0,
                            f"{player_state.ready_count}/{player_state.player_count} players ready...",
                        )
        
                    case RoomState.COUNTDOWN:
                        dots = "." * (player_state.countdown % 3 + 1)
                        addstr_safe(
                            stdscr,
                            0,
                            0,
                            f"Starting in {player_state.countdown} seconds{dots}",
                        )
        
                    case RoomState.IN_GAME:
                        if player_state.my_id in player_state.boards:
                            draw_boards(
                                player_state.boards,
                                stdscr,
                                player_state.my_id,
                            )
                        addstr_safe(stdscr, 0, 1, f"{player_state.latency:.0f}ms")
        
                    case RoomState.RESULTS:
                        suffix = "s" if len(player_state.winners) == 1 else ""
                        addstr_safe(
                            stdscr,
                            0,
                            0,
                            f"{player_state.winners} win{suffix} the game!",
                        )

        
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
