def handle_welcome_info(state, data):
    state.my_id = data["your_id"]
    state.gravity = data["gravity"]

def handle_all_boards(state, data):
    state.boards = {int(k): v for k, v in data["boards"].items()}

def handle_piece_moved(state, data):
    piece = state.boards[data["board_id"]]["piece"]
    piece["rot"] = data["rot"]
    piece["col"] = data["col"]
    piece["row"] = data["row"]

def handle_piece_killed(state, data):
    b = state.boards[data["board_id"]]
    b["piece"] = data["new_piece"]
    b["next_piece"] = data["next_piece"]
    b["cells"] = data["cells"]

def handle_lose(state, data):
    state.boards[data["board_id"]]["game_over"] = True