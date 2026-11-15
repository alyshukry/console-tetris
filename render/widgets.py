"""Game-style curses menus: arrow keys move, Enter selects, text only inside forms."""

import curses
import textwrap
from collections.abc import Callable
from dataclasses import dataclass

from render.colors import ERROR_PAIR, PIECE_COLORS
from render.terminal import addstr_safe, enter_menu_mode

ENTER_KEYS = (curses.KEY_ENTER, 10, 13)
BACKSPACE_KEYS = (curses.KEY_BACKSPACE, 127, 8)
ESCAPE = 27

# "TETRIS" in half-blocks, one (color, top row, bottom row) per letter
_LOGO = [
    (PIECE_COLORS["Z"], "▀█▀", " █ "),
    (PIECE_COLORS["L"], "█▀▀", "██▄"),
    (PIECE_COLORS["O"], "▀█▀", " █ "),
    (PIECE_COLORS["S"], "█▀█", "█▀▄"),
    (PIECE_COLORS["I"], "█", "█"),
    (PIECE_COLORS["T"], "█▀▀", "▄▄█"),
]
_LOGO_WIDTH = sum(len(top) for _, top, _ in _LOGO) + len(_LOGO) - 1
_SUBTITLE = "C O N S O L E"


@dataclass(frozen=True)
class Field:
    label: str
    hidden: bool = False
    max_len: int = 32


def _center(stdscr, row: int, text: str, attr: int = 0):
    _, width = stdscr.getmaxyx()
    addstr_safe(stdscr, row, max((width - len(text)) // 2, 0), text, attr)


def _draw_logo(stdscr, top: int):
    _, width = stdscr.getmaxyx()
    x = max((width - _LOGO_WIDTH) // 2, 0)
    for pair, upper, lower in _LOGO:
        attr = curses.color_pair(pair)
        addstr_safe(stdscr, top, x, upper, attr)
        addstr_safe(stdscr, top + 1, x, lower, attr)
        x += len(upper) + 1


def _render(
    stdscr,
    title: str,
    rows: list[str],
    selected: int,
    *,
    message: str | None = None,
    is_error: bool = True,
    logo: bool = False,
    hint: str = "",
):
    """Draws a centered block: header, one row per option, message, hint."""
    stdscr.erase()
    height, width = stdscr.getmaxyx()

    show_logo = logo and height >= 16
    header_h = (3 + bool(title)) if show_logo else int(bool(title))
    msg_lines = textwrap.wrap(message, max(width - 4, 20)) if message else []
    row_w = max(len(r) for r in rows)

    total = header_h + 1 + len(rows) + 1 + len(msg_lines) + 1 + 1
    y = max((height - total) // 2, 0)

    if show_logo:
        _draw_logo(stdscr, y)
        _center(stdscr, y - 1, _SUBTITLE, curses.A_BOLD)
        if title:
            _center(stdscr, y + 2, title, curses.A_DIM)
    elif title:
        _center(stdscr, y, title, curses.A_BOLD)
    y += header_h + 1

    for i, row in enumerate(rows):
        attr = curses.A_REVERSE | curses.A_BOLD if i == selected else 0
        _center(stdscr, y + i, f"  {row.ljust(row_w)}  ", attr)
    y += len(rows) + 1

    msg_attr = curses.color_pair(ERROR_PAIR) | curses.A_BOLD if is_error else curses.A_DIM
    for line in msg_lines:
        _center(stdscr, y, line, msg_attr)
        y += 1
    _center(stdscr, y + 1, hint, curses.A_DIM)
    stdscr.refresh()


def busy(stdscr, text: str):
    """Shows a centered status line. Call right before a blocking request."""
    stdscr.erase()
    height, _ = stdscr.getmaxyx()
    _center(stdscr, height // 2, text, curses.A_DIM)
    stdscr.refresh()


def menu(
    stdscr,
    title: str,
    options: list[str],
    *,
    selected: int = 0,
    message: str | None = None,
    is_error: bool = True,
    logo: bool = False,
    cancellable: bool = True,
) -> int | None:
    """Returns the chosen index, or None if cancelled with Esc."""
    enter_menu_mode(stdscr)
    hint = "↑/↓ move   Enter select" + ("   Esc back" if cancellable else "")
    selected = min(selected, len(options) - 1)
    while True:
        _render(
            stdscr, title, options, selected,
            message=message, is_error=is_error, logo=logo, hint=hint,
        )  # fmt: skip
        key = stdscr.getch()
        if key == curses.KEY_UP:
            selected = (selected - 1) % len(options)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(options)
        elif key in ENTER_KEYS:
            return selected
        elif key == ESCAPE and cancellable:
            return None


def notice(stdscr, text: str, title: str = ""):
    menu(stdscr, title, ["OK"], message=text)


def _field_row(field: Field, value: str, label_w: int, value_w: int, editing: bool) -> str:
    shown = "*" * len(value) if field.hidden else value
    if editing:
        shown += "_"
    return f"{field.label.rjust(label_w)}: [{shown[-value_w:].ljust(value_w)}]"


def form(
    stdscr,
    title: str,
    fields: list[Field],
    submit_label: str,
    on_submit: Callable[[list[str]], str | None],
) -> bool:
    """Menu of fields + submit/back buttons. Enter on a field edits it.

    on_submit(values) returns an error message to show, or None on success.
    Returns True on success, False if the user went back.
    """
    enter_menu_mode(stdscr)
    n = len(fields)
    values = [""] * n
    selected = 0
    editing = False
    draft = ""
    message: str | None = None

    label_w = max(len(f.label) for f in fields)

    while True:
        _, screen_w = stdscr.getmaxyx()
        value_w = max(6, min(max(f.max_len for f in fields), 24, screen_w - label_w - 14))
        rows = [
            _field_row(f, draft if editing and i == selected else values[i], label_w, value_w,
                       editing and i == selected)
            for i, f in enumerate(fields)
        ]  # fmt: skip
        width = max(len(r) for r in rows)
        rows += [submit_label.center(width), "Back".center(width)]
        hint = (
            "type...   Enter confirm   Esc cancel"
            if editing
            else "↑/↓ move   Enter select   Esc back"
        )
        
        _render(stdscr, title, rows, selected, message=message, hint=hint)

        key = stdscr.getch()
        if editing:
            if key in ENTER_KEYS:
                values[selected] = draft
                editing = False
                selected = min(selected + 1, n)  # jump to next field / submit
            elif key == ESCAPE:
                editing = False
            elif key in BACKSPACE_KEYS:
                draft = draft[:-1]
            elif 32 <= key <= 126 and len(draft) < fields[selected].max_len:
                draft += chr(key)
            continue

        if key == curses.KEY_UP:
            selected = (selected - 1) % (n + 2)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % (n + 2)
        elif key == ESCAPE:
            return False
        elif key in ENTER_KEYS:
            if selected < n:
                editing = True
                draft = values[selected]
                message = None
            elif selected == n:
                _render(
                    stdscr, title, rows, selected,
                    message="Contacting server (may take a moment if it's asleep)...",
                    is_error=False,
                )  # fmt: skip
                message = on_submit(values)
                if message is None:
                    return True
            else:
                return False