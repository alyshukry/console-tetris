import asyncio
from dataclasses import dataclass
from enum import Enum

from client.state.session import Session

from client.state.menu import MenuState

from client.state.game import PlayerState

class Screen(Enum):
    MENU = "menu"
    ROOM = "room"


@dataclass
class ClientState():
    menu_state: MenuState
    player_state: PlayerState | None = None
    screen: Screen = Screen.MENU
    session: Session | None = None
    room_task: asyncio.Task | None = None

    def require_session(self) -> Session:
        if self.session is None:
            raise RuntimeError("Not logged in")
        return self.session
    
    def require_player_state(self) -> PlayerState:
        if self.player_state is None:
            raise RuntimeError("Not in a game")
        return self.player_state