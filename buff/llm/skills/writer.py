"""buff/llm/skills/writer.py"""

from tenacity import retry, stop_after_attempt, wait_fixed

from buff.llm.client import openai

WRITE_SYSTEM_PROMPT = """
You are research scientist.
You are given a task and context information to write about.
You should use the context information to write about the task.
""".strip()


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def write(texts: list[str], task: str) -> str:
    """
    Write about the task using the provided context.

    Args:
        texts (list[str]): Context information
        task (str): Task prompt

    Returns:
        str: Writing about the task
    """

    context = "\n\n".join(texts)

    response = await openai.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {
                "role": "system",
                "content": WRITE_SYSTEM_PROMPT,
            },
            {"role": "user", "content": context},
            {"role": "user", "content": task},
        ],
        temperature=0,
    )

    return response.choices[0].message.content
