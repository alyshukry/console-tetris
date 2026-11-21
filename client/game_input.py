import curses

from client.state.game import BoardState
from game.collision import fits
from game.piece import Piece
from net.protocol import encode
from shared.action import Action


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


async def handle_game_input(player_state, key):
    if key in (
        curses.KEY_LEFT,
        curses.KEY_RIGHT,
        curses.KEY_UP,
        curses.KEY_DOWN,
        ord(" "),
    ):
        if player_state.my_id in player_state.boards:
            apply_local_move(player_state.boards[player_state.my_id], key)
        tick = player_state.tick
        seq = player_state.input_seq_by_tick.get(tick, 0)
        player_state.pending_inputs.append((tick, seq, key))
        player_state.input_seq_by_tick[tick] = seq + 1
        await player_state.ws.send(
            encode(
                "input",
                {"action": key_to_action(key), "tick": tick, "seq": seq},
            )
        )
