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
    round_trip_seconds = time.monotonic() - data["client_sent_at"]

    one_way_seconds = round_trip_seconds / 2
    one_way_tick_estimate = one_way_seconds * state.ticks_per_second

    state.one_way_tick_estimate = (
        0.4 * state.one_way_tick_estimate + 0.6 * one_way_tick_estimate
    )

    estimated_server_tick = data["server_tick"] + state.one_way_tick_estimate

    target_offset = estimated_server_tick - state.tick

    print(
        f"rtt={round_trip_seconds * 1000:.1f}ms "
        f"one_way_ticks={one_way_tick_estimate:.2f} "
        f"one_way_est={state.one_way_tick_estimate:.2f} "
        f"server_tick={data['server_tick']} "
        f"client_tick_before={state.tick} "
        f"raw_gap={data['server_tick'] - state.tick} "
        f"offset={target_offset:.2f} "
        f"tick={state.tick}->{state.tick + round(target_offset)}"
    )

    state.tick += min(max(round(target_offset), -3), 3)
