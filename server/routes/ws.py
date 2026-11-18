import asyncio
import logging

from fastapi import APIRouter, WebSocket
from pydantic import ValidationError
from websockets import InvalidMessage

from net.protocol import encode
from server.dependencies import CurrentUserDep, RoomManagerDep
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


logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws")
async def ws_endpoint(
    ws: WebSocket,
    *,
    host: Username,
    password: str | None = None,
    room_manager: RoomManagerDep,
    user: CurrentUserDep,
):
    await ws.accept()
    room = None

    try:
        room = await asyncio.to_thread(
            room_manager.authorize_join, host, password, user.user_id
        )
        room_manager.attach_player(room, ws, user.user_id)
        async for raw in ws.iter_text():
            try:
                msg = parse_client_message(raw)
            except ValidationError:
                raise InvalidMessage() from None
            await handle_message(room, ws, msg)
    except AppError as e:
        await ws.close(code=e.ws_code, reason=e.detail)
    except Exception:
        logger.exception("Websocket error for user %s", user.user_id)
        await close(ws, code=1011, reason="Internal server error")
    finally:
        if room is not None:
            await handle_leave(room, ws, room_manager)


async def close(ws: WebSocket, code: int, reason: str):
    try:
        await ws.close(code=code, reason=reason[:120])
    except Exception:
        pass
