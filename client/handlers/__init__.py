from client.handlers.game import (
    handle_all_boards,
    handle_lose,
    handle_piece_locked,
    handle_piece_moved,
    handle_welcome_info,
)
from client.handlers.room import (
    handle_countdown_tick,
    handle_lobby_update,
    handle_player_left,
    handle_room_state,
)
from client.handlers.sync import handle_pong

HANDLERS = {
    "welcome_info": handle_welcome_info,
    "all_boards": handle_all_boards,
    "piece_moved": handle_piece_moved,
    "piece_locked": handle_piece_locked,
    "lose": handle_lose,
    "room_state": handle_room_state,
    "lobby_update": handle_lobby_update,
    "countdown_tick": handle_countdown_tick,
    "player_left": handle_player_left,
    "pong": handle_pong,
}
