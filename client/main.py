import asyncio
import websockets
import curses

from render.curses_render import setup_curses


def main(stdscr):
    setup_curses(stdscr)

    async def run_client():
        async with websockets.connect("ws://localhost:8888") as ws:
            print("connected")
            await ws.send("hello server")
            
            async def input_loop():
                while True:
                    key = stdscr.getch()
                    if key != -1: await ws.send(str({"input": key}))

                    await asyncio.sleep(0.05)

            async def receive_loop():
                async for msg in ws:
                    print(f"from server: ${msg}")

            await asyncio.gather(input_loop(), receive_loop())
    asyncio.run(run_client())


curses.wrapper(main)
