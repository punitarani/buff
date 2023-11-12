"""config.py"""

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_PATH = Path(__file__).parent

DATA_DIR = PROJECT_PATH.joinpath("data")
if not DATA_DIR.exists():
    DATA_DIR.mkdir()


EMAIL = "email@gmail.com"

# Load .env
__loaded_env = load_dotenv(".env")
assert __loaded_env, "Could not load .env file"


# Redis
REDIS_HOST = os.getenv("REDISHOST")
REDIS_PORT = os.getenv("REDISPORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
assert REDIS_HOST, "REDIS_HOST environment variable not set"
assert REDIS_PORT, "REDIS_PORT environment variable not set"
assert REDIS_PASSWORD, "REDIS_PASSWORD environment variable not set"
