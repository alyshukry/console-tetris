import time

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
    rtt_seconds = time.monotonic() - data["client_sent_at"]
    one_way_ticks = (rtt_seconds / 2) * state.ticks_per_second
    state.rtt_estimate = 0.4 * state.rtt_estimate + 0.6 * one_way_ticks
    target_offset = (data["server_tick"] + state.rtt_estimate) - state.tick
    print(
        f"rtt={rtt_seconds*1000:.1f}ms one_way_ticks={one_way_ticks:.2f} rtt_est={state.rtt_estimate:.2f} "
        f"server_tick={data['server_tick']} client_tick_before={state.tick} raw_gap={data['server_tick']-state.tick} "
        f"offset={target_offset:.2f} tick={state.tick}->{state.tick+round(target_offset)}"
    )
    state.tick += min(max(round(target_offset), -3), 3)
