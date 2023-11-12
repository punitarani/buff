"""buff/network/data.py"""

import asyncio

from buff.openalex import Work
from buff.openalex.utils import parse_id_from_url


async def build_network_around_work(
    entity_id: str, depth: int = 3, limit: int = 100, max_concurrent_requests: int = 10
) -> tuple[set, set]:
    """
    Build a network around a given work,
    including both citations and references,
    using batching and controlled concurrency.

    Args:
        entity_id (str): The ID of the entity for which to build the network.
        depth (int): Maximum depth for fetching citations and references.
        limit (int): Maximum number of citations/references to fetch per work.
        max_concurrent_requests (int): Maximum number of concurrent requests.

    Returns:
        tuple[set, set]: A tuple where the first element is a set of nodes (works),
                         and the second element is a set of edges (citations and references).
    """
    nodes = set()
    edges = set()
    semaphore = asyncio.Semaphore(max_concurrent_requests)

    async def process_work(work_id: str, current_depth: int) -> None:
        """
        Process a work and its citations/references recursively.

        Args:
            work_id (str): The ID of the work to process.
            current_depth (int): The current depth of the recursion.

        Returns:
            None, but adds nodes and edges to the global sets.
        """
        if current_depth > depth:
            return

        async with semaphore:
            citations_task = asyncio.create_task(Work(work_id).citations(limit=limit))
            references_task = asyncio.create_task(Work(work_id).references(limit=limit))
            citations_result, references_result = await asyncio.gather(
                citations_task, references_task
            )

        # Unpack results for citations and references
        citations_ids, citations_works = citations_result
        references_ids, references_works = references_result

        tasks = []
        for citation_id in citations_ids:
            nodes.add(citation_id)
            edges.add((work_id, citation_id))
            if current_depth + 1 <= depth:
                tasks.append(process_work(citation_id, current_depth + 1))

        for reference_id in references_ids:
            nodes.add(reference_id)
            edges.add((reference_id, work_id))
            if current_depth + 1 <= depth:
                tasks.append(process_work(reference_id, current_depth + 1))

        if tasks:
            await asyncio.gather(*tasks)

    # Start processing with the initial work
    nodes.add(entity_id)
    await process_work(entity_id, 1)

    return nodes, edges


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
