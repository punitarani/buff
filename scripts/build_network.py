#!/usr/bin/env python

import asyncio

from buff.network.data import build_network_around_work

EID = "W2994792393"

res = asyncio.run(
    build_network_around_work(
        entity_id=EID, depth=5, citations_limit=10, references_limit=10
    )
)
print(res)
