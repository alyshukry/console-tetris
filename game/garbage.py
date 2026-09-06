import random

from .board import Board

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