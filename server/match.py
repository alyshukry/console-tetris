import asyncio
from enum import Enum, auto

from websockets.asyncio.server import ServerConnection

from game.board import Board
from game.garbage import send_garbage
from game.seven_bag import SevenBag
from net.client import Client
from net.protocol import broadcast_json, send_json
from server.handlers import handle_input


class MatchState(Enum):
    WAITING = auto()  # lobby, waiting for ready-ups
    COUNTDOWN = auto()  # everyone is ready, countdown started
    IN_PROGRESS = auto()  # game_loop/net_loop active
    RESULTS = auto()  # someone won, results shown


class Match:
    def __init__(self):
        self.connections: dict[ServerConnection, Client] = {}
        self.state = MatchState.WAITING
        self.shared_bag = SevenBag()
        self.gravity = 0.5  # how long each gravity tick takes
        self.countdown_task: asyncio.Task | None = None
        self.countdown_seconds = 5

    def all_boards_payload(self):
        return {"boards": {c.id: c.board.to_dict() for c in self.connections.values()}}

    def check_ready(self) -> bool:
        if (
            self.state == MatchState.WAITING
            and self.connections
            and all(c.ready for c in self.connections.values())
        ):
            return True
        else:
            return False

    def make_callbacks(self, client: Client):
        def on_piece_moved():
            event = (
                "piece_moved",
                {
                    "board_id": client.id,
                    "row": client.board.piece.row,
                    "col": client.board.piece.col,
                    "rot": client.board.piece.rot,
                },
            )
            for c in self.connections.values():
                c.outbox.append(event)

        def on_piece_killed(lines: int):
            affected = []
            if lines > 0:
                affected = send_garbage(client, list(self.connections.values()), lines)

            event = (
                "piece_killed",
                {
                    "board_id": client.id,
                    "cells": client.board.to_dict().get("cells"),
                    "new_piece": client.board.to_dict().get("piece"),
                    "next_piece": client.board.to_dict().get("next_piece"),
                },
            )
            for c in self.connections.values():
                c.outbox.append(event)

            for garbage_client in affected:
                garbage_event = (
                    "piece_killed",  # reuse same event type
                    {
                        "board_id": garbage_client.id,
                        "cells": garbage_client.board.to_dict().get("cells"),
                        "new_piece": garbage_client.board.to_dict().get("piece"),
                        "next_piece": garbage_client.board.to_dict().get("next_piece"),
                    },
                )
                for c in self.connections.values():
                    c.outbox.append(garbage_event)

        def on_lose():
            event = (
                "lose",
                {"board_id": client.id},
            )
            for c in self.connections.values():
                c.outbox.append(event)

        return on_piece_moved, on_piece_killed, on_lose

    async def start_game(self):
        for client in self.connections.values():
            on_moved, on_killed, on_lose = self.make_callbacks(client)
            client.board.on_piece_moved = on_moved
            client.board.on_piece_killed = on_killed
            client.board.on_lose = on_lose

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

        self.state = MatchState.IN_PROGRESS
        await broadcast_json(self, "match_state", {"state": self.state.value})

    async def start_countdown(self):
        self.state = MatchState.COUNTDOWN
        await broadcast_json(self, "match_state", {"state": self.state.value})

        try:
            for remaining in range(self.countdown_seconds, 0, -1):
                await broadcast_json(self, "countdown_tick", {"seconds": remaining})
                await asyncio.sleep(1)
            await self.start_game()
        except asyncio.CancelledError:
            self.state = MatchState.WAITING
            await broadcast_json(
                self,
                "match_state",
                {
                    "state": self.state.value,
                    "player_count": len(self.connections),
                    "ready_count": sum(c.ready for c in self.connections.values()),
                },
            )
        finally:
            self.countdown_task = None

    async def cancel_countdown(self):
        if self.countdown_task is not None:
            self.countdown_task.cancel()
            try:
                await self.countdown_task
            except asyncio.CancelledError:
                pass

    async def end_game(self, winners: list[Client]):
        self.state = MatchState.RESULTS
        winner_ids = [c.id for c in winners]
        await broadcast_json(
            self, "match_state", {"state": self.state.value, "winners": winner_ids}
        )
        await asyncio.sleep(5)
        await self.reset_to_lobby()
        
    async def reset_to_lobby(self):
        for client in self.connections.values():
            client.ready = False
            self.shared_bag = SevenBag()
            client.board = Board(self.shared_bag)

        self.state = MatchState.WAITING
        await broadcast_json(
            self, "match_state",
            {
                "state": self.state.value,
                "player_count": len(self.connections),
                "ready_count": 0,
            },
        )

    async def game_loop(self):
        while True:
            if self.state == MatchState.IN_PROGRESS:
                alive_before = [
                    c for c in self.connections.values() if not c.board.game_over
                ]

                for client in alive_before:
                    client.board.move_piece_down()

                just_died = [c for c in alive_before if c.board.game_over]
                alive_after = [c for c in alive_before if not c.board.game_over]

                if len(alive_after) <= 1:
                    winners = (
                        alive_after if alive_after else just_died
                    )  # two or more players can lose in the same tick
                    await self.end_game(winners)

            await asyncio.sleep(self.gravity)

    async def net_loop(self):
        while True:
            for ws, client in list(self.connections.items()):
                if client.outbox:
                    for e in client.outbox:
                        await send_json(ws, type=e[0], data=e[1])
                    client.outbox.clear()
            await asyncio.sleep(0.01)

    # remove this later and make client send match id when sending stuff
    async def handle_message(self, ws, data):
        client = self.connections[ws]
        match data.get("type"):
            case "input":
                handle_input(client, data.get("key"))
            case "ready":
                client.ready = True
                await broadcast_json(self, "player_ready", None, [ws])
                if self.check_ready() and self.countdown_task is None:
                    self.countdown_task = asyncio.create_task(self.start_countdown())
            case "unready":
                client.ready = False
                await broadcast_json(self, "player_unready", None, [ws])
                await self.cancel_countdown()
