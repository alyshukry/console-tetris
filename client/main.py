import asyncio
import json
import websockets
import curses

from server.match import MatchState
from game.collision import fits
from net.protocol import send_json
from render.curses_render import draw, setup_curses


def draw_boards(boards, stdscr, my_id):
    x = 1
    y = 1 + draw(boards[my_id], stdscr, 1, 1, True)[1] + 1
    for id, board in boards.items():
        if id != my_id:
            y += draw(board, stdscr, x, y, False)[1]


def main(stdscr):
    setup_curses(stdscr)

    boards: dict[int, dict] = {}
    my_id: int = -1
    gravity: float = 0.25
    match_state = MatchState.WAITING
    ready = False
    player_count = 1
    ready_count = 0
    countdown = 5
    winners: list[int] = []

    async def run_client():
        async with websockets.connect("ws://192.168.1.90:8888") as ws:
            print("connected")

            async def gravity_loop():
                nonlocal boards
                while True:
                    await asyncio.sleep(gravity)
                    for board in boards.values():
                        if not board["game_over"] and fits(board["cells"], board["piece"], board["width"], board["height"], 1, 0):
                            board["piece"]["row"] += 1

            async def input_loop():
                nonlocal ready, ready_count
                while True:
                    key = stdscr.getch()

                    if key == ord("k"):
                        await send_json(ws, "unready" if ready else "ready")
                        ready = not ready
                        ready_count += 1 if ready else -1
                    if key != -1:
                        await send_json(ws, "input", {"key": key})

                    await asyncio.sleep(0.05)

            async def receive_loop():
                nonlocal boards, my_id, gravity, match_state, player_count, ready_count, countdown, winners, ready
                async for msg in ws:
                    data = json.loads(msg)
                    print(f"from server: {data}")

                    match data["type"]:
                        case "welcome_info":
                            my_id = data["your_id"]
                            gravity = data["gravity"]
                        case "all_boards":
                            boards = {int(k): v for k, v in data["boards"].items()}
                        case "piece_moved":
                            piece = boards[data["board_id"]]["piece"]
                            piece["rot"] = data["rot"]
                            piece["col"] = data["col"]
                            piece["row"] = data["row"]
                        case "piece_killed":
                            boards[data["board_id"]]["piece"] = data["new_piece"]
                            boards[data["board_id"]]["next_piece"] = data["next_piece"]
                            boards[data["board_id"]]["cells"] = data["cells"]
                        case "lose":
                            boards[data["board_id"]]["game_over"] = True
                        case "match_state":
                            match_state = MatchState(data["state"])
                            if match_state == MatchState.WAITING:
                                player_count = data["player_count"]
                                ready_count = data["ready_count"]
                                ready = False
                            if match_state == MatchState.RESULTS:
                                winners = data["winners"]
                        case "player_joined":
                            if match_state == MatchState.WAITING:
                                player_count += 1
                        case "player_ready":
                            ready_count += 1
                        case "player_unready":
                            ready_count -= 1
                        case "countdown_tick":
                            countdown = data["seconds"]

            async def render_loop():
                nonlocal ready, countdown
                while True:
                    stdscr.erase()
                    match match_state:
                        case MatchState.WAITING:
                            stdscr.addstr(0, 0, "Press K to get ready" if not ready else "You are ready")
                            stdscr.addstr(1, 0, f"{ready_count}/{player_count} players ready...")
                        case MatchState.COUNTDOWN:
                            stdscr.addstr(0, 0, f"Starting in {countdown} seconds{"." * (countdown % 3 + 1)}")
                        case MatchState.IN_PROGRESS:
                            if my_id in boards:
                                draw_boards(boards, stdscr, my_id)
                        case MatchState.RESULTS:
                            stdscr.addstr(0, 0, f"{winners} win the game!")
                    await asyncio.sleep(0.02)

            await asyncio.gather(
                input_loop(), receive_loop(), gravity_loop(), render_loop()
            )

    asyncio.run(run_client())


curses.wrapper(main)
