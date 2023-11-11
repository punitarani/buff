"""buff/network/data.py"""

import asyncio

from buff.openalex import Work
from buff.openalex.utils import parse_id_from_url


async def build_network_around_work(entity_id: str, depth: int = 3, limit: int = 100) -> tuple[set, set]:
    """
    Build a network around a given work, including both citations and references.

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

        citations, references = await asyncio.gather(
            Work(work_id).citations(limit=limit),
            Work(work_id).references(limit=limit)
        )

        for citation in citations:
            citation_id = parse_id_from_url(citation.id)
            nodes.add(citation_id)
            edges.add((work_id, citation_id))
            await process_work(citation_id, current_depth + 1)

        for reference in references:
            reference_id = parse_id_from_url(reference.id)
            nodes.add(reference_id)
            edges.add((reference_id, work_id))
            await process_work(reference_id, current_depth + 1)

    # Start processing with the initial work
    nodes.add(entity_id)
    await process_work(entity_id, 1)

    return nodes, edges


async def get_citations_recursively(entity_id: str, depth: int = 3, limit: int = 100) -> list[dict]:
    """
    Get citations of a paper recursively.

    Args:
        entity_id (str): The ID of the entity for which to get citations.
        depth (int): Maximum depth for fetching citations.
        limit (int): Maximum number of citations to fetch.

    Returns:
        List[dict]: A list of citations of the paper.
    """
    if depth == 0:
        return []

    citations = await Work(entity_id=entity_id).citations(limit=limit)
    result = []
    for citation in citations:
        citation_dict = citation.model_dump()
        child_citations = await get_citations_recursively(parse_id_from_url(citation.id), depth - 1, limit)
        citation_dict['child_citations'] = child_citations
        result.append(citation_dict)

    return result


async def get_references_recursively(entity_id: str, depth: int = 3, limit: int = 100) -> list[dict]:
    """
    Get references of a paper recursively.

    Args:
        entity_id (str): The ID of the entity for which to get references.
        depth (int): Maximum depth for fetching references.
        limit (int): Maximum number of references to fetch.

    Returns:
        List[dict]: A list of references of the paper.
    """
    if depth == 0:
        return []

    references = await Work(entity_id=entity_id).references(limit=limit)
    result = []
    for reference in references:
        reference_dict = reference.model_dump()
        child_references = await get_references_recursively(parse_id_from_url(reference.id), depth - 1, limit)
        reference_dict['child_references'] = child_references
        result.append(reference_dict)

    return result
