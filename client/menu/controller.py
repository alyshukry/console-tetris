import curses

from client.menu.types import Button, MenuName, Separator, TextField


async def set_menu(state, menu_name: MenuName):
    menu_state = state.menu_state
    menu_state.editing = False
    menu_state.message = ""
    menu_state.current_menu = menu_name
    menu = menu_state.menu
    if menu.on_enter:
        await menu.on_enter(state)

    menu_state.selected_index = next(
        (i for i, item in enumerate(menu.items) if not isinstance(item, Separator)),
        None,
    )


def move(state, menu, step):
    n = len(menu.items)
    for _ in range(n):
        state.selected_index = (state.selected_index + step) % n
        if isinstance(menu.items[state.selected_index], (Button, TextField)):
            return


async def handle_menu_input(menu_state, client_state, key):
    menu = menu_state.menu
    idx = menu_state.selected_index
    if idx is None:
        return
    idx %= len(menu.items)
    item = menu.items[idx]

    if not menu_state.editing:
        if key == curses.KEY_UP:
            move(menu_state, menu, -1)
        elif key == curses.KEY_DOWN:
            move(menu_state, menu, 1)
        elif key in (curses.KEY_ENTER, 10, 13):
            if isinstance(item, TextField):
                menu_state.editing = True
            else:
                await item.action(client_state)
    else:
        if key in (curses.KEY_ENTER, 10, 13, 27):  # Enter or Esc
            if key in (curses.KEY_ENTER, 10, 13):
                menu_state.selected_index = (menu_state.selected_index + 1) % len(
                    menu.items
                )
                next_item = menu.items[menu_state.selected_index]
                menu_state.editing = isinstance(next_item, TextField)
            else:
                menu_state.editing = False
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            item.value = item.value[:-1]
        elif 32 <= key <= 126 and len(item.value) < item.max_len:
            item.value += chr(key)
