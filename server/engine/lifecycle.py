import asyncio

from game.board import Board
from game.seven_bag import SevenBag
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
        for remaining in range(room.countdown_seconds, 0, -1):
            room.broadcast("countdown_tick", {"seconds": remaining})
            await asyncio.sleep(1)
        await room.start_game()
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
