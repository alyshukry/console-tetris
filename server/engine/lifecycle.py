import asyncio
import time

from game.board import Board
from game.constants import TICKS_PER_SECOND
from game.seven_bag import SevenBag
from net.serialization import serialize_board
from server.config import COUNTDOWN_SECONDS
from server.models.player import Player
from shared.room_state import RoomState


async def reset_to_lobby(room):
    room.shared_bag = SevenBag()
    room.tick = 0
    for player in room.connections.values():
        player.ready = False
        player.board = Board(room.shared_bag)
        player.input_queue.clear()
        player.last_processed_input_tick = -1
        player.last_processed_input_seq = -1

    await set_room_state(room, RoomState.LOBBY)
    room.broadcast_lobby()


async def start_countdown(room):
    await set_room_state(room, RoomState.COUNTDOWN)

    try:
        for remaining in range(COUNTDOWN_SECONDS, 0, -1):
            room.broadcast("countdown_tick", {"seconds": remaining})
            await asyncio.sleep(1)
        await start_game(room)
    except asyncio.CancelledError:
        await set_room_state(room, RoomState.LOBBY)
        room.broadcast_lobby()
    finally:
        room.countdown_task = None


async def cancel_countdown(room):
    if room.countdown_task is not None:
        room.countdown_task.cancel()
        try:
            await room.countdown_task
        except asyncio.CancelledError:
            pass


async def set_room_state(room, new_state: "RoomState", extra: dict | None = None):
    room.state = new_state
    room.broadcast("room_state", {"state": new_state.value, **(extra or {})})


async def start_game(room):
        for player in list(room.connections.values()):
            player.outbox.append(
                (
                    "welcome_info",
                    {
                        "your_board": serialize_board(player.board),
                        "your_id": player.player_id,
                        "ticks_per_second": TICKS_PER_SECOND,
                        "gravity_ticks": room.gravity_ticks,
                        "tick": room.tick,
                    },
                )
            )
            player.outbox.append(("all_boards", all_boards_payload(room)))

        room.start_time = time.monotonic()
        await set_room_state(room, RoomState.IN_GAME)
        
        
async def end_game(room, winners: list[Player]):
    await set_room_state(
        room, RoomState.RESULTS, {"winners": [p.player_id for p in winners]}
    )
    await asyncio.sleep(5)
    await reset_to_lobby(room)
    
def all_boards_payload(room):
    return {
        "boards": {
            p.player_id: serialize_board(p.board) for p in room.connections.values()
        }
    }