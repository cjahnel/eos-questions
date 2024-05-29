from main import pc
from main import client


def searchBooks(summary: str, book: str = None, chapter: str = None) -> str:
    model = "text-embedding-3-small"

    embed = client.embeddings.create(
        input=summary,
        model=model
    ).data[0].embedding

    index = pc.Index("eos-questions")

    filter = {}

    if book:
        filter["book"] = {"$eq": book}
    
    if chapter:
        filter["chapter"] = {"$eq": chapter}

    results = index.query(
        # namespace="eos-books",
        # id=ids[0],
        vector=embed,
        top_k=5,
        include_metadata=True,
        filter=filter
    )

    cited_results = []

    for match in results["matches"]:
        cited_results.append((
            f"From {match['metadata']['book']} in {match['metadata']['chapter']}:\n"
            f"`{match['metadata']['text']}`"
        ))

    return "\n\n".join(cited_results)
