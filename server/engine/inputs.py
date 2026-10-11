from server.engine.moves import resolve_move
from server.models.player import Player
from shared.action import Action




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
    resolve_move(room, player, fn())
