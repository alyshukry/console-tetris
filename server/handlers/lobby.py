from shared.match_state import MatchState


def check_ready(match) -> bool:
    return (
        match.state == MatchState.LOBBY
        and bool(match.connections)
        and all(p.ready for p in match.connections.values())
    )
