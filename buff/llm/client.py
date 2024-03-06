"""buff/llm/client.py"""

import cohere
from openai import AsyncOpenAI

from buff import SECRETS

cohere = cohere.AsyncClient(api_key=SECRETS.COHERE_API_KEY)

openai = AsyncOpenAI(api_key=SECRETS.OPENAI_API_KEY)
