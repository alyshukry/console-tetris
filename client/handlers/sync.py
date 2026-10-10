import time

from client.state.client import ClientState


def handle_pong(state: ClientState, data):
    round_trip_seconds = time.monotonic() - data["player_sent_at"]
    state.latency = round_trip_seconds * 1000 * 0.3 + state.latency * 0.7

    one_way_seconds = round_trip_seconds / 2
    one_way_tick_estimate = one_way_seconds * state.ticks_per_second

    state.one_way_tick_estimate = 0.4 * state.one_way_tick_estimate + 0.6 * one_way_tick_estimate

    estimated_server_tick = data["server_tick"] + state.one_way_tick_estimate

    target_offset = estimated_server_tick - state.tick

    adj = min(max(round(target_offset), -3), 3)
    state.start_time -= adj / state.ticks_per_second
    state.tick += adj
