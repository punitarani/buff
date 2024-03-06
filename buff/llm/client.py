"""buff/llm/client.py"""

from openai import AsyncOpenAI

from buff import SECRETS

openai = AsyncOpenAI(api_key=SECRETS.OPENAI_API_KEY)
