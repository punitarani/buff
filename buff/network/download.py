"""buff/network.py"""

import asyncio
from typing import Optional

from buff.openalex import Work
from buff.unpaywall import download_paper, extract_text, PAPERS_DIR
from config import DATA_DIR

OA_FP = DATA_DIR.joinpath("oa.txt")
NO_OA_FP = DATA_DIR.joinpath("no_oa.txt")
PAPERS_TXT_DIR = PAPERS_DIR.joinpath("txt")

# Ensure the directories exist
PAPERS_TXT_DIR.mkdir(parents=True, exist_ok=True)


async def download_papers(works: list[str], max_concurrent_downloads: int = 10) -> list[str]:
    """
    Download the papers concurrently

    Args:
        works (list[str]): List of work IDs to download
        max_concurrent_downloads (int): Maximum number of concurrent downloads (default: 10)

    Returns:
        list[str]: List of work IDs that were successfully downloaded
    """

    try:
        with open(NO_OA_FP, "r", encoding="utf-8") as no_oa_file:
            NO_OA = no_oa_file.read().splitlines()
    except FileNotFoundError:
        # Create the file if it does not exist
        NO_OA_FP.touch()
        NO_OA = []

    semaphore = asyncio.Semaphore(max_concurrent_downloads)

    async def download_paper_with_semaphore(work_id: str) -> Optional[str]:
        """
        Download a paper with semaphore control

        This function acquires the semaphore before calling the `download_paper_wrapper`
        function to limit the number of concurrent downloads.

        Args:
            work_id (str): The work ID of the paper to download

        Returns:
            Optional[str]: The work ID if the paper is successfully downloaded,
                None otherwise
        """
        async with semaphore:
            return await download_paper_wrapper(work_id)

    async def download_paper_wrapper(work_id: str) -> Optional[str]:
        """
        Wrapper function to download a paper

        Retrieves the work data, checks the DOI, and downloads the paper.
        It extracts the text from the downloaded paper and saves it as a text file.

        Args:
            work_id (str): The work ID of the paper to download

        Returns:
            Optional[str]: The work ID if the paper is successfully downloaded,
                None otherwise
        """
        work = await Work(work_id).data

        doi = str(work.doi)
        if doi is None:
            print(f"Work has no DOI: {work_id}")
            return None

        # Remove the prefix "https://doi.org/" from the DOI
        if doi.startswith("https://doi.org/"):
            doi = doi[16:]
        elif doi.startswith("doi.org/"):
            doi = doi[8:]

        # If the work is not open access, skip it
        if doi in NO_OA:
            print(f"Work not open access: {work_id}")
            return None

        fp = await download_paper(str(work.doi))

        # Handle the case where the paper is not found
        if fp is None:
            print(f"Paper not found for work: {work_id}")

            # Add the work to the list of works that are not open access
            with open(NO_OA_FP, "a", encoding="utf-8") as no_oa_txt:
                no_oa_txt.write(f"{work_id}\n")

            return None

        # Extract the text from the paper
        text = extract_text(fp)

        # Replace the pdf to txt in the file path string
        txt_fp = str(fp).replace("pdf", "txt")
        with open(txt_fp, "w", encoding="utf-8") as txt_file:
            txt_file.write(text)

        print(f"Downloaded paper for work: {work_id}")

        # Add the work to the list of works that are open access
        with open(OA_FP, "a", encoding="utf-8") as oa_file:
            oa_file.write(f"{work_id}\n")

        return work_id

    # Use asyncio.gather to run the downloads concurrently
    download_tasks = [download_paper_with_semaphore(work_id) for work_id in works]
    results = await asyncio.gather(*download_tasks)

    downloaded = [result for result in results if result is not None]

    return downloaded
