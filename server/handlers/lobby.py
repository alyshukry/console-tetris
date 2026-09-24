import asyncio
from game.board import Board
from game.seven_bag import SevenBag
from net.protocol import broadcast_json
from server.match_state import MatchState, set_match_state


def check_ready(match) -> bool:
    return (
        match.state == MatchState.LOBBY
        and bool(match.connections)
        and all(c.ready for c in match.connections.values())
    )


async def start_countdown(match):
    await set_match_state(match, MatchState.COUNTDOWN)

    try:
        for remaining in range(match.countdown_seconds, 0, -1):
            await broadcast_json(match, "countdown_tick", {"seconds": remaining})
            await asyncio.sleep(1)
        await match.start_game()
    except asyncio.CancelledError:
        await set_match_state(
            match,
            MatchState.LOBBY,
            {
                "player_count": len(match.connections),
                "ready_count": sum(c.ready for c in match.connections.values()),
            },
        )
    finally:
        match.countdown_task = None


async def cancel_countdown(match):
    if match.countdown_task is not None:
        match.countdown_task.cancel()
        try:
            await match.countdown_task
        except asyncio.CancelledError:
            pass


async def reset_to_lobby(match):
    match.shared_bag = SevenBag()
    match.tick = 0
    for client in match.connections.values():
        client.ready = False
        client.board = Board(match.shared_bag)
        client.input_queue.clear()
        client.last_processed_input_tick = -1

    await set_match_state(
        match,
        MatchState.LOBBY,
        {
            "player_count": len(match.connections),
            "ready_count": 0,
        },
    )
