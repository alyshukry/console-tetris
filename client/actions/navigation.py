from client.menu.controller import set_menu
from client.menu.types import MenuName
from client.state.client import ClientState


async def quit_app(state: ClientState):
    raise SystemExit


def go_to(menu_name: MenuName):
    async def action(state: ClientState):
        await set_menu(state, menu_name)

    return action
