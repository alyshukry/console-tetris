from shared.match_state import MatchState


def handle_player_left(state, data):
    if state.match_state == MatchState.LOBBY:
        state.player_count -= 1
        if data["was_ready"]:
            state.ready_count -= 1
    if state.match_state == MatchState.IN_GAME:
        state.boards.pop(data["player_id"], None)


def handle_player_joined(state, data):
    if state.match_state == MatchState.LOBBY:
        state.player_count += 1
