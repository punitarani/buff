"""config.py"""

import os
from pathlib import Path

from motor.motor_asyncio import AsyncIOMotorClient

PROJECT_PATH = Path(__file__).parent

DATA_DIR = PROJECT_PATH.joinpath("data")
if not DATA_DIR.exists():
    DATA_DIR.mkdir()

EMAIL = "email@gmail.com"
