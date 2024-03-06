"""buff/llm/skills/summarize.py"""

from buff.llm.client import openai

SUMMARIZE_PAPER_SYSTEM_PROMPT = """
You will be provided the contents of a research paper.
Your task is to summarize the meeting notes as follows:

- Write a summary of the paper in 3-4 sentences.
- Write a list of key findings from the paper.
    - Write a list of supporting evidence for the key findings.
    - Write a list of refuting evidence for the key findings.
- Write a list of potential next steps or research directions.
""".strip()


async def summarize_paper(text: str) -> str:
    """
    Summarize the paper.

    Args:
        text (str): Contents of the paper

    Returns:
        str: Summary of the paper
    """

    response = await openai.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": SUMMARIZE_PAPER_SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        response_format={"type": "text"},
        temperature=0,
    )

    return response.choices[0].message.content
