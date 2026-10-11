import asyncio

from server.config import MIN_PLAYERS
from server.engine.lifecycle import cancel_countdown, start_countdown
from shared.room_state import RoomState


def check_ready(room) -> bool:
    return (
        room.state == RoomState.LOBBY
        and len(room.connections) >= MIN_PLAYERS
        and all(p.ready for p in room.connections.values())
    )


async def handle_leave(room, ws):
    leaver = room.connections.pop(ws, None)
    if leaver is None:
        return

    room.broadcast("player_left", {"player_id": leaver.player_id})
    room.broadcast_lobby()

    if room.state == RoomState.COUNTDOWN and len(room.connections) < MIN_PLAYERS:
        await cancel_countdown(room)
    elif check_ready(room) and room.countdown_task is None:
        room.countdown_task = asyncio.create_task(start_countdown(room))
