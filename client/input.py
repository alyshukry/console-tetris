import asyncio
from net.protocol import send_json


async def input_loop(ws, stdscr, state):
    while True:
        key = stdscr.getch()
        if key == ord("k"):
            await send_json(ws, "unready" if state.ready else "ready")
            state.ready = not state.ready
            state.ready_count += 1 if state.ready else -1
        if key != -1:
            await send_json(ws, "input", {"key": key})
        await asyncio.sleep(0.05)
