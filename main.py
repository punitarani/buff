"""
Streamlit App

python -m streamlit run main.py
"""

import asyncio

import pandas as pd
import streamlit as st

from buff.openalex import Work
from buff.openalex.models import WorkObject


async def get_papers(entity_id: str, max_depth: int = 10, max_count: int = 100) -> list[WorkObject]:
    """
    Get papers from the OpenAlex API without batching, with limits on depth and count.

    Args:
        entity_id (str): The ID of the entity for which to get papers.
        max_depth (int): Maximum depth for fetching referenced works.
        max_count (int): Maximum number of papers to fetch.

    Returns:
        List[WorkObject]: A list of WorkObject instances representing papers.
    """
    papers: list[WorkObject] = []
    pending_entities = [entity_id]
    next_entities = []
    processed_entities = set()

    while (pending_entities or next_entities) and max_depth > 0 and len(papers) < max_count:
        if not pending_entities:
            pending_entities, next_entities = next_entities, []
            max_depth -= 1

        # Prepare a list of unprocessed entity IDs
        unprocessed_entities = [eid for eid in pending_entities if eid not in processed_entities]

        # Perform requests for all unprocessed entities
        results = await asyncio.gather(
            *(Work(eid).get() for eid in unprocessed_entities),
            return_exceptions=False
        )

        # Reset pending_entities for the next iteration
        pending_entities = []

        for result in results:
            if isinstance(result, Exception):
                print(f"Error during request: {result}")
            else:
                papers.append(result)
                processed_entities.add(result.id)

                # Process results to get next entities
                for url in result.referenced_works:
                    url = str(url)
                    if url.startswith("https://openalex.org/"):
                        next_entity_id = url[21:]
                        if next_entity_id not in processed_entities:
                            next_entities.append(next_entity_id)

            # Early exit if max_count is reached
            if len(papers) >= max_count:
                return papers

    return papers


async def main():
    """Main function of the App."""
    st.title("AutoResearcher")
    entity_id_input = st.text_input("Enter OpenAlex Entity ID", "")

    if entity_id_input:
        with st.spinner("Getting papers..."):
            works = await get_papers(entity_id_input)

        # Convert list of dictionaries to a pandas DataFrame
        papers_df = pd.DataFrame(
            [
                {
                    "id": str(work.id),
                    "title": work.title,
                }
                for work in works
            ]
        )

        # Display the DataFrame as a table
        st.header("Related papers")
        st.table(papers_df)


if __name__ == "__main__":
    import platform

    st.set_page_config(
        page_title="AutoResearcher",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Check if windows
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
