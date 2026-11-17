from client.ui.colors import PIECE_COLORS

LOGO = [
    (PIECE_COLORS["Z"], "▀█▀", " █ "),
    (PIECE_COLORS["L"], "█▀▀", "██▄"),
    (PIECE_COLORS["O"], "▀█▀", " █ "),
    (PIECE_COLORS["S"], "█▀█", "█▀▄"),
    (PIECE_COLORS["I"], "█", "█"),
    (PIECE_COLORS["T"], "█▀▀", "▄▄█"),
]
LOGO_WIDTH = sum(len(top) for _, top, _ in LOGO) + len(LOGO) - 1
SUBTITLE = "C O N S O L E"
