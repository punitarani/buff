#!/usr/bin/env python

import json

from buff.network.data import build_network_around_work
from buff.network.download import download_papers
from config import DATA_DIR
from download_papers import map_work_id_to_doi

EID = "W2994792393"
NETWORK_FP = DATA_DIR.joinpath(f"network_{EID}.json")
WORKS_FP = DATA_DIR.joinpath(f"works_{EID}.json")


async def main() -> None:
    """main function"""
    nodes, edges = await build_network_around_work(
        entity_id=EID, depth=1, citations_limit=100, references_limit=100
    )
    print(f"Nodes: {len(nodes)}, Edges: {len(edges)}")

    data = {
        "nodes": [str(work_id) for work_id in nodes],
        "edges": [(str(src), str(dst)) for src, dst in edges],
    }

    print(f"Saving network to {NETWORK_FP}")
    with open(NETWORK_FP, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    WORKS = list(nodes)
    print(f"Downloading {len(WORKS)} papers")
    await download_papers(works=WORKS)

    print("Mapping work IDs to DOIs")
    work_dois = await map_work_id_to_doi(WORKS)

    print("Saving to file works.json")
    with open(WORKS_FP, "w", encoding="utf-8") as work_file:
        json.dump(work_dois, work_file, indent=2)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
