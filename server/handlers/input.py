import curses

from server.player import Player


def handle_input(player: Player, action, tick):
    if player.board.game_over:
        return
    player.input_queue.append((tick, action))

def apply_input(player: Player, action):
    {
        "left": player.board.move_piece_left,
        "right": player.board.move_piece_right,
        "rotate": player.board.rotate_piece,
        "soft_drop": player.board.soft_drop_piece,
        "drop": player.board.drop_piece,
    }.get(action, lambda: None)()