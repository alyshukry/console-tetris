import asyncio
from typing import TypeAlias

from fastapi import WebSocket

from game.board import Board
from server.engine.loop import run_room
from server.errors import (
    AlreadyInRoom,
    RoomFull,
    RoomInProgress,
    RoomNameTaken,
    RoomNotFound,
    WrongPassword,
)
from server.models.player import Player
from server.models.room import Room
from server.security import hash_password, verify_password
from shared.room_state import RoomState

Rooms: TypeAlias = dict[str, Room]


class RoomManager:
    def __init__(self):
        self.rooms: Rooms = {}
        self.player_rooms: dict[int, str] = {}

    def _check_joinable(self, room: Room):
        if room.state != RoomState.LOBBY:
            raise RoomInProgress()
        if len(room.connections) >= room.max_players:
            raise RoomFull()

    def authorize_join(self, host: str, password: str | None, user_id: int) -> Room:
        room = self.rooms.get(host)
        if room is None:
            raise RoomNotFound()
        if user_id in self.player_rooms:
            raise AlreadyInRoom()
        self.check_password(room, password)
        self._check_joinable(room)
        return room

    def attach_player(self, room: Room, ws: WebSocket, user_id: int) -> Player:
        self._check_joinable(room)
        self.player_rooms[user_id] = room.host
        player = Player(Board(room.shared_bag), user_id)
        room.connections[ws] = player
        player.outbox.append(("room_state", {"state": room.state.value}))
        room.broadcast_lobby()
        return player

    def get_room(self, room_id: str) -> Room | None:
        return self.rooms.get(room_id)

    def list_rooms(self) -> list[Room]:
        return list(self.rooms.values())

    async def create_room(self, host: str, password: str | None = None):
        if host in self.rooms:
            raise RoomNameTaken()
        room = Room(
            host,
            (
                await asyncio.to_thread(hash_password, password)
                if password is not None
                else None
            ),
        )
        room.task = asyncio.create_task(run_room(room))
        self.rooms[host] = room
        return room

    def check_password(self, room: Room, password: str | None):
        if room.password_hash and not verify_password(
            password or "", room.password_hash
        ):
            raise WrongPassword()

    async def delete_room(self, room_id: str):
        try:
            room = self.rooms.pop(room_id)
        except KeyError:
            raise RoomNotFound() from None

        room.task.cancel()
        try:
            await room.task
        except asyncio.CancelledError:
            pass
