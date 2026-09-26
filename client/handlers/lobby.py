from shared.match_state import MatchState


def handle_player_ready(state, data):
    state.ready_count += 1


def handle_player_unready(state, data):
    state.ready_count -= 1


def handle_countdown_tick(state, data):
    state.countdown = data["seconds"]
