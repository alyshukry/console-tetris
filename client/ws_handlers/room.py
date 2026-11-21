from client.state.client import ClientState
from shared.room_state import RoomState
from client.menu.controller import set_menu


async def handle_room_state(state: ClientState, data):
    player_state = state.require_player_state()
    room_state = RoomState(data["state"])
    player_state.room_state = room_state
    if room_state != RoomState.IN_GAME:
        await set_menu(state, room_state.name)
    if player_state.room_state == RoomState.LOBBY:
        player_state.pending_inputs = []
        player_state.reset_room()
    if player_state.room_state == RoomState.RESULTS:
        player_state.winners = data["winners"]
