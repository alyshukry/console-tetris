import asyncio
import time

import websockets

from game.constants import TICKS_PER_SECOND
from net.protocol import send_json
from server.engine.inputs import apply_input
from server.engine.lifecycle import end_game
from server.engine.moves import resolve_move
from server.routes.ws import handler
from shared.room_state import RoomState


async def game_loop(room):
    while True:
        if room.state == RoomState.IN_GAME:
            target_ticks = int(
                (time.monotonic() - (room.start_time or 0)) * TICKS_PER_SECOND
            )
            while room.tick < target_ticks:
                room.tick += 1
                alive_before = [
                    p for p in room.connections.values() if not p.board.game_over
                ]

                for player in alive_before:
                    if player.board.game_over:  # died earlier this tick (e.g. garbage)
                        continue
                    due = [item for item in player.input_queue if item[0] <= room.tick]
                    player.input_queue = [
                        i for i in player.input_queue if i[0] > room.tick
                    ]
                    for tick, seq, action in sorted(
                        due, key=lambda item: (item[0], item[1])
                    ):
                        if (tick, seq) > (
                            player.last_processed_input_tick,
                            player.last_processed_input_seq,
                        ):
                            player.last_processed_input_tick = tick
                            player.last_processed_input_seq = seq
                        apply_input(room, player, action)

                if room.tick % room.gravity_ticks == 0:
                    for player in alive_before:
                        if not player.board.game_over:
                            resolve_move(room, player, player.board.move_piece_down())

                just_died = [p for p in alive_before if p.board.game_over]
                for p in just_died:
                    room.broadcast("lose", {"board_id": p.player_id})

                alive_after = [p for p in alive_before if not p.board.game_over]
                if len(alive_after) <= 1:
                    await end_game(room, alive_after or just_died)
                    break
        await asyncio.sleep(1 / TICKS_PER_SECOND)


async def net_loop(room):
    while True:
        await asyncio.gather(
            *(flush(ws, p) for ws, p in list(room.connections.items()) if p.outbox),
            return_exceptions=True,
        )
        await asyncio.sleep(0.01)


async def flush(ws, player):
    msgs, player.outbox = player.outbox, []
    for t, d in msgs:
        await send_json(ws, t, d)


async def run_room(room):
    async with websockets.serve(handler, "0.0.0.0", 8888):
        await asyncio.gather(game_loop(room), net_loop(room))
