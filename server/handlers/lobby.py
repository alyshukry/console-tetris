from shared.room_state import RoomState


def check_ready(room) -> bool:
    return (
        room.state == RoomState.LOBBY
        and bool(room.connections)
        and all(p.ready for p in room.connections.values())
    )
