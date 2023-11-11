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

    @retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=(
            retry_if_exception_type(JSONDecodeError)
            | retry_if_exception_type(httpx.ConnectTimeout)
            | retry_if_exception_type(OpenAlexError)
        ),
    )
    @cached(
        **aiocache_redis_config,
        key_builder=lambda func, self, url, *args, **kwargs: url,
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
        return WorkObject(**data)
