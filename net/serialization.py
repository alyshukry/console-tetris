from dataclasses import asdict

from game.board import Board
from game.piece import Piece


def serialize_piece(piece: Piece) -> dict:
    return asdict(piece)


def serialize_board(board: Board) -> dict:
    return {
        "cells": board.cells,
        "width": board.width,
        "height": board.height,
        "piece": serialize_piece(board.piece),
        "next_piece": {
            "shape": board.bag.get(board.piece_index + 1),
            "row": 0,
            "col": 0,
            "rot": 0,
        },
        "game_over": board.game_over,
    }


def deserialize_piece(data: dict) -> Piece:
    return Piece(shape=data["shape"], row=data["row"], col=data["col"], rot=data["rot"])
