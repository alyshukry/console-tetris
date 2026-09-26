from server.player import Player
from server.handlers.game import handle_move_result


def handle_input(player: Player, action, tick, seq):
    if player.board.game_over:
        return
    player.input_queue.append((tick, seq, action))

def apply_input(match, player: Player, action):
    fn = {
        "left": player.board.move_piece_left,
        "right": player.board.move_piece_right,
        "rotate": player.board.rotate_piece,
        "soft_drop": player.board.soft_drop_piece,
        "drop": player.board.drop_piece,
    }.get(action)
    if fn is None:
        return
    handle_move_result(match, player, fn())