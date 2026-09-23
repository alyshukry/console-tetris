def handle_welcome_info(state, data):
    state.my_id = data["your_id"]
    state.gravity = data["gravity"]

def handle_all_boards(state, data):
    state.boards = {int(k): v for k, v in data["boards"].items()}

def handle_piece_moved(state, data):
    board_id = int(data["board_id"])
    board = state.boards[board_id]

    raw_seq = data.get("seq")
    seq = int(raw_seq) if raw_seq is not None else None

    prediction = (
        state.predictions.get(seq)
        if board_id == state.my_id and seq is not None
        else None
    )

    matches = (
        prediction is not None
        and prediction["col"] == data["col"]
        and prediction["row"] == data["row"]
        and prediction["rot"] == data["rot"]
    )

    if not matches:
        board["piece"]["col"] = data["col"]
        board["piece"]["row"] = data["row"]
        board["piece"]["rot"] = data["rot"]

    if board_id == state.my_id and seq is not None:
        state.predictions.pop(seq, None)
            
    print(
        "ACK",
        "seq=", seq,
        "predicted=", prediction,
        "server=",
        data["col"],
        data["row"],
        data["rot"],
    )


def handle_piece_killed(state, data):
    board_id = int(data["board_id"])
    b = state.boards[board_id]
    b["piece"] = data["new_piece"]
    b["next_piece"] = data["next_piece"]
    b["cells"] = data["cells"]


def handle_lose(state, data):
    board_id = int(data["board_id"])
    state.boards[board_id]["game_over"] = True