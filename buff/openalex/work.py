"""buff/openalex/work.py"""

import httpx
from aiolimiter import AsyncLimiter
from tenacity import retry, stop_after_attempt

from config import EMAIL

from .errors import OpenAlexError
from .models import WorkObject

limiter = AsyncLimiter(max_rate=10, time_period=1)


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

    @retry(stop=stop_after_attempt(3))
    async def __GET(self, url: str) -> httpx.Response:
        """
        GET request to the OpenAlex API.

        Args:
            url (str): URL to the OpenAlex API endpoint

        Returns:
            httpx.Response: Response object from the OpenAlex API
        """
        async with limiter:
            async with httpx.AsyncClient() as client:
                return await client.get(
                    url, params={"email": EMAIL}, follow_redirects=True
                )

    async def get(self) -> WorkObject:
        """
        Get the work data from the OpenAlex API.

        Returns:
            dict: Work data
        """
        url = f"{self.BASE_URL}{self.entity_id}"

        response = await self.__GET(url)

        if not response.status_code:
            raise OpenAlexError(f"Error calling OpenAlex API: {url}")
        elif response.status_code == 404:
            raise OpenAlexError("Paper not found")

        data = response.json()
        return WorkObject(**data)
