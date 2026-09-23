import asyncio
from enum import Enum, auto

from websockets.asyncio.server import ServerConnection

from net.client import Client
from net.protocol import broadcast_json, send_json
from server.handlers.input import handle_input
from server.handlers.lobby import (
    check_ready,
    start_countdown,
    cancel_countdown,
    reset_to_lobby,
)
from server.handlers.game_events import make_callbacks
from server.match_state import MatchState, set_match_state


class Match:
    def __init__(self):
        self.connections: dict[ServerConnection, Client] = {}
        self.state = MatchState.LOBBY
        from game.seven_bag import SevenBag

        self.shared_bag = SevenBag()
        self.gravity = 0.5
        self.countdown_task: asyncio.Task | None = None
        self.countdown_seconds = 5

    def all_boards_payload(self):
        return {"boards": {c.id: c.board.to_dict() for c in self.connections.values()}}

    async def start_game(self):
        for client in self.connections.values():
            (
                client.board.on_piece_moved,
                client.board.on_piece_killed,
                client.board.on_lose,
            ) = make_callbacks(self, client)

        for ws, client in self.connections.items():
            await send_json(
                ws,
                "welcome_info",
                {
                    "your_board": client.board.to_dict(),
                    "your_id": client.id,
                    "gravity": self.gravity,
                },
            )
            await send_json(ws, "all_boards", self.all_boards_payload())

        await set_match_state(self, MatchState.IN_GAME)

    async def end_game(self, winners: list[Client]):
        await set_match_state(self, MatchState.RESULTS, {"winners": [c.id for c in winners]})
        await asyncio.sleep(5)
        await reset_to_lobby(self)

    async def game_loop(self):
        while True:
            if self.state == MatchState.IN_GAME:
                alive_before = [
                    c for c in self.connections.values() if not c.board.game_over
                ]
                for client in alive_before:
                    client.board.move_piece_down()
                just_died = [c for c in alive_before if c.board.game_over]
                alive_after = [c for c in alive_before if not c.board.game_over]
                if len(alive_after) <= 1:
                    await self.end_game(alive_after if alive_after else just_died)
            await asyncio.sleep(self.gravity)

    async def net_loop(self):
        while True:
            tasks = []
            for ws, client in list(self.connections.items()):
                if client.outbox:
                    for e in client.outbox:
                        tasks.append(send_json(ws, msg_type=e[0], data=e[1]))
                    client.outbox.clear()
            if tasks:
                await asyncio.gather(*tasks)
            await asyncio.sleep(0.01)

    async def handle_message(self, ws, data):
        client = self.connections[ws]
        match data.get("type"):
            case "input":
                handle_input(client, data.get("key"))
            case "ready":
                client.ready = True
                await broadcast_json(self, "player_ready", None, [ws])
                if check_ready(self) and self.countdown_task is None:
                    self.countdown_task = asyncio.create_task(start_countdown(self))
            case "unready":
                client.ready = False
                await broadcast_json(self, "player_unready", None, [ws])
                await cancel_countdown(self)
