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

    @pytest.mark.skip
    async def test_citations(self) -> None:
        """Test Work.citations()"""
        work = Work("W2741809807")
        citations_ids, citations_works = await work.citations()
        assert len(citations_ids) >= 574
        assert len(citations_works) >= 574

    @pytest.mark.skip
    async def test_references(self) -> None:
        """Test Work.references()"""
        work = Work("W2741809807")
        references_ids, references_works = await work.references()
        assert len(references_ids) == 35
        assert len(references_works) == 35
