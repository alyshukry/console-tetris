from client.state.game import PlayerState
from shared.room_state import RoomState


def handle_room_state(state: PlayerState, data):
    state.room_state = RoomState(data["state"])
    if state.room_state == RoomState.LOBBY:
        state.pending_inputs = []
        state.reset_room()
    if state.room_state == RoomState.RESULTS:
        state.winners = data["winners"]
