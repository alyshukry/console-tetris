
import asyncio
import time

from client.state.game import PlayerState
from game.collision import fits


async def gravity_loop(player_state: PlayerState):
    while True:
        await asyncio.sleep(0.01)
        target_ticks = int(
            (time.monotonic() - player_state.start_time) * player_state.ticks_per_second
        )
        while player_state.tick < target_ticks:
            player_state.tick += 1
            if player_state.tick % player_state.gravity_ticks == 0:
                for board in player_state.boards.values():
                    if not board.game_over and fits(
                        board.cells,
                        board.piece,
                        board.width,
                        board.height,
                        1,
                        0,
                    ):
                        board.piece.row += 1

