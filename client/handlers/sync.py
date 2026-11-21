import time

from client.state.client import ClientState


async def handle_pong(state: ClientState, data):
    player_state = state.require_player_state()
    round_trip_seconds = time.monotonic() - data["player_sent_at"]
    player_state.latency = round_trip_seconds * 1000 * 0.3 + player_state.latency * 0.7

    one_way_seconds = round_trip_seconds / 2
    one_way_tick_estimate = one_way_seconds * player_state.ticks_per_second

    player_state.one_way_tick_estimate = (
        0.4 * player_state.one_way_tick_estimate + 0.6 * one_way_tick_estimate
    )

    estimated_server_tick = data["server_tick"] + player_state.one_way_tick_estimate

    target_offset = estimated_server_tick - player_state.tick

    adj = min(max(round(target_offset), -3), 3)
    player_state.start_time -= adj / player_state.ticks_per_second
    player_state.tick += adj
