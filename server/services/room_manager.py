import asyncio
from typing import TypeAlias

from fastapi import WebSocket

from game.board import Board
from server.engine.loop import run_room
from server.models.player import Player
from server.models.room import Room
from server.schemas.common import Username
from shared.room_state import RoomState


Rooms: TypeAlias = dict[str, Room]

class RoomManager:
    def __init__(self):
        self.rooms: Rooms = {}

    def get_room(self, room_id: str) -> Room | None:
        return self.rooms.get(room_id)

    def create_room(self, host: Username, password_hash: str | None = None) -> bool:
        if self.rooms.get(host) is None:
            self.rooms[host] = Room(
                host, password_hash if password_hash is not None else None
            )
            self.rooms[host].task = asyncio.create_task(run_room(self.rooms[host]))
            return True
        return False

    async def delete_room(self, room_id: str):
        room = self.rooms.pop(room_id)
        if room is not None:
            room.task.cancel()
            try:
                await room.task
            except asyncio.CancelledError:
                pass

    def join_room(self, room_id: str, player: WebSocket) -> bool:
        room = self.rooms.get(room_id)

        if room is None:
            return False
        if len(room.connections) >= room.max_players:
            return False
        if room.state != RoomState.LOBBY:
            return False

        self.onboard_player(room_id, player)
        return True

    def onboard_player(self, room_id: str, ws: WebSocket) -> bool:
        room = self.rooms.get(room_id)
        if room is None:
            return False

        player_id = next(room._player_id_counter)
        room.connections[ws] = Player(Board(room.shared_bag), player_id)
        room.connections[ws].outbox.append(("room_state", {"state": room.state.value}))
        room.broadcast_lobby()

        return True
