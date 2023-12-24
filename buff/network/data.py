"""buff/network/data.py"""

import asyncio

from tqdm import tqdm

from buff.openalex import Work
from buff.openalex.models import WorkObject
from buff.openalex.utils import parse_id_from_url


async def build_network_around_work(
    entity_id: str, depth: int = 3, limit: int = 100
) -> tuple[set, set]:
    """
    Build a network around a given work, including both citations and references,
    using batching and controlled concurrency with a specified batch size.

    Args:
        entity_id (str): The ID of the entity for which to build the network.
        depth (int): Maximum depth for fetching citations and references.
        limit (int): Maximum number of citations/references to fetch per work.

    Returns:
        tuple[set, set]: A tuple where the first element is a set of nodes (works),
                         and the second element is a set of edges (citations and references).
    """
    nodes = set()
    edges = set()

    queue = asyncio.Queue()
    await queue.put((entity_id, 0))

    with tqdm(desc="Processing", dynamic_ncols=True) as pbar:
        while not queue.empty():
            current_work, current_depth = await queue.get()
            citations, references = await get_citations_and_references(
                current_work, depth - current_depth, limit
            )

            for citation in citations:
                citation_id = citation["id"]
                nodes.add(citation_id)
                edges.add((current_work, citation_id))
                if current_depth < depth:
                    await queue.put((citation_id, current_depth + 1))

            for reference in references:
                reference_id = reference["id"]
                nodes.add(reference_id)
                edges.add((reference_id, current_work))
                if current_depth < depth:
                    await queue.put((reference_id, current_depth + 1))

            pbar.update(1)

    return nodes, edges


async def get_citations_and_references(work_id: str, depth: int, limit: int) -> tuple:
    """
    Fetch citations and references for a given work.
    This function is now a wrapper around the recursive fetching functions.

    Args:
        work_id (str): The ID of the work for which to fetch citations and references.
        depth (int): Maximum depth for fetching citations and references.
        limit (int): Maximum number of citations/references to fetch per work.
    """
    citations = await get_citations_recursively(work_id, depth, limit)
    references = await get_references_recursively(work_id, depth, limit)
    return citations, references


async def fetch_work_details(
    work_id: str, limit: int, fetch_type: str = "citations"
) -> tuple[list[str], dict[str, WorkObject]]:
    """
    Fetch either citations or references of a work asynchronously.

    Args:
        work_id (str): The ID of the work for which to fetch citations or references.
        limit (int): Maximum number of citations/references to fetch per work.
        fetch_type (str): Either "citations" or "references".

    Returns:
        tuple[list, list]: A tuple where the first element is a list of IDs,
                           and the second element is a list of Work objects.
    """
    work = Work(work_id)
    if fetch_type == "citations":
        return await work.citations(limit)
    else:
        return await work.references(limit)


async def fetch_recursively(
    entity_id: str, depth: int, limit: int, fetch_type: str
) -> list[dict[str, list[str]]]:
    """
    Generic recursive function to fetch citations or references.

    Args:
        entity_id (str): The ID of the work for which to fetch citations or references.
        depth (int): Maximum depth for fetching citations or references.
        limit (int): Maximum number of citations/references to fetch per work.
        fetch_type (str): Either "citations" or "references".

    Returns:
        list: A list of citations or references,
        where each citation or reference is a dict with keys "id" and "child_items".
    """
    if depth == 0:
        return []

    result = []
    child_fetches = []
    citations_or_references_ids, _ = await fetch_work_details(
        entity_id, limit, fetch_type
    )

    for child_url in citations_or_references_ids:
        child_id = parse_id_from_url(child_url)
        child_fetches.append(fetch_recursively(child_id, depth - 1, limit, fetch_type))

    for child_fetch, child_id in zip(
        await asyncio.gather(*child_fetches), citations_or_references_ids
    ):
        result.append({"id": child_id, "child_items": child_fetch})

    return result


async def get_citations_recursively(
    entity_id, depth=3, limit=100
) -> list[dict[str, list[str]]]:
    """
    Recursively fetch citations for a specified work.

    Args:
        entity_id (str): The ID of the work for which to fetch citations.
        depth (int): Maximum depth for fetching citations.
        limit (int): Maximum number of citations to fetch per work.

    Returns:
        list: A list of citations,
        where each citation is a dict with keys "id" and "child_items".
    """
    return await fetch_recursively(entity_id, depth, limit, "citations")


async def get_references_recursively(
    entity_id: str, depth: int = 3, limit: int = 100
) -> list[dict[str, list[str]]]:
    """
    Recursively fetch references for a specified work.

    Args:
        entity_id (str): The ID of the work for which to fetch references.
        depth (int): Maximum depth for fetching references.
        limit (int): Maximum number of references to fetch per work.

    Returns:
        list: A list of references,
        where each reference is a dict with keys "id" and "child_items".
    """
    return await fetch_recursively(entity_id, depth, limit, "references")
