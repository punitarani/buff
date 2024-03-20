"""scripts/embed_papers.py"""

import json

from buff.llm.embed import embed_texts
from buff.llm.models import Document, DocumentMetadata
from buff.llm.split import split_text
from buff.openalex import Work
from buff.store.vector import pc_papers
from buff.utils import sanitize_name
from config import DATA_DIR, PAPERS_DIR

PAPERS_TXT_DIR = PAPERS_DIR.joinpath("txt")
NETWORK_FP = DATA_DIR.joinpath("network.json")
WORKS_FP = DATA_DIR.joinpath("works.json")
EMBEDDED_WORKS_FP = DATA_DIR.joinpath("embedded_works.txt")

with open(NETWORK_FP, "r", encoding="utf-8") as network_file:
    WORKS = json.load(network_file).get("nodes", [])


async def process_paper(work_id: str) -> None:
    """Process a paper"""
    print(f"Processing: {work_id}")

    # Check if the work ID has already been embedded
    with open(EMBEDDED_WORKS_FP, "a+") as f:
        f.seek(0)
        embedded_works = f.read().splitlines()

    if work_id in embedded_works:
        print(f"Work already embedded: {work_id}")
        return

    work = await Work(work_id).data
    doi = str(work.doi)
    filename = sanitize_name(doi) + ".txt"
    txt_fp = PAPERS_TXT_DIR.joinpath(filename)

    if not txt_fp.exists():
        print(f"TXT not found: {work_id} - {doi}")
        return

    with open(txt_fp, "r", encoding="utf-8") as f:
        text = f.read()

    # Split the text
    chunks = split_text(text)

    # Embed the chunks
    embeds = await embed_texts(texts=chunks, input_type="search_document")

    # Build the documents
    documents = [
        Document(
            id=f"{work_id}#{i}",
            values=embed,
            metadata=DocumentMetadata(
                index=i,
                work_id=work_id,
                doi=doi,
                text=chunk
            ),
        )
        for i, (chunk, embed) in enumerate(zip(chunks, embeds))
    ]

    # Convert the documents to JSON
    docs = [doc.model_dump(mode="json") for doc in documents]

    # Upsert the documents into the vector database
    pc_papers.upsert(docs, namespace="papers")

    # Write the work ID to the embedded works file
    with open(EMBEDDED_WORKS_FP, "a") as f:
        f.write(f"{work_id}\n")


async def main():
    """main function"""
    semaphore = asyncio.Semaphore(10)  # Allow up to 10 concurrent tasks

    async def process_paper_with_semaphore(work_id: str) -> None:
        async with semaphore:
            await process_paper(work_id)

    tasks = [process_paper_with_semaphore(work) for work in WORKS]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
