"""buff/utils.py"""

import pandas as pd

from config import DATA_DIR

SANITIZED_NAMES_FP = DATA_DIR.joinpath("sanitized_names.csv")
SANITIZED_NAMES_FP.touch(exist_ok=True)


def sanitize_name(text: str) -> str:
    """
    Sanitizes a string for use as a filename.
    Replace any non-alphanumeric characters with underscores.

    Args:
        text (str): The input string to sanitize.

    Returns:
        str: A sanitized, file-safe name.
    """
    name = "".join(c if c.isalnum() else "_" for c in text)
    save_sanitized_name(text, name)
    return name


def save_sanitized_name(text: str, name: str) -> None:
    """
    Save a sanitized name to a file in the data directory.

    Args:
        text (str): The original text.
        name (str): The sanitized name.
    """

    # Read the existing data, or create a new DataFrame if the file is empty
    try:
        df = pd.read_csv(SANITIZED_NAMES_FP, encoding="utf-8")
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=["text", "name"])

    # Check for duplicates based on both `text` and `name`
    if not ((df["text"] == text) & (df["name"] == name)).any():
        # Append without reading the entire file again
        df_new = pd.DataFrame([[text, name]], columns=["text", "name"])
        df_new.to_csv(
            SANITIZED_NAMES_FP, mode="a", header=False, index=False, encoding="utf-8"
        )


def get_original_text(name: str) -> str | None:
    """
    Retrieves the original text given a sanitized name.

    Args:
        name (str): The sanitized name.

    Returns:
        str: The original text corresponding to the sanitized name if found, else None.
    """
    try:
        df = pd.read_csv(SANITIZED_NAMES_FP, encoding="utf-8")
        match = df[df["name"] == name]
        if not match.empty:
            return match.iloc[0]["text"]
    except pd.errors.EmptyDataError:
        pass
    return None
