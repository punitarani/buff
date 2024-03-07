"""buff/llm/split.py"""

from unstructured.partition.auto import partition_text


def split_text(text: str) -> list[str]:
    """
    Split the text into chunks.

    Args:
        text (str): The text to chunk

    Returns:
        list[str]: List of chunks
    """
    elements = partition_text(text=text, min_partition=40, max_partition=2000)
    return [chunk.text for chunk in elements]
