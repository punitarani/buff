"""
Streamlit App

python -m streamlit run main.py
"""

import asyncio

import pandas as pd
import streamlit as st

from buff.openalex import find_similar_papers, get_openalex_work


async def get_paper_data(paper) -> dict:
    """Get the paper data from the OpenAlex API."""
    sim_entity_id = paper[0]
    sim_score = paper[1]

    sim_openalex_work = await get_openalex_work(entity_id=sim_entity_id)
    return {
        "Title": sim_openalex_work.get('title'),
        "DOI": sim_openalex_work.get('doi'),
        "Score": sim_score
    }


async def main():
    """Main function of the App."""
    st.title("AutoResearcher")
    doi_input = st.text_input("Enter DOI", "")

    if doi_input:
        with st.spinner("Finding similar papers..."):
            similar_papers = await find_similar_papers(doi_input)

        with st.spinner("Loading similar papers..."):
            similar_paper_data = [await get_paper_data(paper) for paper in similar_papers]

        # Convert list of dictionaries to a pandas DataFrame
        papers_df = pd.DataFrame(similar_paper_data)

        # Display the DataFrame as a table
        st.header("Related papers")
        st.table(papers_df)


if __name__ == "__main__":
    # Streamlit config
    st.set_page_config(
        page_title="AutoResearcher",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    asyncio.run(main())
