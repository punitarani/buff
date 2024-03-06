"""buff/llm/agents/search.py"""

from buff.llm.client import cohere

SEARCH_WIKI_PREAMBLE = """
You are a scientist with access to Wikipedia.
Your task is to answer the following question concisely and accurately using information from Wikipedia.
""".strip


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
