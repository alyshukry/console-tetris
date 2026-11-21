from client.menu.controller import set_menu
from client.menu.types import MenuName
from client.state.client import ClientState
from shared.room_state import RoomState


async def handle_room_state(state: ClientState, data):
    player_state = state.require_player_state()
    room_state = RoomState(data["state"])
    player_state.room_state = room_state
    if room_state != RoomState.IN_GAME:
        await set_menu(state, MenuName[room_state.name])
    if player_state.room_state == RoomState.LOBBY:
        player_state.pending_inputs = []
        player_state.reset_room()
    if player_state.room_state == RoomState.RESULTS:
        player_state.winners = data["winners"]


async def handle_player_left(state: ClientState, data):
    player_state = state.require_player_state()
    if player_state.room_state == RoomState.IN_GAME:
        player_state.boards.pop(data["player_id"], None)


async def handle_lobby_update(state: ClientState, data):
    player_state = state.require_player_state()
    player_state.player_count = data["player_count"]
    player_state.ready_count = data["ready_count"]
    player_state.ready = data["you_ready"]


async def handle_countdown_tick(state: ClientState, data):
    player_state = state.require_player_state()
    player_state.countdown = data["seconds"]
