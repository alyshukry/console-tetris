import asyncio

from fastapi import APIRouter, WebSocket
from pydantic import ValidationError

from net.protocol import encode
from server.dependencies import RoomManagerDep
from server.engine.lifecycle import cancel_countdown, start_countdown
from server.engine.lobby import check_ready, handle_leave
from server.errors import AppError
from server.schemas.common import Username
from server.schemas.messages import (
    ClientMessage,
    InputMsg,
    PingMsg,
    ReadyMsg,
    UnreadyMsg,
    parse_client_message,
)
from shared.room_state import RoomState


async def handle_message(room, ws, msg: ClientMessage):
    player = room.connections[ws]
    match msg:
        case InputMsg():
            if room.state == RoomState.IN_GAME:
                room.queue_input(player, msg.action, msg.tick, msg.seq)
        case ReadyMsg():
            if player.ready or room.state not in (
                RoomState.LOBBY,
                RoomState.COUNTDOWN,
            ):
                return
            player.ready = True
            room.broadcast_lobby()
            if check_ready(room) and room.countdown_task is None:
                room.countdown_task = asyncio.create_task(start_countdown(room))
        case UnreadyMsg():
            if not player.ready or room.state not in (
                RoomState.LOBBY,
                RoomState.COUNTDOWN,
            ):
                return
            player.ready = False
            room.broadcast_lobby()
            await cancel_countdown(room)
        case PingMsg():
            await ws.send_text(  # not going thru player's outbox to bypass delay
                encode(
                    "pong", {"player_sent_at": msg.sent_at, "server_tick": room.tick}
                )
            )


router = APIRouter()


@router.websocket("/ws")
async def ws_endpoint(
    ws: WebSocket,
    *,
    host: Username,
    password: str | None = None,
    room_manager: RoomManagerDep,
):
    await ws.accept()

    try:
        room = await asyncio.to_thread(room_manager.authorize_join, host, password)
        room_manager.attach_player(room, ws)
    except AppError as e:
        await ws.close(code=1008, reason=e.detail)
        return

    try:
        async for raw in ws.iter_text():
            try:
                msg = parse_client_message(raw)
            except ValidationError:
                await ws.close(code=1003)
                return
            await handle_message(room, ws, msg)
    finally:
        await handle_leave(room, ws, room_manager)
