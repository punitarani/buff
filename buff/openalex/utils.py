"""buff.openalex.utils.py"""

from pydantic import HttpUrl

from .errors import OpenAlexError


def parse_id_from_url(url: str | HttpUrl) -> str:
    """
    Parse the ID from an OpenAlex URL
    Parses Work, Author, Institution, and Source IDs.

    Args:
        url (str | HttpUrl): OpenAlex URL

    Returns:
        str: OpenAlex ID
    """
    url = str(url)
    if url.startswith("https://openalex.org/"):
        url = url[21:]
        if url[0] in ["W", "A", "I", "S"]:
            return url
    raise OpenAlexError("Invalid OpenAlex URL")
