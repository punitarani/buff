"""buff/network/data.py"""


from buff.openalex import Work
from buff.openalex.utils import parse_id_from_url


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
