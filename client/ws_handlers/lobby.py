def handle_lobby_update(state, data):
    state.player_count = data["player_count"]
    state.ready_count = data["ready_count"]
    state.ready = data["you_ready"]


def handle_countdown_tick(state, data):
    state.countdown = data["seconds"]
