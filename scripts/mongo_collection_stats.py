#!/usr/bin/env python

from buff.store.mongo import mongo_client

mongo_db_openalex = mongo_client["openalex"]
mongo_collection_works = mongo_db_openalex["works"]


async def stats():
    """stats function"""
    total_count = await mongo_collection_works.count_documents({})
    print("# Works: ", total_count)

    count = await mongo_collection_works.count_documents({"best_oa_location.pdf_url": {"$exists": True, "$ne": None}})
    print("# OA Works: ", count)

    # Get the count of PDF URLs ending with ".pdf"
    pdf_count = await mongo_collection_works.count_documents({"best_oa_location.pdf_url": {"$regex": "\\.pdf$"}})
    print("# PDF URLs ending with '.pdf': ", pdf_count)

    # Print the DOI and PDF URL for each document
    print("# Documents with DOI and PDF URL:")
    async for doc in mongo_collection_works.find({"best_oa_location.pdf_url": {"$exists": True, "$ne": None}}):
        doi = doc.get("doi")
        pdf_url = doc["best_oa_location"]["pdf_url"]
        print(f"  DOI: {doi}, PDF URL: {pdf_url}")

if __name__ == "__main__":
    import asyncio

    asyncio.run(stats())
