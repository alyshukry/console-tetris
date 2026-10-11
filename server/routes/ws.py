import asyncio
import itertools
import json

from websockets import ConnectionClosed, ServerConnection

from game.board import Board
from net.protocol import send_json
from server.engine.lifecycle import cancel_countdown, start_countdown
from server.engine.lobby import check_ready, handle_leave
from server.models.player import Player
from server.models.room import Room
from shared.action import Action
from shared.room_state import RoomState


async def handle_message(room, ws, data):
    player = room.connections[ws]
    match data.get("type"):
        case "input":
            tick = data.get("tick")
            seq = data.get("seq")
            try:
                action = Action(data.get("action"))
            except ValueError:
                return
            if (
                room.state == RoomState.IN_GAME
                and isinstance(tick, int)
                and isinstance(seq, int)
            ):
                room.queue_input(player, action, tick, seq)
        case "ready":
            if player.ready or room.state not in (
                RoomState.LOBBY,
                RoomState.COUNTDOWN,
            ):
                return
            player.ready = True
            room.broadcast_lobby()
            if check_ready(room) and room.countdown_task is None:
                room.countdown_task = asyncio.create_task(start_countdown(room))
        case "unready":
            if not player.ready or room.state not in (
                RoomState.LOBBY,
                RoomState.COUNTDOWN,
            ):
                return
            player.ready = False
            room.broadcast_lobby()
            await cancel_countdown(room)
        case "ping":
            await send_json(  # not going thru player's outbox to bypass delay
                ws,
                "pong",
                {"player_sent_at": data.get("sent_at"), "server_tick": room.tick},
            )


room = Room()
_player_id_counter = itertools.count()


async def handler(ws: ServerConnection):
    player_id = next(_player_id_counter)
    room.connections[ws] = Player(Board(room.shared_bag), player_id)
    room.connections[ws].outbox.append(("room_state", {"state": room.state.value}))
    room.broadcast_lobby()

    try:
        async for msg in ws:
            try:
                data = json.loads(msg)
            except json.JSONDecodeError:
                await ws.close(1003)
                return
            if not isinstance(data, dict):
                await ws.close(1003)
                return
            await handle_message(room, ws, data)
    except ConnectionClosed:
        pass
    finally:
        await handle_leave(room, ws)
