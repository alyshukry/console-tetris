import asyncio
import json
from server.match import MatchState
from game.collision import fits


async def receive_loop(ws, state):
    async for msg in ws:
        data = json.loads(msg)
        match data["type"]:
            case "welcome_info":
                state.my_id = data["your_id"]
                state.gravity = data["gravity"]
            case "all_boards":
                state.boards = {int(k): v for k, v in data["boards"].items()}
            case "piece_moved":
                piece = state.boards[data["board_id"]]["piece"]
                piece["rot"] = data["rot"]
                piece["col"] = data["col"]
                piece["row"] = data["row"]
            case "piece_killed":
                b = state.boards[data["board_id"]]
                b["piece"] = data["new_piece"]
                b["next_piece"] = data["next_piece"]
                b["cells"] = data["cells"]
            case "lose":
                state.boards[data["board_id"]]["game_over"] = True
            case "match_state":
                state.match_state = MatchState(data["state"])
                if state.match_state == MatchState.WAITING:
                    state.player_count = data["player_count"]
                    state.ready_count = data["ready_count"]
                    state.ready = False
                if state.match_state == MatchState.RESULTS:
                    state.winners = data["winners"]
            case "player_joined":
                if state.match_state == MatchState.WAITING:
                    state.player_count += 1
            case "player_ready":
                state.ready_count += 1
            case "player_unready":
                state.ready_count -= 1
            case "countdown_tick":
                state.countdown = data["seconds"]
            case "player_left":
                if state.match_state == MatchState.WAITING:
                    state.player_count -= 1
                    if data["was_ready"]:
                        state.ready_count -= 1
                if state.match_state == MatchState.IN_PROGRESS:
                    state.boards.pop(data["player_id"], None)


async def gravity_loop(state):
    while True:
        await asyncio.sleep(state.gravity)
        for board in state.boards.values():
            if not board["game_over"] and fits(
                board["cells"], board["piece"], board["width"], board["height"], 1, 0
            ):
                board["piece"]["row"] += 1
