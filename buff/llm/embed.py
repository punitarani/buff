"""buff/llm/embed.py"""

from buff.llm.client import cohere


async def embed_text(text: str, input_type: str = "search_document") -> list[float]:
    """Embed text using OpenAI's text-embedding-3-small model."""
    response = await cohere.embed(
        texts=[text], model="embed-english-v3.0", input_type=input_type
    )
    return response.embeddings[0]


async def embed_texts(
    texts: list[str], input_type: str = "search_document"
) -> list[list[float]]:
    """Embed a list of texts using OpenAI's text-embedding model."""
    response = await cohere.embed(
        texts=texts, model="embed-english-v3.0", input_type=input_type
    )
    return response.embeddings
