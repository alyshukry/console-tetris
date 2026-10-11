import asyncio

from net.protocol import send_json
from server.engine.lifecycle import cancel_countdown, start_countdown
from server.engine.lobby import check_ready
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