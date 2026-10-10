from server.handlers.game import handle_move_result
from server.player import Player
from shared.action import Action


def handle_input(player: Player, action: Action, tick: int, seq: int):
    if player.board.game_over:
        return
    if len(player.input_queue) < 50:
        player.input_queue.append((tick, seq, action))


def apply_input(room, player: Player, action):
    fn = {
        "left": player.board.move_piece_left,
        "right": player.board.move_piece_right,
        "rotate": player.board.rotate_piece,
        "soft_drop": player.board.soft_drop_piece,
        "drop": player.board.drop_piece,
    }.get(action)
    if fn is None:
        return
    handle_move_result(room, player, fn())
