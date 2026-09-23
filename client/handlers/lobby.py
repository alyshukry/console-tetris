from server.match_state import MatchState

def handle_match_state(state, data):
    state.match_state = MatchState(data["state"])
    if state.match_state == MatchState.LOBBY:
        state.player_count = data["player_count"]
        state.ready_count = data["ready_count"]
        state.ready = False
    if state.match_state == MatchState.RESULTS:
        state.winners = data["winners"]

def handle_player_joined(state, data):
    if state.match_state == MatchState.LOBBY:
        state.player_count += 1

def handle_player_ready(state, data):
    state.ready_count += 1

def handle_player_unready(state, data):
    state.ready_count -= 1

def handle_countdown_tick(state, data):
    state.countdown = data["seconds"]

def handle_player_left(state, data):
    if state.match_state == MatchState.LOBBY:
        state.player_count -= 1
        if data["was_ready"]:
            state.ready_count -= 1
    if state.match_state == MatchState.IN_GAME:
        state.boards.pop(data["player_id"], None)
        
def handle_pong(state, data):
    rtt_ticks = state.tick - data["client_tick"]
    one_way_ticks = rtt_ticks / 2
    state.rtt_estimate = 0.8 * state.rtt_estimate + 0.2 * one_way_ticks
    target_offset = (data["server_tick"] + state.rtt_estimate) - state.tick
    state.tick += max(-1, min(round(target_offset), 1))