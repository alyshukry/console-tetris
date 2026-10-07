from client.state.client import ClientState
from shared.room_state import RoomState


def handle_room_state(state: ClientState, data):
    state.room_state = RoomState(data["state"])
    if state.room_state == RoomState.LOBBY:
        state.player_count = data["player_count"]
        state.ready_count = data["ready_count"]
        state.pending_inputs = []
        state.ready = False
        state.reset_room()
    if state.room_state == RoomState.RESULTS:
        state.winners = data["winners"]
