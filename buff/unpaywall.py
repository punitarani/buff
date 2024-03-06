"""
buff/unpaywall.py

unpaywall API wrapper
"""

import re
from pathlib import Path

import fitz
import httpx

from buff.utils import get_logger, sanitize_name, save_sanitized_name
from config import DATA_DIR, EMAIL

PAPERS_DIR = DATA_DIR.joinpath("papers")

logger = get_logger(__name__)


async def get_paper_info(doi: str) -> dict:
    """
    Get the paper info from the Unpaywall API.

    Args:
        doi (str): DOI of the paper

    Returns:
        dict: Info of the paper
    """
    request_url = f"https://api.unpaywall.org/v2/{doi}?email={EMAIL}"
    async with httpx.AsyncClient() as client:
        response = await client.get(request_url)
        if response.status_code == 200:
            return response.json()
    return {}


async def get_paper_url(doi: str) -> str | None:
    """
    Get the URL of the paper from the Unpaywall API.

    Args:
        doi (str): DOI of the paper

    Returns:
        str | None: URL of the paper or None if not found
    """
    data = await get_paper_info(doi)

    best_oa_location = data.get("best_oa_location", {})
    return best_oa_location.get("url_for_pdf", None)


async def get_paper_authors(doi: str) -> list[set[str]]:
    """
    Get the authors of the paper from the Unpaywall API.

    Args:
        doi (str): DOI of the paper

    Returns:
        list[set[str]]: List of authors of the paper
    """
    data = await get_paper_info(doi)
    return data.get("z_authors", [])


async def download_paper(doi: str) -> Path | None:
    """
    Download the paper from the Unpaywall API.

    Args:
        doi (str): DOI of the paper

    Returns:
        Path | None: Path to the downloaded paper or None if not found
    """

    # Handle the case where the DOI is not found
    if doi is None:
        return None

    # Remove the prefix "https://doi.org/" from the DOI
    if doi.startswith("https://doi.org/"):
        doi = doi[16:]
    elif doi.startswith("http://doi.org/"):
        doi = doi[15:]
    elif doi.startswith("doi.org/"):
        doi = doi[8:]

    filename = sanitize_name(doi)
    filepath = PAPERS_DIR.joinpath("pdf", filename + ".pdf")

    # If the file already exists, return it
    if filepath.exists():
        logger.info(f"Paper already downloaded: {doi}")
        return filepath

    # Save the sanitized name
    save_sanitized_name(text=doi, name=filename)

    url = await get_paper_url(doi)
    if url is None:
        return None

    return await download_pdf(doi, filepath)


async def download_pdf(doi: str, filepath: Path) -> Path | None:
    """
    Download the PDF of the paper from the Unpaywall API.

    Args:
        doi (str): DOI of the paper
        filepath (Path): Path to save the PDF

    Returns:
        str | None: Path to the downloaded PDF or None if not found
    """

    url = await get_paper_url(doi)
    if url is None:
        return None

    timeout = httpx.Timeout(60.0, connect=60.0)

    for i in range(3):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, follow_redirects=True)
                content_type = response.headers.get("Content-Type", "")

                # Check MIME type and PDF signature
                if content_type == "application/pdf" or response.content.startswith(
                    b"%PDF-"
                ):
                    with open(filepath, "wb") as f:
                        f.write(response.content)
                    return filepath
                else:
                    logger.debug(
                        f"Attempt {i + 1}: Content is not a PDF. MIME type: {content_type}"
                    )

        except httpx.RequestError as e:
            logger.debug(
                f"Attempt {i + 1}: An error occurred while requesting {url}: {e}"
            )
    logger.error(f"Error downloading paper: {doi}")

    return None


def extract_text(fp: Path) -> str:
    """
    Extract text from a PDF file.

    Args:
        fp (Path): Path to the PDF file

    Returns:
        str: Extracted text from the PDF file
    """

    text = ""
    try:
        with fitz.open(fp) as doc:
            for page in doc:
                page_text = page.get_text()
                text += clean_text(page_text) + " "  # Add a space between pages' text
    except Exception as e:
        logger.error(f"Failed to extract text from {fp}: {e}")
        return ""

    return text.strip()


def clean_text(text: str) -> str:
    """
    Basic text cleaning to remove excessive whitespace.

    Args:
        text (str): Text to clean

    Returns:
        str: Cleaned text
    """
    return re.sub("\s+", " ", text).strip()
