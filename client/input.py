import asyncio
import curses

from game.collision import fits
from net.protocol import send_json


async def input_loop(ws, stdscr, state):
    while True:
        key = stdscr.getch()
        if key == ord("k"):
            await send_json(ws, "unready" if state.ready else "ready")
            state.ready = not state.ready
            state.ready_count += 1 if state.ready else -1
        if key != -1 and key in (
            curses.KEY_LEFT,
            curses.KEY_RIGHT,
            curses.KEY_UP,
            curses.KEY_DOWN,
            ord(" "),
        ):
            if state.my_id in state.boards:
                apply_local_move(state.boards[state.my_id], key)
                state.pending_inputs[state.tick] = key
            await send_json(ws, "input", {"key": key, "tick": state.tick})
        await asyncio.sleep(0.025)


def apply_local_move(board, key):
    if not board["game_over"]:

        piece = board["piece"]
        w, h, cells = board["width"], board["height"], board["cells"]

        if key == curses.KEY_LEFT:
            if fits(cells, piece, w, h, 0, -1):
                piece["col"] -= 1
        elif key == curses.KEY_RIGHT:
            if fits(cells, piece, w, h, 0, 1):
                piece["col"] += 1
        elif key == curses.KEY_UP:
            new_rot = (piece["rot"] + 1) % 4
            if fits(cells, piece, w, h, 0, 0, rot=new_rot):
                piece["rot"] = new_rot
        elif key == curses.KEY_DOWN:
            if fits(cells, piece, w, h, 1, 0):
                piece["row"] += 1
        elif key == ord(" "):
            while fits(cells, piece, w, h, 1, 0):
                piece["row"] += 1

        return {"col": piece["col"], "row": piece["row"], "rot": piece["rot"]}
