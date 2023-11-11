"""tests/test_openalex.py"""

import pytest

from buff.openalex import Work


class TestWork:
    """Test OpenAlex Work class"""

    @pytest.mark.asyncio
    async def test_get(self) -> None:
        """Test Work.get()"""
        work = Work("W2741809807")
        work_data = await work.get()
        assert (
            work_data.title
            == "The state of OA: a large-scale analysis of the prevalence and impact of Open Access articles"
        )
