"""buff/openalex/work.py"""

from json import JSONDecodeError

import httpx
from aiocache import cached
from aiolimiter import AsyncLimiter
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
from pydantic import ValidationError

from config import EMAIL

from .config import aiocache_redis_config
from .errors import OpenAlexError
from .models import WorkObject

limiter = AsyncLimiter(max_rate=10, time_period=2)


class Work:
    """
    OpenAlex Work class.

    Works are scholarly documents like journal articles, books, datasets, and theses
    """

    BASE_URL = "https://api.openalex.org/works/"

    def __init__(self, entity_id: str | None):
        """
        Initialize the Work object.

        Args:
            entity_id (str | None): Entity ID of the work
        """

        # Ensure the Entity ID is valid
        if not entity_id.startswith("W"):
            raise OpenAlexError("Invalid Entity ID")
        self.entity_id: str | None = entity_id

        self._data: WorkObject | None = None

    @property
    async def data(self) -> WorkObject:
        """Get the work object data."""
        if self._data is None:
            self._data = await self.get()
        return self._data

    @retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=(
            retry_if_exception_type(JSONDecodeError)
            | retry_if_exception_type(httpx.ConnectTimeout)
            | retry_if_exception_type(OpenAlexError)
        ),
    )
    async def __GET(self, url: str) -> dict:
        """
        GET request to the OpenAlex API.

        Args:
            url (str): URL to the OpenAlex API endpoint

        Returns:
            dict: Response object from the OpenAlex API
        """
        async with limiter:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url, params={"email": EMAIL}, follow_redirects=True
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    raise OpenAlexError(f"Error {response.status_code}: GET {url}")

    async def get(self) -> WorkObject:
        """
        Get the work data from the OpenAlex API.

        Returns:
            dict: Work data
        """
        url = f"{self.BASE_URL}{self.entity_id}"

        data = await self.__GET(url)
        self._data = WorkObject(**data)
        return self._data

    async def citations(self, limit: int = 1000) -> tuple[list[str], dict[str, WorkObject]]:
        """
        Get the citations of the work from the OpenAlex API.
        Works that cite the given work. Incoming citations.

        Args:
            limit (int): Maximum number of citations to fetch.
                Default: 1000. Maximum: 10,000.

        Returns:
            tuple[list[str], dict[str, WorkObject]]:
                - List of IDs URLs of the citations
                - Dictionary of {id: WorkObject} of all the citation works

        TODO: add support for batched requests
        """
        per_page: int = 200  # OpenAlex supports 1-200 per page
        limit = min(limit, 10000)  # Ensure limit is under 10,000 (OpenAlex API limit)

        url = f"https://api.openalex.org/works?filter=cites:{self.entity_id}"

        citations: list[dict] = []
        total_citations = None
        page: int = 1
        max_pages: int = 1

        citation_ids = []
        citation_works = {}

        while len(citations) < limit:
            try:
                data = await self.__GET(url + f"&page={page}&per-page={per_page}")
            except Exception as e:
                print(f"Error fetching data: {e}")
                break

            new_citations = data["results"]
            if not new_citations:
                break
            citations.extend(new_citations)

            for citation in new_citations:
                try:
                    citation_id = citation.get('id')
                    if citation_id:
                        citation_ids.append(citation_id)
                        citation_works[citation_id] = WorkObject(**citation)
                    # TODO: handle citations without IDs (shouldn't happen)
                except OpenAlexError or ValidationError:
                    pass

            if total_citations is None:
                total_citations = data["meta"]["count"]
                max_pages = (total_citations + len(new_citations) - 1) // len(new_citations)
                limit = min(limit, total_citations)

            if page >= max_pages:
                break
            page += 1

        return citation_ids, citation_works

    async def references(self, limit: int = 1000) -> tuple[list[str], dict[str, WorkObject]]:
        """
        Get the references of the work from the OpenAlex API.
        Works that the given work cites. Outgoing citations.

        Args:
            limit (int): Maximum number of references to fetch.
                Default: 1000. Maximum: 10,000.

        Returns:
            tuple[list[str], dict[str, WorkObject]]:
                - List of IDs URLs of the references
                - Dictionary of {id: WorkObject} of all the referenced works
        """
        per_page: int = 200  # OpenAlex supports 1-200 per page
        limit = min(limit, 10000)  # Ensure limit is under 10,000 (OpenAlex API limit)

        url = f"https://api.openalex.org/works?filter=cited_by:{self.entity_id}"

        references: list[dict] = []
        total_references = None
        page: int = 1
        max_pages: int = 1

        reference_ids = []
        reference_works = {}

        while len(references) < limit:
            try:
                data = await self.__GET(url + f"&page={page}&per-page={per_page}")
            except Exception as e:
                print(f"Error fetching data: {e}")
                break

            new_references = data["results"]
            if not new_references:
                break
            references.extend(new_references)

            for reference in new_references:
                try:
                    reference_id = reference.get('id')  # Assuming 'id' is the key for reference ID
                    if reference_id:
                        reference_ids.append(reference_id)
                        reference_works[reference_id] = WorkObject(**reference)
                except ValidationError:
                    pass

            if total_references is None:
                total_references = data["meta"]["count"]
                max_pages = (total_references + len(new_references) - 1) // len(new_references)
                limit = min(limit, total_references)

            if page >= max_pages:
                break
            page += 1

        return reference_ids, reference_works
