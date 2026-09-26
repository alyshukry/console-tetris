import random

def calc_garbage(recipients: list[int], lines: int) -> dict[int, int]:
    if lines <= 1:
        return {}

    total_garbage = lines - 1
    per_board = total_garbage // len(recipients)
    remainder = total_garbage % len(recipients)

    extra_recipients = random.sample(recipients, remainder)  # randomly pick who gets +1

    garbage = {}
    for receiver in recipients:
        amount = per_board + (1 if receiver in extra_recipients else 0)
        if amount > 0:
            garbage[receiver] = amount
            
    return garbage