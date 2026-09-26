import time

from client.input import apply_local_move
from client.state.client import ClientState


def handle_welcome_info(state: ClientState, data):
    state.my_id = data["your_id"]
    state.ticks_per_second = data["ticks_per_second"]
    state.gravity_ticks = data["gravity_ticks"]
    state.tick = data["tick"]
    state.start_time = time.monotonic()


def handle_all_boards(state: ClientState, data):
    state.boards = {int(k): v for k, v in data["boards"].items()}


def handle_piece_moved(state, data):
    board_id = int(data["board_id"])
    board = state.boards[board_id]

    if board_id != state.my_id:
        board.piece.col = data["col"]
        board.piece.row = data["row"]
        board.piece.rot = data["rot"]
        return

    server_tick = data.get("tick")
    ack_input_tick = data.get("ack_input_tick")

    board.piece.col = data["col"]
    board.piece.row = data["row"]
    board.piece.rot = data["rot"]

    if ack_input_tick is not None:
        state.pending_inputs = [
            item for item in state.pending_inputs if item[0] > ack_input_tick
        ]

    for tick, seq, key in sorted(state.pending_inputs):
        apply_local_move(board, key)


def handle_piece_killed(state, data):
    board_id = int(data["board_id"])
    b = state.boards[board_id]
    b.piece = data["new_piece"]
    b.next_piece = data["next_piece"]
    b.cells = data["cells"]


def handle_lose(state, data):
    board_id = int(data["board_id"])
    state.boards[board_id].game_over = True
