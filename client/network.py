import asyncio
import json
from game.collision import fits
from client.handlers.game import (
    handle_welcome_info, handle_all_boards, handle_piece_moved,
    handle_piece_killed, handle_lose,
)
from client.handlers.lobby import (
    handle_match_state, handle_player_joined, handle_player_ready,
    handle_player_unready, handle_countdown_tick, handle_player_left,
)

HANDLERS = {
    "welcome_info": handle_welcome_info,
    "all_boards": handle_all_boards,
    "piece_moved": handle_piece_moved,
    "piece_killed": handle_piece_killed,
    "lose": handle_lose,
    "match_state": handle_match_state,
    "player_joined": handle_player_joined,
    "player_ready": handle_player_ready,
    "player_unready": handle_player_unready,
    "countdown_tick": handle_countdown_tick,
    "player_left": handle_player_left,
}

async def receive_loop(ws, state):
    async for msg in ws:
        data = json.loads(msg)
        handler = HANDLERS.get(data["type"])
        if handler:
            handler(state, data)

async def gravity_loop(state):
    while True:
        await asyncio.sleep(state.tick_interval)
        state.tick += 1
        if state.tick % state.gravity_ticks == 0:
            for board in state.boards.values():
                if not board["game_over"] and fits(
                    board["cells"], board["piece"], board["width"], board["height"], 1, 0
                ):
                    board["piece"]["row"] += 1