from game.garbage import calc_garbage
from net.serialization import serialize_board
from server.models.player import Player


def handle_move_result(room, player: Player, result):
    if result.moved:
        room.broadcast(
            "piece_moved",
            {
                "board_id": player.player_id,
                "row": player.board.piece.row,
                "col": player.board.piece.col,
                "rot": player.board.piece.rot,
            },
            [player],
        )
        player.outbox.append(
            (
                "piece_moved",
                {
                    "board_id": player.player_id,
                    "row": player.board.piece.row,
                    "col": player.board.piece.col,
                    "rot": player.board.piece.rot,
                    "tick": room.tick,
                    "ack_input_tick": player.last_processed_input_tick,
                    "ack_input_seq": player.last_processed_input_seq,
                },
            )
        )

    if result.locked:
        garbage = {}
        if result.lines_cleared > 0:
            recipients = [
                p.player_id
                for p in room.connections.values()
                if p.player_id != player.player_id and not p.board.game_over
            ]
            garbage = calc_garbage(recipients, result.lines_cleared)

        msg_type, data = board_update_event(player)
        room.broadcast(msg_type, data)
        for recipient_id, amount in garbage.items():
            recipient_player = next(
                p for p in room.connections.values() if p.player_id == recipient_id
            )
            recipient_player.board.add_garbage(amount)
            msg_type, data = board_update_event(recipient_player)
            room.broadcast(msg_type, data)


def board_update_event(p: Player):
    d = serialize_board(p.board)
    return "piece_locked", {
        "board_id": p.player_id,
        "cells": d.get("cells"),
        "new_piece": d.get("piece"),
        "next_piece": d.get("next_piece"),
    }
