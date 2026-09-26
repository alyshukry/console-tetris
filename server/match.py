import asyncio
import time

from websockets.asyncio.server import ServerConnection
from server.player import Player
from net.protocol import broadcast_json, send_json
from server.handlers.input import handle_input, apply_input
from server.handlers.lobby import (
    check_ready,
    start_countdown,
    cancel_countdown,
    reset_to_lobby,
)
from server.handlers.game import make_callbacks
from shared.match_state import MatchState, set_match_state
from game.constants import TICKS_PER_SECOND


class Match:
    def __init__(self):
        self.connections: dict[ServerConnection, Player] = {}
        self.state = MatchState.LOBBY
        from game.seven_bag import SevenBag

        self.shared_bag = SevenBag()
        self.tick = 0
        self.start_time = None
        self.gravity_ticks = round(0.5 * TICKS_PER_SECOND)
        self.countdown_task: asyncio.Task | None = None
        self.countdown_seconds = 5

    def all_boards_payload(self):
        return {"boards": {p.id: p.board.to_dict() for p in self.connections.values()}}

    async def start_game(self):
        for ws, player in self.connections.items():
            await send_json(
                ws,
                "welcome_info",
                {
                    "your_board": player.board.to_dict(),
                    "your_id": player.id,
                    "ticks_per_second": TICKS_PER_SECOND,
                    "gravity_ticks": self.gravity_ticks,
                    "tick": self.tick,
                },
            )
            await send_json(ws, "all_boards", self.all_boards_payload())

        self.start_time = time.monotonic()
        await set_match_state(self, MatchState.IN_GAME)

    async def end_game(self, winners: list[Player]):
        await set_match_state(
            self, MatchState.RESULTS, {"winners": [p.id for p in winners]}
        )
        await asyncio.sleep(5)
        await reset_to_lobby(self)

    async def game_loop(self):
        while True:
            if self.state == MatchState.IN_GAME:
                target_ticks = int(
                    (time.monotonic() - (self.start_time or 0)) * TICKS_PER_SECOND
                )
                while self.tick < target_ticks:
                    self.tick += 1

                    for player in self.connections.values():
                        if player.board.game_over:
                            continue
                        due = [
                            item for item in player.input_queue if item[0] <= self.tick
                        ]
                        player.input_queue = [
                            item for item in player.input_queue if item[0] > self.tick
                        ]
                        for tick, action in sorted(due, key=lambda item: item[0]):
                            player.last_processed_input_tick = max(
                                player.last_processed_input_tick,
                                tick,
                            )
                            apply_input(player, action)

                    if self.tick % self.gravity_ticks == 0:
                        alive_before = [
                            p
                            for p in self.connections.values()
                            if not p.board.game_over
                        ]
                        for player in alive_before:
                            player.board.move_piece_down()
                        just_died = [p for p in alive_before if p.board.game_over]
                        alive_after = [p for p in alive_before if not p.board.game_over]
                        if len(alive_after) <= 1:
                            await self.end_game(
                                alive_after if alive_after else just_died
                            )
                            break
            await asyncio.sleep(1 / TICKS_PER_SECOND)

    async def net_loop(self):
        while True:
            tasks = []
            for ws, player in list(self.connections.items()):
                if player.outbox:
                    for e in player.outbox:
                        tasks.append(send_json(ws, msg_type=e[0], data=e[1]))
                    player.outbox.clear()
            if tasks:
                await asyncio.gather(*tasks)
            await asyncio.sleep(0.01)

    async def handle_message(self, ws, data):
        player = self.connections[ws]
        match data.get("type"):
            case "input":
                handle_input(player, data.get("action"), data.get("tick"))
            case "ready":
                player.ready = True
                await broadcast_json(self, "player_ready", None, [ws])
                if check_ready(self) and self.countdown_task is None:
                    self.countdown_task = asyncio.create_task(start_countdown(self))
            case "unready":
                player.ready = False
                await broadcast_json(self, "player_unready", None, [ws])
                await cancel_countdown(self)
            case "ping":
                await send_json(
                    ws,
                    "pong",
                    {"player_sent_at": data.get("sent_at"), "server_tick": self.tick},
                )
