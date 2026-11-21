import curses

from client.menu.types import Label, Menu, TextField
from client.state.client import ClientState
from client.state.menu import MenuState
from client.ui.colors import ERROR_PAIR
from client.ui.curses import addstr_safe, center
from client.ui.logo import LOGO, LOGO_WIDTH, SUBTITLE


def resolve_label(value: Label, state: ClientState) -> str:
    return value if isinstance(value, str) else value(state)


def draw_logo(stdscr, row: int, w: int) -> int:
    center(stdscr, row, SUBTITLE)
    row += 1
    col = max((w - LOGO_WIDTH) // 2, 0)
    for pair, upper, lower in LOGO:
        addstr_safe(stdscr, row, col, upper, curses.color_pair(pair))
        addstr_safe(stdscr, row + 1, col, lower, curses.color_pair(pair))
        col += len(upper) + 1
    return row + 4


def draw_items(stdscr, row: int, w: int, menu_state: MenuState, items, labels) -> int:
    fields = [i for i in items if isinstance(i, TextField)]
    # +4 = 2 leading spaces + 2 from ljust padding
    label_width = max(map(len, labels)) + 4
    input_length = max((f.max_len for f in fields), default=0) + 1

    def field_text(item: TextField, label: str, selected: bool) -> str:
        cursor = "_" if menu_state.editing and selected else " "
        shown = "*" * len(item.value) if item.hide_chars else item.value
        value = f"{shown}{cursor}".ljust(input_length)
        return f"  {(label + ':').ljust(label_width - 3)} [{value}]  "

    if fields:
        block_width = max(
            len(field_text(i, label, False))
            for i, label in zip(items, labels, strict=True)
            if isinstance(i, TextField)
        )
    else:
        block_width = label_width
    block_col = (w - block_width) // 2

    for idx, (item, label) in enumerate(zip(items, labels, strict=True)):
        selected = idx == menu_state.selected_index
        if isinstance(item, TextField):
            text = field_text(item, label, selected)
        elif fields:
            text = label.center(block_width)
        else:
            text = f"  {label}"
        addstr_safe(
            stdscr,
            row,
            block_col,
            text.ljust(block_width),
            curses.A_REVERSE if selected else 0,
        )
        row += 1
    return row


def draw_menu(stdscr, state: ClientState):
    h, w = stdscr.getmaxyx()
    menu_state: MenuState = state.menu_state
    menu: Menu = menu_state.menu
    items = menu.items
    labels = [resolve_label(i.label, state) for i in items]

    height = (
        len(items)
        + (3 if menu.title else 0)
        + (5 if menu.show_logo else 0)
        + (3 if menu_state.message else 0)
        + (3 if menu.hint else 0)
    )
    row = (h - height) // 2

    if menu.show_logo:
        row = draw_logo(stdscr, row, w)
    if menu.title:
        center(stdscr, row, menu.title)
        row += 3

    row = draw_items(stdscr, row, w, menu_state, items, labels)

    if menu_state.message:
        attr = curses.color_pair(
            ERROR_PAIR if menu_state.message_kind == "error" else 0
        )
        center(stdscr, row + 2, f" {menu_state.message} ", attr)
        row += 2
    center(stdscr, row + 2, resolve_label(menu.hint, state), curses.A_DIM)
