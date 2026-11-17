from shared.room_state import RoomState


def handle_player_left(state, data):
    if state.room_state == RoomState.IN_GAME:
        state.boards.pop(data["player_id"], None)
