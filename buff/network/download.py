"""buff/network.py"""

import asyncio

from tqdm import tqdm

from buff.openalex import Work
from buff.unpaywall import download_paper, extract_text
from config import DATA_DIR


async def download_papers(works: list[str]) -> list[str]:
    """
    Download the papers

    Args:
        works (list[str]): List of work IDs to download

    Returns:
        list[str]: List of work IDs that were successfully downloaded
    """

    with open(DATA_DIR.joinpath("no_oa.txt"), "r", encoding="utf-8") as f:
        NO_OA = f.read().splitlines()

    downloaded = []
    for work_id in tqdm(works, desc="Downloading papers"):
        work = await Work(work_id).data

        doi = work.doi
        if doi is None:
            print(f"Work has no DOI: {work_id}")
            continue

        # Remove the prefix "https://doi.org/" from the DOI
        if doi.startswith("https://doi.org/"):
            doi = doi[16:]
        elif doi.startswith("doi.org/"):
            doi = doi[8:]

        # If the work is not open access, skip it
        if doi in NO_OA:
            print(f"Work not open access: {work_id}")
            continue

        fp = await download_paper(work.doi)

        # Handle the case where the paper is not found
        if fp is None:
            print(f"Paper not found for work: {work_id}")

            # Add the work to the list of works that are not open access
            with open(DATA_DIR.joinpath("no_oa.txt"), "a", encoding="utf-8") as f:
                f.write(f"{work_id}\n")

            continue

        # Extract the text from the paper
        text = extract_text(fp)

        # Replace the pdf to txt in the file path string
        txt_fp = str(fp).replace("pdf", "txt")
        with open(txt_fp, "w", encoding="utf-8") as f:
            f.write(text)

        downloaded.append(work_id)
        print(f"Downloaded paper for work: {work_id}")

    return downloaded
