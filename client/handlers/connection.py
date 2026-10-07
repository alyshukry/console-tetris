from shared.room_state import RoomState


def handle_player_left(state, data):
    if state.room_state == RoomState.LOBBY:
        state.player_count -= 1
        if data["was_ready"]:
            state.ready_count -= 1
    if state.room_state == RoomState.IN_GAME:
        state.boards.pop(data["player_id"], None)


def handle_player_joined(state, data):
    if state.room_state == RoomState.LOBBY:
        state.player_count += 1
