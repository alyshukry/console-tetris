import asyncio

from client.game_input import handle_game_input
from client.menu.controller import handle_menu_input
from client.state.client import ClientState
from shared.room_state import RoomState


async def input_loop(stdscr, state: ClientState):
    while True:
        key = stdscr.getch()
        if key != -1:
            if (
                state.player_state is not None
                and state.player_state.room_state == RoomState.IN_GAME
            ):
                await handle_game_input(state.player_state, key)
            else:
                await handle_menu_input(state.menu_state, state, key)
        await asyncio.sleep(0.025)
