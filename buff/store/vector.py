"""buff/store/vector.py"""

from pinecone import Pinecone

from buff import SECRETS

pc = Pinecone(api_key=SECRETS.PINECONE_API_KEY)


# papers index
papers_index = pc.Index(name="papers")