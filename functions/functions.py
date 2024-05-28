from main import pc
from main import client


def searchDocs(summary: str) -> str:
    # TODO: Add an additional optional query parameter with the chapter number and text?
    
    model = "text-embedding-3-small"

    embed = client.embeddings.create(
        input=summary,
        model=model
    ).data[0].embedding

    index = pc.Index("eos-questions")

    # TODO: GPT-3.5 can handle 16,385 tokens, so we need to ensure the data first in context upon retrieval, may need to summarize with GPT-4

    result = index.query(
        # namespace="eos-docs",
        # id=ids[0],
        vector=embed,
        top_k=5,
        include_metadata=True
        # filter={"genre": {"$eq": "action"}}
    )

    return "\n\n".join([match["metadata"]["text"] for match in result["matches"]])
