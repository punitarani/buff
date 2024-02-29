"""buff/utils.py"""


def sanitize_name(text: str) -> str:
    """
    Sanitizes a string for use as a filename.
    Replace any non-alphanumeric characters with underscores.

    Args:
        text (str): The input string to sanitize.

    Returns:
        str: A sanitized, file-safe name.
    """
    return "".join(c if c.isalnum() else "_" for c in text)
