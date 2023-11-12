"""config.py"""

import os
from pathlib import Path

from dotenv import load_dotenv

from motor.motor_asyncio import AsyncIOMotorClient


PROJECT_PATH = Path(__file__).parent

DATA_DIR = PROJECT_PATH.joinpath("data")
if not DATA_DIR.exists():
    DATA_DIR.mkdir()


EMAIL = "email@gmail.com"

# Load .env
__loaded_env = load_dotenv(".env")
assert __loaded_env, "Could not load .env file"


# Mongo
MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_USERNAME = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
assert MONGO_HOST, "MONGO_HOST environment variable not set"
assert MONGO_DB, "MONGO_DB environment variable not set"
assert MONGO_USERNAME, "MONGO_USERNAME environment variable not set"
assert MONGO_PASSWORD, "MONGO_PASSWORD environment variable not set"

MONGO_URI = f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_DB}.{MONGO_HOST}/?retryWrites=true&w=majority"
mongo_client = AsyncIOMotorClient(MONGO_URI)


# Redis
REDIS_HOST = os.getenv("REDISHOST")
REDIS_PORT = os.getenv("REDISPORT")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
assert REDIS_HOST, "REDIS_HOST environment variable not set"
assert REDIS_PORT, "REDIS_PORT environment variable not set"
assert REDIS_PASSWORD, "REDIS_PASSWORD environment variable not set"
