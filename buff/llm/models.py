"""buff/llm/models.py"""

from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    """Metadata for a document"""

    index: int
    work_id: str
    doi: str
    text: str


class Document(BaseModel):
    """Embedding document"""

    id: str
    values: list[float]
    metadata: DocumentMetadata
