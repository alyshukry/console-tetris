from game.garbage import calc_garbage
from server.player import Player


def make_callbacks(match, player):
    def on_piece_moved():
        broadcast_event(
            match,
            (
                "piece_moved",
                {
                    "board_id": player.id,
                    "row": player.board.piece.row,
                    "col": player.board.piece.col,
                    "rot": player.board.piece.rot
                },
            ),
            [player]
        )
        player.outbox.append(
            (
                "piece_moved",
                {
                    "board_id": player.id,
                    "row": player.board.piece.row,
                    "col": player.board.piece.col,
                    "rot": player.board.piece.rot,
                    "tick": match.tick,
                    "ack_input_tick": player.last_processed_input_tick,
                },
            )
        )

    def board_update_event(p):
        d = p.board.to_dict()
        return (
            "piece_killed",
            {
                "board_id": p.id,
                "cells": d.get("cells"),
                "new_piece": d.get("piece"),
                "next_piece": d.get("next_piece"),
            },
        )

    def on_piece_killed(lines: int):
        garbage = {}
        if lines > 0:
            recipients = [
                p.id for p in match.connections.values()
                if p.id != player.id and not p.board.game_over
            ]
            garbage = calc_garbage(recipients, lines)

        broadcast_event(match, board_update_event(player))
        for recipient_id, amount in garbage.items():
            recipient_player = next(
                p for p in match.connections.values() if p.id == recipient_id
            )
            recipient_player.board.add_garbage(amount)
            broadcast_event(match, board_update_event(recipient_player))

    def on_lose():
        broadcast_event(match, ("lose", {"board_id": player.id}))

    return on_piece_moved, on_piece_killed, on_lose


def broadcast_event(match, event, exclude: list[Player] | None = None):
    for p in match.connections.values():
        if not exclude or p not in exclude:
            p.outbox.append(event)