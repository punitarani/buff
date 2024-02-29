"""config.py"""

from pathlib import Path

PROJECT_PATH = Path(__file__).parent

DATA_DIR = PROJECT_PATH.joinpath("data")
if not DATA_DIR.exists():
    DATA_DIR.mkdir()

LOGS_DIR = PROJECT_PATH.joinpath("logs")
if not LOGS_DIR.exists():
    LOGS_DIR.mkdir()


EMAIL = "email@gmail.com"
