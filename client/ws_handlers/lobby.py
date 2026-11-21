from client.state.client import ClientState


async def handle_lobby_update(state: ClientState, data):
    player_state = state.require_player_state()
    player_state.player_count = data["player_count"]
    player_state.ready_count = data["ready_count"]
    player_state.ready = data["you_ready"]


async def handle_countdown_tick(state: ClientState, data):
    player_state = state.require_player_state()
    player_state.countdown = data["seconds"]
