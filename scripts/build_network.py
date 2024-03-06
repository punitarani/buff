#!/usr/bin/env python

import asyncio
import json

from buff.network.data import build_network_around_work
from config import DATA_DIR

NETWORK_FP = DATA_DIR.joinpath("network.json")

EID = "W2994792393"

res = asyncio.run(
    build_network_around_work(
        entity_id=EID, depth=4, citations_limit=10, references_limit=10
    )
)

# Save the result to a file
print(f"Saving network to {NETWORK_FP}")
data = {
    "nodes": [str(work_id) for work_id in res[0]],
    "edges": [(str(src), str(dst)) for src, dst in res[1]],
}
with open(NETWORK_FP, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
