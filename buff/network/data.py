"""buff/network/data.py"""

import asyncio

from tqdm import tqdm

from buff.openalex import Work
from buff.openalex.utils import parse_id_from_url


async def build_network_around_work(
    entity_id: str, depth: int = 3, limit: int = 100, batch_size: int = 10
) -> tuple[set, set]:
    """
    Build a network around a given work, including both citations and references,
    using batching and controlled concurrency with a specified batch size.

    Args:
        entity_id (str): The ID of the entity for which to build the network.
        depth (int): Maximum depth for fetching citations and references.
        limit (int): Maximum number of citations/references to fetch per work.
        batch_size (int): Number of pairs of citations and references to process concurrently.

    Returns:
        tuple[set, set]: A tuple where the first element is a set of nodes (works),
                         and the second element is a set of edges (citations and references).
    """
    nodes = set()
    edges = set()

    queue = asyncio.Queue()
    await queue.put((entity_id, 0))

    total_items_processed = 0
    max_items = 1  # Initial assumption, will increase as we add more items to the queue

    with tqdm(total=max_items, desc="Processing", dynamic_ncols=True) as pbar:
        while not queue.empty():
            batch_tasks = []
            for _ in range(batch_size):
                if queue.empty():
                    break
                current_work, current_depth = await queue.get()
                if current_depth <= depth:
                    batch_tasks.append(
                        asyncio.create_task(
                            get_citations_and_references(
                                current_work, current_depth, limit
                            )
                        )
                    )

            results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    continue  # Skipping any tasks that resulted in an exception

                current_work, current_depth, citations_ids, references_ids = result

                # Update max_items and progress bar after obtaining the ids
                if current_depth < depth:
                    max_items += len(citations_ids[:limit]) + len(
                        references_ids[:limit]
                    )
                    pbar.total = max_items
                pbar.set_description(
                    f"Depth: {current_depth} | Processed: {total_items_processed}/{max_items}"
                )
                pbar.update(1)

                # Process citations and references
                for citation_id in citations_ids[:limit]:
                    nodes.add(citation_id)
                    edges.add((current_work, citation_id))
                    if current_depth < depth:
                        await queue.put(
                            (parse_id_from_url(citation_id), current_depth + 1)
                        )

                for reference_id in references_ids[:limit]:
                    nodes.add(reference_id)
                    edges.add((reference_id, current_work))
                    if current_depth < depth:
                        await queue.put(
                            (parse_id_from_url(reference_id), current_depth + 1)
                        )

                total_items_processed += 1

    return nodes, edges


async def get_citations_and_references(work_id, depth, limit) -> tuple:
    """
    Fetch citations and references for a given work.
    """
    try:
        citations_task = asyncio.create_task(Work(work_id).citations(limit=limit))
        references_task = asyncio.create_task(Work(work_id).references(limit=limit))
        citations_result, references_result = await asyncio.gather(
            citations_task, references_task
        )

        citations_ids, _ = citations_result
        references_ids, _ = references_result

        return work_id, depth, citations_ids, references_ids

    except Exception as e:
        print(f"Error fetching data for work {work_id}: {e}")
        return work_id, depth, [], []


async def get_citations_recursively(
    entity_id: str, depth: int = 3, limit: int = 100
) -> list[dict[str, str]]:
    """
    Recursively fetches citations for a specified work and its citations up to a given depth.

    This function retrieves the citations of a work identified by `entity_id` and then
    recursively fetches citations for each of those citations. This process is repeated
    up to the specified depth.

    Args:
        entity_id (str): The ID of the work for which to fetch citations.
        depth (int): The maximum depth of recursion for fetching citations.
                     Depth 0 means no recursive fetching, just the citations of the initial work.
        limit (int): The maximum number of citations to fetch for each work.

    Returns:
        list[dict]: A list of dictionaries, each representing a citation. Each dictionary includes
                    the citation details and a key 'child_citations' which is a list of citations
                    for that particular work, fetched recursively up to the specified depth.
    """
    if depth == 0:
        return []

    citations_ids, citations_works = await Work(entity_id=entity_id).citations(
        limit=limit
    )
    result = []
    for citation_id in citations_ids:
        citation = citations_works[citation_id]
        citation_dict = citation.model_dump()
        child_citations = await get_citations_recursively(citation_id, depth - 1, limit)
        citation_dict["child_citations"] = child_citations
        result.append(citation_dict)

    return result


async def get_references_recursively(
    entity_id: str, depth: int = 3, limit: int = 100
) -> list[dict]:
    """
    Recursively fetches references for a specified work and its references up to a given depth.

    This function retrieves the references of a work identified by `entity_id` and then
    recursively fetches references for each of those references. This process is repeated
    up to the specified depth.

    Args:
        entity_id (str): The ID of the work for which to fetch references.
        depth (int): The maximum depth of recursion for fetching references.
                     Depth 0 means no recursive fetching, just the references of the initial work.
        limit (int): The maximum number of references to fetch for each work.

    Returns:
        list[dict]: A list of dictionaries, each representing a reference. Each dictionary includes
                    the reference details and a key 'child_references' which is a list of references
                    for that particular work, fetched recursively up to the specified depth.
    """
    if depth == 0:
        return []

    references_ids, references_works = await Work(entity_id=entity_id).references(
        limit=limit
    )
    result = []
    for reference_id in references_ids:
        reference = references_works[reference_id]
        reference_dict = reference.model_dump()
        child_references = await get_references_recursively(
            reference_id, depth - 1, limit
        )
        reference_dict["child_references"] = child_references
        result.append(reference_dict)

    return result
