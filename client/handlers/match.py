from shared.match_state import MatchState


def handle_match_state(state, data):
    state.match_state = MatchState(data["state"])
    if state.match_state == MatchState.LOBBY:
        state.player_count = data["player_count"]
        state.ready_count = data["ready_count"]
        state.ready = False
    if state.match_state == MatchState.RESULTS:
        state.winners = data["winners"]
