import asyncio
import curses

from client.menu.types import TextField

from client.menu.controller import move
from websockets import ClientConnection

from client.state.client import ClientState, Screen
from client.state.game import BoardState
from game.collision import fits
from game.piece import Piece
from net.protocol import encode
from shared.action import Action
from shared.room_state import RoomState


async def input_loop(stdscr, state: ClientState):
    while True:
        key = stdscr.getch()
        if state.screen == Screen.MENU or (Screen.ROOM and not RoomState.IN_GAME):
            if state.menu_state.editing:
                handle_text_input(state.menu_state, key)
            else:
                await handle_menu_input(state.menu_state, state, key)
        elif state.screen == Screen.ROOM and RoomState.IN_GAME:
            player_state = state.require_player_state()
            if key == ord("k"):
                await player_state.ws.send(
                    encode("unready" if player_state.ready else "ready")
                )
            if player_state.room_state == RoomState.IN_GAME and key in (
                curses.KEY_LEFT,
                curses.KEY_RIGHT,
                curses.KEY_UP,
                curses.KEY_DOWN,
                ord(" "),
            ):
                if player_state.my_id in player_state.boards:
                    apply_local_move(player_state.boards[player_state.my_id], key)
                tick = player_state.tick
                seq = player_state.input_seq_by_tick.get(tick, 0)
                player_state.pending_inputs.append((tick, seq, key))
                player_state.input_seq_by_tick[tick] = seq + 1
                await player_state.ws.send(
                    encode(
                        "input",
                        {"action": key_to_action(key), "tick": tick, "seq": seq},
                    )
                )
        await asyncio.sleep(0.025)


def key_to_action(key) -> Action | None:
    return {
        curses.KEY_LEFT: Action.LEFT,
        curses.KEY_RIGHT: Action.RIGHT,
        curses.KEY_UP: Action.ROTATE,
        curses.KEY_DOWN: Action.SOFT_DROP,
        ord(" "): Action.DROP,
    }.get(key)


def apply_local_move(board: BoardState, key):
    if not board.game_over:
        piece: Piece = board.piece
        w, h, cells = board.width, board.height, board.cells

        if key == curses.KEY_LEFT:
            if fits(cells, piece, w, h, 0, -1):
                piece.col -= 1
        elif key == curses.KEY_RIGHT:
            if fits(cells, piece, w, h, 0, 1):
                piece.col += 1
        elif key == curses.KEY_UP:
            new_rot = (piece.rot + 1) % 4
            if fits(cells, piece, w, h, 0, 0, rot=new_rot):
                piece.rot = new_rot
        elif key == curses.KEY_DOWN:
            if fits(cells, piece, w, h, 1, 0):
                piece.row += 1
        elif key == ord(" "):
            while fits(cells, piece, w, h, 1, 0):
                piece.row += 1


def handle_text_input(menu_state, key):
    menu = menu_state.menu
    item = menu.items[menu_state.selected_index % len(menu.items)]
    menu.hint = "type    Enter finish    Esc cancel"
    if key in (curses.KEY_ENTER, 10, 13, 27):  # Enter or Esc
        if key in (curses.KEY_ENTER, 10, 13):
            menu_state.selected_index = (menu_state.selected_index + 1) % len(
                menu.items
            )
        next_item = menu.items[menu_state.selected_index]
        menu_state.editing = isinstance(next_item, TextField)
    elif key in (curses.KEY_BACKSPACE, 127, 8):
        item.value = item.value[:-1]
    elif 32 <= key <= 126 and len(item.value) < item.max_len:
        item.value += chr(key)


async def handle_menu_input(menu_state, client_state, key):
    menu = menu_state.menu
    item = menu.items[menu_state.selected_index % len(menu.items)]
    menu.hint = "↑/↓ move    Enter select"
    if key == curses.KEY_UP:
        move(menu_state, menu, -1)
    elif key == curses.KEY_DOWN:
        move(menu_state, menu, 1)
    elif key in (curses.KEY_ENTER, 10, 13):
        if isinstance(item, TextField):
            menu_state.editing = True
        else:
            await item.action(client_state)
