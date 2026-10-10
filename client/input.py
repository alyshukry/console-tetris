import asyncio
import curses

from client.state.board import BoardState
from game.collision import fits
from game.piece import Piece
from net.protocol import send_json
from shared.action import Action
from shared.room_state import RoomState


async def input_loop(ws, stdscr, state):
    while True:
        key = stdscr.getch()
        if key == ord("k"):
            await send_json(ws, "unready" if state.ready else "ready")
            state.ready = not state.ready
            state.ready_count += 1 if state.ready else -1
        if state.room_state == RoomState.IN_GAME and key in (
            curses.KEY_LEFT,
            curses.KEY_RIGHT,
            curses.KEY_UP,
            curses.KEY_DOWN,
            ord(" "),
        ):
            if state.my_id in state.boards:
                apply_local_move(state.boards[state.my_id], key)
            tick = state.tick
            seq = state.input_seq_by_tick.get(tick, 0)
            state.pending_inputs.append((tick, seq, key))
            state.input_seq_by_tick[tick] = seq + 1
            await send_json(
                ws,
                "input",
                {"action": key_to_action(key), "tick": tick, "seq": seq},
            )
        await asyncio.sleep(0.025)


def key_to_action(key) -> Action | None:
    return {
        curses.KEY_LEFT: Action.LEFT,
        curses.KEY_RIGHT: Action.RIGHT,
        curses.KEY_UP: Action.ROTATE,
        curses.KEY_DOWN: Action.SOFT_DROP,
        ord(" "): Action.DROP,
    }.get(key)


def apply_local_move(board: BoardState, key):
    if not board.game_over:
        piece: Piece = board.piece
        w, h, cells = board.width, board.height, board.cells

        if key == curses.KEY_LEFT:
            if fits(cells, piece, w, h, 0, -1):
                piece.col -= 1
        elif key == curses.KEY_RIGHT:
            if fits(cells, piece, w, h, 0, 1):
                piece.col += 1
        elif key == curses.KEY_UP:
            new_rot = (piece.rot + 1) % 4
            if fits(cells, piece, w, h, 0, 0, rot=new_rot):
                piece.rot = new_rot
        elif key == curses.KEY_DOWN:
            if fits(cells, piece, w, h, 1, 0):
                piece.row += 1
        elif key == ord(" "):
            while fits(cells, piece, w, h, 1, 0):
                piece.row += 1
