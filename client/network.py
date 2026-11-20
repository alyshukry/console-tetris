import asyncio
import json
import time

from websockets import ClientConnection

from client.state.game import PlayerState
from client.ws_handlers.connection import handle_player_left
from client.ws_handlers.game import (
    handle_all_boards,
    handle_lose,
    handle_piece_locked,
    handle_piece_moved,
    handle_welcome_info,
)
from client.ws_handlers.lobby import handle_countdown_tick, handle_lobby_update
from client.ws_handlers.room import handle_room_state
from client.ws_handlers.sync import handle_pong
from game.collision import fits
from net.protocol import encode

HANDLERS = {
    "welcome_info": handle_welcome_info,
    "all_boards": handle_all_boards,
    "piece_moved": handle_piece_moved,
    "piece_locked": handle_piece_locked,
    "lose": handle_lose,
    "room_state": handle_room_state,
    "lobby_update": handle_lobby_update,
    "countdown_tick": handle_countdown_tick,
    "player_left": handle_player_left,
    "pong": handle_pong,
}


async def receive_loop(ws: ClientConnection, player_state: PlayerState):
    async for msg in ws:
        try:
            data = json.loads(msg)
        except json.JSONDecodeError:
            continue

        message_type = data.get("type") if isinstance(data, dict) else None
        handler = HANDLERS.get(message_type) if isinstance(message_type, str) else None
        if handler:
            handler(player_state, data)


async def gravity_loop(player_state: PlayerState):
    while True:
        await asyncio.sleep(0.01)
        target_ticks = int(
            (time.monotonic() - player_state.start_time) * player_state.ticks_per_second
        )
        while player_state.tick < target_ticks:
            player_state.tick += 1
            if player_state.tick % player_state.gravity_ticks == 0:
                for board in player_state.boards.values():
                    if not board.game_over and fits(
                        board.cells,
                        board.piece,
                        board.width,
                        board.height,
                        1,
                        0,
                    ):
                        board.piece.row += 1


async def ping_loop(ws: ClientConnection, player_state: PlayerState):
    while True:
        await ws.send(
            encode("ping", {"player_tick": player_state.tick, "sent_at": time.monotonic()})
        )
        await asyncio.sleep(1)
