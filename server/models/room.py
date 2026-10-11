import asyncio

from websockets.asyncio.server import ServerConnection

from game.constants import TICKS_PER_SECOND
from game.seven_bag import SevenBag
from server.config import GRAVITY_IN_SECONDS
from server.models.player import Player
from shared.action import Action
from shared.room_state import RoomState


class Room:
    def __init__(self):
        self.connections: dict[ServerConnection, Player] = {}
        self.state = RoomState.LOBBY

        self.shared_bag = SevenBag()
        self.tick = 0
        self.start_time = None
        self.gravity_ticks = round(GRAVITY_IN_SECONDS * TICKS_PER_SECOND)
        self.countdown_task: asyncio.Task | None = None

    def queue_input(self, player: Player, action: Action, tick: int, seq: int):
        if player.board.game_over:
            return
        if len(player.input_queue) < 50:
            player.input_queue.append((tick, seq, action))

    def broadcast_lobby(self):
        player_count = len(self.connections)
        ready_count = sum(p.ready for p in self.connections.values())
        for p in self.connections.values():
            p.outbox.append(
                (
                    "lobby_update",
                    {
                        "player_count": player_count,
                        "ready_count": ready_count,
                        "you_ready": p.ready,
                    },
                )
            )

    def broadcast(self, msg_type: str, data=None, exclude=None):
        for p in list(self.connections.values()):
            if not exclude or p not in exclude:
                p.outbox.append((msg_type, data or {}))
