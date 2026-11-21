import time

from client.input import apply_local_move
from client.state.client import ClientState
from client.state.game import BoardState, PlayerState
from game.collision import fits
from net.serialization import deserialize_piece


async def handle_welcome_info(state: ClientState, data):
    player_state = state.require_player_state()
    player_state.reset_room()

    player_state.my_id = data["your_id"]
    player_state.ticks_per_second = data["ticks_per_second"]
    player_state.gravity_ticks = data["gravity_ticks"]
    player_state.tick = data["tick"]
    player_state.start_time = time.monotonic()

    player_state.boards[player_state.my_id] = BoardState.from_dict(data["your_board"])


async def handle_all_boards(state: ClientState, data):
    player_state = state.require_player_state()
    player_state.boards = {
        int(player_id): BoardState.from_dict(board)
        for player_id, board in data["boards"].items()
    }


async def handle_piece_moved(state: ClientState, data):
    player_state = state.require_player_state()
    board_id = int(data["board_id"])
    board = player_state.boards[board_id]

    if board_id != player_state.my_id:
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
        player_state.pending_inputs = [
            item
            for item in player_state.pending_inputs
            if (item[0], item[1]) > (ack_input_tick, ack_input_seq)
        ]

    replay_pending(player_state, board, data["tick"])


async def handle_piece_locked(state: ClientState, data):
    player_state = state.require_player_state()
    board_id = int(data["board_id"])
    board = player_state.boards[board_id]

    board.piece = deserialize_piece(data["new_piece"])
    board.next_piece = deserialize_piece(data["next_piece"])
    board.cells = data["cells"]


async def handle_lose(state: ClientState, data):
    player_state = state.require_player_state()
    board_id = int(data["board_id"])
    player_state.boards[board_id].game_over = True


def replay_pending(state: PlayerState, board: BoardState, server_tick: int):
    pending = sorted(state.pending_inputs)
    i = 0
    for t in range(server_tick + 1, state.tick + 1):
        while i < len(pending) and pending[i][0] <= t:
            apply_local_move(board, pending[i][2])
            i += 1
        if t % state.gravity_ticks == 0 and fits(
            board.cells, board.piece, board.width, board.height, 1, 0
        ):
            board.piece.row += 1

    for _, _, key in pending[i:]:
        apply_local_move(board, key)
