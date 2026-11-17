import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

SERVER_URL = os.getenv("SERVER_URL", "console-tetris.onrender.ui.com")
SECURE = os.getenv("APP_ENV", "production") == "production"

HTTP_BASE = f"{'https' if SECURE else 'http'}://{SERVER_URL}"
WS_BASE = f"{'wss' if SECURE else 'ws'}://{SERVER_URL}"
