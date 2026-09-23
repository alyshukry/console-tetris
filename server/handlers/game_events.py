from game.garbage import send_garbage


def make_callbacks(match, client):
    def on_piece_moved():
        event = (
            "piece_moved",
            {
                "board_id": client.id,
                "row": client.board.piece.row,
                "col": client.board.piece.col,
                "rot": client.board.piece.rot,
            },
        )
        for c in match.connections.values():
            c.outbox.append(event)

    def board_update_event(c):
        d = c.board.to_dict()
        return (
            "piece_killed",
            {
                "board_id": c.id,
                "cells": d.get("cells"),
                "new_piece": d.get("piece"),
                "next_piece": d.get("next_piece"),
            },
        )

    def on_piece_killed(lines: int):
        affected = (
            send_garbage(client, list(match.connections.values()), lines)
            if lines > 0
            else []
        )

        event = board_update_event(client)
        for c in match.connections.values():
            c.outbox.append(event)

        for garbage_client in affected:
            garbage_event = board_update_event(garbage_client)
            for c in match.connections.values():
                c.outbox.append(garbage_event)

    def on_lose():
        event = ("lose", {"board_id": client.id})
        for c in match.connections.values():
            c.outbox.append(event)

    return on_piece_moved, on_piece_killed, on_lose
