import asyncio
import json
import time

from websockets import ClientConnection

from client.handlers.connection import handle_player_joined, handle_player_left
from client.handlers.game import (
    handle_all_boards,
    handle_lose,
    handle_piece_locked,
    handle_piece_moved,
    handle_welcome_info,
)
from client.handlers.lobby import (
    handle_countdown_tick,
    handle_player_ready,
    handle_player_unready,
)
from client.handlers.room import handle_room_state
from client.handlers.sync import handle_pong
from client.state.client import ClientState
from game.collision import fits
from net.protocol import send_json

HANDLERS = {
    "welcome_info": handle_welcome_info,
    "all_boards": handle_all_boards,
    "piece_moved": handle_piece_moved,
    "piece_locked": handle_piece_locked,
    "lose": handle_lose,
    "room_state": handle_room_state,
    "player_joined": handle_player_joined,
    "player_ready": handle_player_ready,
    "player_unready": handle_player_unready,
    "countdown_tick": handle_countdown_tick,
    "player_left": handle_player_left,
    "pong": handle_pong,
}


async def receive_loop(ws: ClientConnection, state: ClientState):
    async for msg in ws:
        try:
            data = json.loads(msg)
        except json.JSONDecodeError:
            continue

        message_type = data.get("type") if isinstance(data, dict) else None
        handler = HANDLERS.get(message_type) if isinstance(message_type, str) else None
        if handler:
            handler(state, data)


async def gravity_loop(state: ClientState):
    while True:
        await asyncio.sleep(0.01)
        target_ticks = int(
            (time.monotonic() - state.start_time) * state.ticks_per_second
        )
        while state.tick < target_ticks:
            state.tick += 1
            if state.tick % state.gravity_ticks == 0:
                for board in state.boards.values():
                    if not board.game_over and fits(
                        board.cells,
                        board.piece,
                        board.width,
                        board.height,
                        1,
                        0,
                    ):
                        board.piece.row += 1


async def ping_loop(ws: ClientConnection, state: ClientState):
    while True:
        await send_json(
            ws, "ping", {"player_tick": state.tick, "sent_at": time.monotonic()}
        )
        await asyncio.sleep(1)
