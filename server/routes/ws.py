import asyncio
import json

from fastapi import APIRouter, WebSocket

from net.protocol import encode
from server.engine.lifecycle import cancel_countdown, start_countdown
from server.engine.lobby import check_ready, handle_leave
from server.types import Username
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
            await ws.send_text(
                encode(  # not going thru player's outbox to bypass delay
                    "pong",
                    {"player_sent_at": data.get("sent_at"), "server_tick": room.tick},
                )
            )


router = APIRouter()


@router.websocket("/ws")
async def ws_endpoint(ws: WebSocket, host: Username, password_hash: str | None = None):
    await ws.accept()

    room_manager = ws.app.state.room_manager
    room = room_manager.get_room(host)

    if room is None:
        await ws.close(code=1008, reason="Room not found")
        return
    if room.password_hash is not None and password_hash != room.password_hash:
        await ws.close(code=1008, reason="Incorrect password")
        return

    if not room_manager.join_room(host, ws):
        await ws.close(code=1008, reason="Unable to join room")
        return

    try:
        async for msg in ws.iter_text():
            try:
                data = json.loads(msg)
            except json.JSONDecodeError:
                await ws.close(code=1003)
                return

            if not isinstance(data, dict):
                await ws.close(code=1003)
                return

            await handle_message(room, ws, data)
    finally:
        await handle_leave(room, ws)
