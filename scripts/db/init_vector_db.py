#!/usr/bin/env python3

from pinecone import ServerlessSpec

from buff.store.vector import pc

pc_indexes = pc.list_indexes()

# Ensure the 'papers' index does not exist
# pc.delete_index("papers")
if "papers" in pc_indexes.names():
    raise ValueError("Index 'papers' already exists")

# Create 'papers' index
pc.create_index(
    name="papers",
    dimension=1024,
    metric="cosine",
    spec=ServerlessSpec(cloud="aws", region="us-west-2"),
)
