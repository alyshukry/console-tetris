import time

from client.input import apply_local_move


def handle_welcome_info(state, data):
    state.my_id = data["your_id"]
    state.ticks_per_second = data["ticks_per_second"]
    state.gravity_ticks = data["gravity_ticks"]
    state.start_time = time.monotonic()

def handle_all_boards(state, data):
    state.boards = {int(k): v for k, v in data["boards"].items()}

def handle_piece_moved(state, data):
    board_id = int(data["board_id"])
    board = state.boards[board_id]

    if board_id != state.my_id:
        board["piece"]["col"] = data["col"]
        board["piece"]["row"] = data["row"]
        board["piece"]["rot"] = data["rot"]
        return

    server_tick = data.get("tick")
    ack_input_tick = data.get("ack_input_tick")

    board["piece"]["col"] = data["col"]
    board["piece"]["row"] = data["row"]
    board["piece"]["rot"] = data["rot"]

    if ack_input_tick is not None:
        for tick in list(state.pending_inputs):
            if tick <= ack_input_tick:
                del state.pending_inputs[tick]

    for t in sorted(state.pending_inputs):
        apply_local_move(board, state.pending_inputs[t])


def handle_piece_killed(state, data):
    board_id = int(data["board_id"])
    b = state.boards[board_id]
    b["piece"] = data["new_piece"]
    b["next_piece"] = data["next_piece"]
    b["cells"] = data["cells"]


def handle_lose(state, data):
    board_id = int(data["board_id"])
    state.boards[board_id]["game_over"] = True