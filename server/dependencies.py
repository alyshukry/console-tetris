from fastapi import Request, WebSocket

from server.services.room_manager import RoomManager


def get_room_manager(request: Request) -> RoomManager:
    return request.state.room_manager


def get_websocket_room_manager(ws: WebSocket) -> RoomManager:
    return ws.state.room_manager
