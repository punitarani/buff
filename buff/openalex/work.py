"""buff/openalex/work.py"""

from json import JSONDecodeError

import httpx
from aiolimiter import AsyncLimiter
from pydantic import ValidationError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config import EMAIL, mongo_client

from .errors import OpenAlexError
from .models import WorkObject

limiter = AsyncLimiter(max_rate=10, time_period=2)


class Work:
    """
    OpenAlex Work class.

    Works are scholarly documents like journal articles, books, datasets, and theses
    """

    API_URL = "https://api.openalex.org/works/"
    BASE_URL = "https://openalex.org/"

    mongo_db_openalex = mongo_client["openalex"]
    mongo_collection_works = mongo_db_openalex["works"]
    mongo_collection_citations = mongo_db_openalex["citations"]
    mongo_collection_references = mongo_db_openalex["references"]

    def __init__(self, entity_id: str) -> None:
        """
        Initialize the Work object.

        Args:
            entity_id (str): Entity ID of the work
        """

        # Ensure the Entity ID is valid
        if not entity_id.startswith("W"):
            raise OpenAlexError(f"Invalid Entity ID: {entity_id}")
        self.entity_id: str = entity_id

        self.idx: str = f"{self.BASE_URL}{self.entity_id}"

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
        # Try to get the work data from MongoDB
        data = await self.mongo_collection_works.find_one({"id": self.idx})
        if data:
            # Deserialize data into WorkObject
            self._data = WorkObject(**data)
            return self._data

        url = f"{self.API_URL}{self.entity_id}"

        # Get the work data from the OpenAlex API
        data = await self.__GET(url)
        self._data = WorkObject(**data)

        # Serialize WorkObject data into a dict and save to MongoDB
        await self.mongo_collection_works.update_one(
            update=self._data.model_dump(mode="json"), upsert=True
        )

        return self._data

    async def citations(
        self, limit: int = 1000
    ) -> tuple[list[str], dict[str, WorkObject]]:
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
        # Try to get the citations from MongoDB
        db_citations = await self.mongo_collection_citations.find_one({"id": self.idx})
        if db_citations:
            citation_ids = db_citations["citations"][:limit]

            # Fetch all citation works in a single query
            citation_works_cursor = self.mongo_collection_works.find(
                {"id": {"$in": citation_ids}}
            )
            citation_works = {
                work["id"]: WorkObject(**work) async for work in citation_works_cursor
            }

            return citation_ids, citation_works

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
                    citation_id = citation.get("id")
                    if citation_id:
                        citation_ids.append(citation_id)
                        citation_works[citation_id] = WorkObject(**citation)
                    # TODO: handle citations without IDs (shouldn't happen)
                except OpenAlexError or ValidationError:
                    pass

            if total_citations is None:
                total_citations = data["meta"]["count"]
                max_pages = (total_citations + len(new_citations) - 1) // len(
                    new_citations
                )
                limit = min(limit, total_citations)

            if page >= max_pages:
                break
            page += 1

        # Save the Citation IDs to MongoDB
        await self.mongo_collection_citations.update_one(
            filter={"id": self.idx},
            update={"$set": {"citations": citation_ids}},
            upsert=True
        )

        # Save the Citation Works to MongoDB
        for citation_work in citation_works.values():
            await self.mongo_collection_works.update_one(
                filter={"id": str(citation_work.id)},
                update={"$set": citation_work.model_dump(mode="json")},
                upsert=True,
            )

        return citation_ids, citation_works

    async def references(
        self, limit: int = 1000
    ) -> tuple[list[str], dict[str, WorkObject]]:
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
        # Try to get the references from MongoDB
        db_references = await self.mongo_collection_references.find_one(
            {"id": self.idx}
        )
        if db_references:
            reference_ids = db_references["references"][:limit]

            # Fetch all reference works in a single query
            reference_works_cursor = self.mongo_collection_works.find(
                {"id": {"$in": reference_ids}}
            )
            reference_works = {
                work["id"]: WorkObject(**work) async for work in reference_works_cursor
            }

            return reference_ids, reference_works

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
                    reference_id = reference.get("id")
                    if reference_id:
                        reference_ids.append(reference_id)
                        reference_works[reference_id] = WorkObject(**reference)
                    # TODO: handle references without IDs (shouldn't happen)
                except ValidationError:
                    pass

            if total_references is None:
                total_references = data["meta"]["count"]
                max_pages = (total_references + len(new_references) - 1) // len(
                    new_references
                )
                limit = min(limit, total_references)

            if page >= max_pages:
                break
            page += 1

        # Save the Reference IDs to MongoDB
        await self.mongo_collection_references.update_one(
            filter={"id": self.idx},
            update={"$set": {"references": reference_ids}},
            upsert=True,
        )

        # Save the Reference Works to MongoDB
        for reference_work in reference_works.values():
            await self.mongo_collection_works.update_one(
                filter={"id": str(reference_work.id)},
                update={"$set": reference_work.model_dump(mode="json")},
                upsert=True,
            )

        return reference_ids, reference_works
