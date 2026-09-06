import curses
import time
import random
from typing import Callable

from game.board import Board
from game.seven_bag import SevenBag
from render.curses import draw, setup_curses

def send_garbage(sender: Board, recipients: list[Board], lines: int) -> int:
    if lines <= 1:
        return 0

    opponents = [b for b in recipients if b is not sender and not b.game_over]
    if not opponents:
        return 0

    total_garbage = lines - 1
    per_board = total_garbage // len(opponents)
    remainder = total_garbage % len(opponents)

    extra_recipients = random.sample(opponents, remainder)  # randomly pick who gets +1

    sent = 0
    for board in opponents:
        amount = per_board + (1 if board in extra_recipients else 0)
        if amount > 0:
            board.add_garbage(amount)
            sent += amount
    return sent

def make_lines_cleared_handler(board, all_boards) -> Callable[[int], None]:
    def handler(lines_cleared):
        send_garbage(board, all_boards, lines_cleared)

    return handler


def main(stdscr):
    setup_curses(stdscr)
    
    shared_bag = SevenBag()
    boards = [
        Board(1, 1, shared_bag),
        Board(1, 18 + 1, shared_bag, show_next=False),
        Board(1, 30 + 1, shared_bag, show_next=False),
    ]
    for board in boards:
        board.on_lines_cleared = make_lines_cleared_handler(board, boards)

    last_drop = time.time()
    drop_interval = 0.5
    selected_board = 0

    while True:
        key = stdscr.getch()
        if key == ord("q"):
            break
        if key == ord("p"):
            selected_board = (selected_board + 1) % len(boards)

        if not boards[selected_board].game_over:
            if key == curses.KEY_LEFT:
                boards[selected_board].move_piece_left()
            if key == curses.KEY_RIGHT:
                boards[selected_board].move_piece_right()
            if key == curses.KEY_UP:
                boards[selected_board].rotate_piece()
            if key == curses.KEY_DOWN:
                boards[selected_board].move_piece_down()
                last_drop = time.time()
            if key == ord(" "):
                boards[selected_board].drop_piece()

        now = time.time()
        if now - last_drop >= drop_interval:
            for board in boards:
                if not board.game_over:
                    board.move_piece_down()
            last_drop = now

        stdscr.clear()
        try:
            for board in boards:
                draw(board, stdscr)
        except curses.error:
            stdscr.clear()
            stdscr.addstr(0, 0, "Please expand console window.")

        stdscr.refresh()


curses.wrapper(main)
