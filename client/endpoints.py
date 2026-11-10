DEFAULT_SERVER = "https://console-tetris.onrender.com"  # replace with your real Render host


def endpoints(server: str) -> tuple[str, str]:
    if "://" not in server:
        host = server.split(":")[0]
        local = host in ("localhost", "127.0.0.1") or host.startswith(("192.168.", "10."))
        server = ("http://" if local else "https://") + server
    http = server.rstrip("/")
    return http, "ws" + http[4:]  # http -> ws, https -> wss