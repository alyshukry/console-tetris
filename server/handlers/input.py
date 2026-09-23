import curses

from net.client import Client


def handle_input(client: Client, key, tick):
    if client.board.game_over:
        return
    client.input_queue.append((tick, key))

def apply_input(client: Client, key):
    {
        curses.KEY_LEFT: client.board.move_piece_left,
        curses.KEY_RIGHT: client.board.move_piece_right,
        curses.KEY_UP: client.board.rotate_piece,
        curses.KEY_DOWN: client.board.soft_drop_piece,
        ord(" "): client.board.drop_piece,
    }.get(key, lambda: None)()