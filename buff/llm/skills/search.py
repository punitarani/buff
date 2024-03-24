"""buff/llm/skills/search.py"""

from tenacity import retry, stop_after_attempt, wait_fixed

from buff.llm.client import cohere
from buff.llm.embed import embed_text
from buff.store.vector import pc_papers

SEARCH_WEB_PREAMBLE = """
You are a scientist with access to the internet.
Your task is to answer the following question concisely and accurately using web-search.
""".strip()

SEARCH_WIKI_PREAMBLE = """
You are a scientist with access to Wikipedia.
Your task is to answer the following question concisely and accurately using information from Wikipedia.
""".strip()


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def search_web(question: str) -> str:
    """Search the internet for the answer to a question."""

    prediction = await cohere.chat(
        message=question,
        preamble_override=SEARCH_WEB_PREAMBLE,
        model="command",
        temperature=0,
        stream=False,
        citation_quality="accurate",
        connectors=[{"id": "web-search"}],
        documents=[],
    )
    return prediction.text


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def search_wiki(question: str) -> str:
    """Search Wikipedia for the answer to a question."""

    prediction = await cohere.chat(
        message=question,
        preamble_override=SEARCH_WIKI_PREAMBLE,
        model="command",
        temperature=0,
        stream=False,
        citation_quality="accurate",
        connectors=[
            {"id": "web-search", "options": {"site": "https://www.wikipedia.org/"}}
        ],
        documents=[],
    )
    return prediction.text


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def search_memory(question: str, n: int = 10) -> list[dict]:
    """Search the memory for the answer to a question."""
    q_vector = await embed_text(text=question, input_type="search_query")
    docs = pc_papers.query(
        vector=q_vector,
        top_k=n,
        include_values=False,
        include_metadata=True,
        namespace="papers",
    )
    return docs.get("matches", [])
