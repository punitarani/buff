"""cli.py"""

import asyncio

import pandas as pd
from tqdm.asyncio import tqdm

from buff.openalex import Work
from buff.openalex.models import WorkObject


async def get_papers(entity_id: str, max_depth: int = 25, max_count: int = 10000, batch_size: int = 10) -> list[WorkObject]:
    """
    Get papers from the OpenAlex API with batching, with limits on depth and count, and a customizable batch size.

    Args:
        entity_id (str): The ID of the entity for which to get papers.
        max_depth (int): Maximum depth for fetching referenced works.
        max_count (int): Maximum number of papers to fetch.
        batch_size (int): Number of requests to batch together.

    Returns:
        List[WorkObject]: A list of WorkObject instances representing papers.

    TODO: max_depth and/or max_count are not respected
    """
    papers: list[WorkObject] = []
    pending_entities = [entity_id]
    next_entities = []
    processed_entities = set()

    while (pending_entities or next_entities) and max_depth > 0 and len(papers) < max_count:
        if not pending_entities:
            pending_entities, next_entities = next_entities, []
            max_depth -= 1

        unprocessed_entities = [eid for eid in pending_entities if eid not in processed_entities]
        batches = [unprocessed_entities[i:i + batch_size] for i in range(0, len(unprocessed_entities), batch_size)]

        for batch in batches:
            # Use tqdm.gather for progress bar support
            results = await tqdm.gather(
                *(Work(eid).get() for eid in batch),
                total=len(batch),
                desc="Fetching papers"
            )

            for result in results:
                if isinstance(result, Exception):
                    print(f"Error during request: {result}")
                else:
                    papers.append(result)
                    processed_entities.add(result.id)

                    # Process results to get next entities
                    for url in result.referenced_works:
                        url = str(url)
                        if url.startswith("https://openalex.org/"):
                            next_entity_id = url[21:]
                            if next_entity_id not in processed_entities:
                                next_entities.append(next_entity_id)

                # Early exit if max_count is reached
                if len(papers) >= max_count:
                    return papers

        pending_entities = []

    return papers


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        while True:
            # Get user input for the entity ID
            _entity_id = input("Entity ID: ")

            # Get the papers
            try:
                _works = loop.run_until_complete(get_papers(_entity_id))

                # Convert list of dictionaries to a pandas DataFrame
                _papers_df = pd.DataFrame(
                    [
                        {
                            "id": str(_work.id),
                            "title": _work.title,
                        }
                        for _work in _works
                    ]
                )

                print(_papers_df)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(e)
    finally:
        loop.close()
