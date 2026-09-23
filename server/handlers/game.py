from game.garbage import send_garbage
from net.client import Client


def make_callbacks(match, client):
    def on_piece_moved():
        broadcast_event(
            match,
            (
                "piece_moved",
                {
                    "board_id": client.id,
                    "row": client.board.piece.row,
                    "col": client.board.piece.col,
                    "rot": client.board.piece.rot
                },
            ),
            [client]
        )
        client.outbox.append(
            (
                "piece_moved",
                {
                    "board_id": client.id,
                    "row": client.board.piece.row,
                    "col": client.board.piece.col,
                    "rot": client.board.piece.rot,
                    "seq": client.current_input_seq
                },
            )
        )

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
        broadcast_event(match, board_update_event(client))
        for garbage_client in affected:
            broadcast_event(match, board_update_event(garbage_client))

    def on_lose():
        broadcast_event(match, ("lose", {"board_id": client.id}))

    return on_piece_moved, on_piece_killed, on_lose


def broadcast_event(match, event, exclude: list[Client] | None = None):
    for c in match.connections.values():
        if not exclude or c not in exclude:
            c.outbox.append(event)
