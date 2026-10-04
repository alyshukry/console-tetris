import time

from client.input import apply_local_move
from client.state.board import BoardState
from client.state.client import ClientState


def handle_welcome_info(state: ClientState, data):
    state.reset_match()
    
    state.my_id = data["your_id"]
    state.ticks_per_second = data["ticks_per_second"]
    state.gravity_ticks = data["gravity_ticks"]
    state.tick = data["tick"]
    state.start_time = time.monotonic()

    state.boards[state.my_id] = BoardState.from_dict(data["your_board"])


def handle_all_boards(state: ClientState, data):
    state.boards = {
        int(player_id): BoardState.from_dict(board)
        for player_id, board in data["boards"].items()
    }


def handle_piece_moved(state, data):
    board_id = int(data["board_id"])
    board = state.boards[board_id]

    if board_id != state.my_id:
        board.piece.col = data["col"]
        board.piece.row = data["row"]
        board.piece.rot = data["rot"]
        return

    ack_input_tick = data.get("ack_input_tick")
    ack_input_seq = data.get("ack_input_seq")

    board.piece.col = data["col"]
    board.piece.row = data["row"]
    board.piece.rot = data["rot"]

    if ack_input_tick is not None and ack_input_seq is not None:
        state.pending_inputs = [
            item for item in state.pending_inputs
            if (item[0], item[1]) > (ack_input_tick, ack_input_seq)
        ]

    for tick, seq, key in sorted(state.pending_inputs):
        apply_local_move(board, key)


from net.serialization import deserialize_piece


def handle_piece_locked(state: ClientState, data):
    board_id = int(data["board_id"])
    board = state.boards[board_id]

    board.piece = deserialize_piece(data["new_piece"])
    board.next_piece = deserialize_piece(data["next_piece"])
    board.cells = data["cells"]


def handle_lose(state, data):
    board_id = int(data["board_id"])
    state.boards[board_id].game_over = True
