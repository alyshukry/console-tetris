from client.state.client import ClientState
from shared.room_state import RoomState


async def handle_player_left(state: ClientState, data):
    player_state = state.require_player_state()
    if player_state.room_state == RoomState.IN_GAME:
        player_state.boards.pop(data["player_id"], None)
