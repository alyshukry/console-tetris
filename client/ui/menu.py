import curses

from client.menu.types import Menu, TextField
from client.state.menu import MenuState
from client.ui.colors import ERROR_PAIR
from client.ui.logo import LOGO, LOGO_WIDTH, SUBTITLE


def center(stdscr, y: int, text: str, attr=0):
    h, w = stdscr.getmaxyx()
    x = (w - len(text)) // 2
    stdscr.addstr(y, x, text, attr)


def draw_menu(stdscr, menu: Menu, state: MenuState):
    stdscr.clear()
    h, w = stdscr.getmaxyx()

    button_count = len(menu.buttons)
    menu_height = (
        button_count
        + (3 if menu.title else 0)
        + (5 if menu.show_logo else 0)
        + (3 if state.message else 0)
        + (3 if menu.hint else 0)
    )
    y = (h - menu_height) // 2

    if menu.show_logo:
        center(stdscr, y, SUBTITLE)
        y += 1
        x = max((w - LOGO_WIDTH) // 2, 0)
        for pair, upper, lower in LOGO:
            stdscr.addstr(y, x, upper, curses.color_pair(pair))
            stdscr.addstr(y + 1, x, lower, curses.color_pair(pair))
            x += len(upper) + 1
        y += 4

    if menu.title:
        center(stdscr, y, menu.title)
        y += 3

    has_fields = any(isinstance(i, TextField) for i in menu.buttons)
    label_width = (
        max(len(i.label) for i in menu.buttons) + 4
    )  # + 4 to include the 2 spaces added before the label and the 2 spaces created by .ljust()
    input_length = TextField.max_len + 1

    def field_text(item, selected):
        cursor = "_" if state.editing and selected else " "
        displayed_value = "*" * len(item.value) if item.hide_chars else item.value
        value = f"{displayed_value}{cursor}".ljust(input_length)
        return f"  {(item.label + ':').ljust(label_width - 3)} [{value}]  "

    if has_fields:
        block_width = max(
            len(field_text(i, False)) for i in menu.buttons if isinstance(i, TextField)
        )
    else:
        block_width = label_width

    block_x = (w - block_width) // 2

    for idx, item in enumerate(menu.buttons):
        selected = idx == state.selected_index
        attr = curses.A_REVERSE if selected else 0

        if isinstance(item, TextField):
            text = field_text(item, selected)
        elif has_fields:
            text = item.label.center(block_width)
        else:
            text = f"  {item.label}".ljust(block_width)

        stdscr.addstr(y, block_x, text.ljust(block_width), attr)
        y += 1

    if state.message:
        center(
            stdscr,
            y + 2,
            f" {state.message} ",
            curses.color_pair(ERROR_PAIR if state.message_kind == "error" else 0),
        )
        y += 2

    center(stdscr, y + 2, menu.hint, curses.A_DIM)

    stdscr.refresh()
