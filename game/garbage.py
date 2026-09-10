import random

from net.client import Client

def send_garbage(sender: Client, recipients: list[Client], lines: int) -> list[Client]:
    if lines <= 1:
        return []

    opponents = [c for c in recipients if c is not sender and not c.board.game_over]
    if not opponents:
        return []

    total_garbage = lines - 1
    per_board = total_garbage // len(opponents)
    remainder = total_garbage % len(opponents)

    extra_recipients = random.sample(opponents, remainder)  # randomly pick who gets +1

    affected = []
    for client in opponents:
        amount = per_board + (1 if client.board in extra_recipients else 0)
        if amount > 0:
            client.board.add_garbage(amount)
            affected.append(client)
    return affected