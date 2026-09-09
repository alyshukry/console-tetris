from typing import Callable
from .board import Board
from .garbage import send_garbage

def make_lines_cleared_handler(board: Board, all_boards: list[Board]) -> Callable[[int], None]:
    def handler(lines_cleared: int):
        send_garbage(board, all_boards, lines_cleared)
    return handler