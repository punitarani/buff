"""buff/llm/embed.py"""

from buff.llm.client import openai


async def embed_text(text: str) -> list[float]:
    """Embed text using OpenAI's text-embedding-3-small model."""
    response = await openai.embeddings.create(input=[text], model="text-embedding-3-small")
    return response.data[0].embedding


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts using OpenAI's text-embedding model."""
    response = await openai.embeddings.create(
        input=texts,
        model="text-embedding-3-small"
    )
    embeddings = [embedding.embedding for embedding in response.data]
    return embeddings
