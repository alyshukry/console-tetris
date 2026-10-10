import asyncio
import logging
import time

from websockets import ConnectionClosed
from websockets.asyncio.server import ServerConnection

from game.constants import TICKS_PER_SECOND
from game.seven_bag import SevenBag
from net.protocol import send_json
from net.serialization import serialize_board
from server.handlers.game import handle_move_result
from server.handlers.input import apply_input, handle_input
from server.handlers.life_cycle import (
    cancel_countdown,
    reset_to_lobby,
    set_room_state,
    start_countdown,
)
from server.handlers.lobby import check_ready
from server.player import Player
from shared.action import Action
from shared.room_state import RoomState


class Room:
    def __init__(self):
        self.connections: dict[ServerConnection, Player] = {}
        self.state = RoomState.LOBBY

        self.shared_bag = SevenBag()
        self.tick = 0
        self.start_time = None
        self.gravity_ticks = round(0.5 * TICKS_PER_SECOND)
        self.countdown_task: asyncio.Task | None = None
        self.countdown_seconds = 5

    def all_boards_payload(self):
        return {
            "boards": {
                p.player_id: serialize_board(p.board) for p in self.connections.values()
            }
        }

    async def start_game(self):
        for player in list(self.connections.values()):
            player.outbox.append(
                (
                    "welcome_info",
                    {
                        "your_board": serialize_board(player.board),
                        "your_id": player.player_id,
                        "ticks_per_second": TICKS_PER_SECOND,
                        "gravity_ticks": self.gravity_ticks,
                        "tick": self.tick,
                    },
                )
            )
            player.outbox.append(("all_boards", self.all_boards_payload()))

        self.start_time = time.monotonic()
        await set_room_state(self, RoomState.IN_GAME)

    async def end_game(self, winners: list[Player]):
        await set_room_state(
            self, RoomState.RESULTS, {"winners": [p.player_id for p in winners]}
        )
        await asyncio.sleep(5)
        await reset_to_lobby(self)

    async def game_loop(self):
        while True:
            if self.state == RoomState.IN_GAME:
                target_ticks = int(
                    (time.monotonic() - (self.start_time or 0)) * TICKS_PER_SECOND
                )
                while self.tick < target_ticks:
                    self.tick += 1
                    alive_before = [
                        p for p in self.connections.values() if not p.board.game_over
                    ]

                    for player in alive_before:
                        if (
                            player.board.game_over
                        ):  # died earlier this tick (e.g. garbage)
                            continue
                        due = [
                            item for item in player.input_queue if item[0] <= self.tick
                        ]
                        player.input_queue = [
                            i for i in player.input_queue if i[0] > self.tick
                        ]
                        for tick, seq, action in sorted(
                            due, key=lambda item: (item[0], item[1])
                        ):
                            if (tick, seq) > (
                                player.last_processed_input_tick,
                                player.last_processed_input_seq,
                            ):
                                player.last_processed_input_tick = tick
                                player.last_processed_input_seq = seq
                            apply_input(self, player, action)

                    if self.tick % self.gravity_ticks == 0:
                        for player in alive_before:
                            if not player.board.game_over:
                                handle_move_result(
                                    self, player, player.board.move_piece_down()
                                )

                    just_died = [p for p in alive_before if p.board.game_over]
                    for p in just_died:
                        self.broadcast("lose", {"board_id": p.player_id})

                    alive_after = [p for p in alive_before if not p.board.game_over]
                    if len(alive_after) <= 1:
                        await self.end_game(alive_after or just_died)
                        break
            await asyncio.sleep(1 / TICKS_PER_SECOND)

    async def net_loop(self):
        while True:
            await asyncio.gather(
                *(flush(ws, p) for ws, p in list(self.connections.items()) if p.outbox),
                return_exceptions=True,
            )
            await asyncio.sleep(0.01)

    async def handle_message(self, ws, data):
        player = self.connections[ws]
        match data.get("type"):
            case "input":
                tick = data.get("tick")
                seq = data.get("seq")
                try:
                    action = Action(data.get("action"))
                except ValueError:
                    return
                if (
                    self.state == RoomState.IN_GAME
                    and isinstance(tick, int)
                    and isinstance(seq, int)
                ):
                    handle_input(player, action, tick, seq)
            case "ready":
                player.ready = True
                self.broadcast("player_ready", None, [player])
                if check_ready(self) and self.countdown_task is None:
                    self.countdown_task = asyncio.create_task(start_countdown(self))
            case "unready":
                player.ready = False
                self.broadcast("player_unready", None, [player])
                await cancel_countdown(self)
            case "ping":
                await send_json(  # not going thru player's outbox to bypass delay
                    ws,
                    "pong",
                    {"player_sent_at": data.get("sent_at"), "server_tick": self.tick},
                )

    def broadcast(self, msg_type: str, data=None, exclude=None):
        for p in list(self.connections.values()):
            if not exclude or p not in exclude:
                p.outbox.append((msg_type, data or {}))


async def flush(ws, player):
    msgs, player.outbox = player.outbox, []
    for t, d in msgs:
        await send_json(ws, t, d)
