"""buff/store/vector.py"""

import os

from pinecone import Pinecone

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
assert PINECONE_API_KEY, "Env var PINECONE_API_KEY not set"

pc = Pinecone(api_key=PINECONE_API_KEY)


# papers index
papers_index = pc.Index(name="papers")
