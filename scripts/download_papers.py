"""scripts/download_papers.py"""

import json

from tqdm import tqdm

from buff.network.download import download_papers
from buff.openalex import Work
from buff.utils import sanitize_name
from config import DATA_DIR, PAPERS_DIR

PAPERS_TXT_DIR = PAPERS_DIR.joinpath("txt")
NETWORK_FP = DATA_DIR.joinpath("network.json")
WORKS_FP = DATA_DIR.joinpath("works.json")

with open(NETWORK_FP, "r", encoding="utf-8") as f:
    WORKS = json.load(f).get("nodes", [])


async def map_work_id_to_doi(works: list[str]) -> dict[str, str]:
    """
    Map work IDs to DOIs

    Args:
        works (list[str]): List of work IDs

    Returns:
        dict[str, str]: Dictionary mapping work IDs to DOIs
    """

    work_doi = {}
    for work_id in tqdm(works, desc="Mapping"):
        work = await Work(work_id).data
        doi = str(work.doi)

        # Check if the txt file exists
        if doi:
            if doi.startswith("https://doi.org/"):
                doi = doi[16:]
            if doi.startswith("http://doi.org/"):
                doi = doi[15:]
            elif doi.startswith("doi.org/"):
                doi = doi[8:]

            filename = sanitize_name(doi) + ".txt"
            filepath = PAPERS_DIR.joinpath("txt", filename)
            if filepath.exists():
                work_doi[work_id] = doi

    return work_doi


if __name__ == "__main__":
    import asyncio

    print(f"Downloading {len(WORKS)} papers")
    downloaded = asyncio.run(download_papers(works=WORKS))

    print("Mapping work IDs to DOIs")
    work_dois = asyncio.run(map_work_id_to_doi(WORKS))

    print("Saving to file works.json")
    with open(WORKS_FP, "w", encoding="utf-8") as work_file:
        json.dump(work_dois, work_file, indent=2)
