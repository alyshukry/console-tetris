import curses

from client.ui.curses import center

from client.menu.types import Menu, TextField
from client.state.menu import MenuState
from client.ui.colors import ERROR_PAIR
from client.ui.logo import LOGO, LOGO_WIDTH, SUBTITLE


def draw_menu(stdscr, menu_state: MenuState):
    h, w = stdscr.getmaxyx()
    menu = menu_state.menu

    item_count = len(menu.items)
    menu_height = (
        item_count
        + (3 if menu.title else 0)
        + (5 if menu.show_logo else 0)
        + (3 if menu_state.message else 0)
        + (3 if menu.hint else 0)
    )
    row = (h - menu_height) // 2

    if menu.show_logo:
        center(stdscr, row, SUBTITLE)
        row += 1
        col = max((w - LOGO_WIDTH) // 2, 0)
        for pair, upper, lower in LOGO:
            stdscr.addstr(row, col, upper, curses.color_pair(pair))
            stdscr.addstr(row + 1, col, lower, curses.color_pair(pair))
            col += len(upper) + 1
        row += 4

    if menu.title:
        center(stdscr, row, menu.title)
        row += 3

    has_fields = any(isinstance(i, TextField) for i in menu.items)
    label_width = (
        max(len(i.label) for i in menu.items) + 4
    )  # + 4 to include the 2 spaces added before the label and the 2 spaces created by .ljust()
    input_length = TextField.max_len + 1

    def field_text(item, selected):
        cursor = "_" if menu_state.editing and selected else " "
        displayed_value = "*" * len(item.value) if item.hide_chars else item.value
        value = f"{displayed_value}{cursor}".ljust(input_length)
        return f"  {(item.label + ':').ljust(label_width - 3)} [{value}]  "

    if has_fields:
        block_width = max(
            len(field_text(i, False)) for i in menu.items if isinstance(i, TextField)
        )
    else:
        block_width = label_width

    block_col = (w - block_width) // 2

    for idx, item in enumerate(menu.items):
        selected = idx == menu_state.selected_index
        attr = curses.A_REVERSE if selected else 0

        if isinstance(item, TextField):
            text = field_text(item, selected)
        elif has_fields:
            text = item.label.center(block_width)
        else:
            text = f"  {item.label}".ljust(block_width)

        stdscr.addstr(row, block_col, text.ljust(block_width), attr)
        row += 1

    if menu_state.message:
        center(
            stdscr,
            row + 2,
            f" {menu_state.message} ",
            curses.color_pair(ERROR_PAIR if menu_state.message_kind == "error" else 0),
        )
        row += 2

    center(stdscr, row + 2, menu.hint, curses.A_DIM)
