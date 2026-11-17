import os

from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv("APP_ENV")
SERVER_URL = os.getenv("SERVER_URL")