import curses

from net.client import Client


def handle_input(client: Client, key):
    if client.board.game_over:
        return
    {
        curses.KEY_LEFT: client.board.move_piece_left,
        curses.KEY_RIGHT: client.board.move_piece_right,
        curses.KEY_UP: client.board.rotate_piece,
        curses.KEY_DOWN: client.board.move_piece_down,
        ord(" "): client.board.drop_piece,
    }.get(key, lambda: None)()
