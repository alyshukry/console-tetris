import asyncio

from client.state.client import ClientState
from client.ui.curses import addstr_safe
from client.ui.game import draw_boards
from client.ui.menu import draw_menu
from shared.room_state import RoomState


async def render_loop(stdscr, state: ClientState):
    while True:
        stdscr.erase()
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
