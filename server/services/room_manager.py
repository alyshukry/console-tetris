from fastapi import WebSocket

from game.board import Board
from server.models.player import Player
from server.models.room import Room
from server.types import Rooms


class RoomManager:
    def __init__(self):
        self.rooms: Rooms = {}

    def get_room(self, room_id: str) -> Room | None:
        return self.rooms.get(room_id)

    def join_room(self, room_id: str, player: WebSocket) -> bool:
        room = self.rooms.get(room_id)

        if room is None:
            return False

        if len(room.connections) >= room.max_players:
            return False

        self.onboard_player(room_id, player)
        return True

    def onboard_player(self, room_id: str, ws: WebSocket) -> bool:
        room = self.rooms.get(room_id)
        if room is None:
            return False

        player_id = next(room._player_id_counter)
        room.connections[ws] = Player(Board(room.shared_bag), player_id)
        room.connections[ws].outbox.append(
            ("room_state", {"state": room.state.value})
        )
        room.broadcast_lobby()

        return True
