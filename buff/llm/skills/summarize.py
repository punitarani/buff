"""buff/llm/skills/summarize.py"""

from langchain.chains.summarize import load_summarize_chain
from langchain.schema import Document
from langchain_openai import ChatOpenAI
from tenacity import retry, stop_after_attempt, wait_fixed

SUMMARIZE_PAPER_SYSTEM_PROMPT = """
You will be provided the contents of a research paper.
Your task is to summarize the meeting notes as follows:

- Write a summary of the paper in 3-4 sentences.
- Write a list of key findings from the paper.
    - Write a list of supporting evidence for the key findings.
    - Write a list of refuting evidence for the key findings.
- Write a list of potential next steps or research directions.
""".strip()

LLM_OPENAI = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-0125")
SUMMARIZE_CHAIN = load_summarize_chain(llm=LLM_OPENAI, chain_type="stuff")


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def summarize_text(text: str) -> str:
    """
    Summarize the contents of a research paper.

    Args:
        text (str): Contents of the paper

    Returns:
        str: Summary of the paper
    """

    return await SUMMARIZE_CHAIN.arun([Document(page_content=text)])
