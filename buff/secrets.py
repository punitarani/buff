"""buff/secrets.py"""

import os

from pydantic import BaseModel


class Secrets(BaseModel):
    """Secrets loaded from environment variables"""

    OPENAI_API_KEY: str

    @classmethod
    def load(cls) -> "Secrets":
        """Load secrets from environment variables"""
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        assert OPENAI_API_KEY, "OPENAI_API_KEY environment variable not set"

        return cls(
            OPENAI_API_KEY=OPENAI_API_KEY,
        )
