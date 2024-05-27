import os
from pinecone import Pinecone

pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))


def searchDocs(summary: str) -> str:
    index = pc.Index("eos-questions")

    # TODO: Add an additional optional query parameter with the chapter number and text

    # TODO: (Later version?) Ask GPT-4 to describe the images and upload them to the index
    # tagged as images and can call with another function upon request, images stored in Firebase Storage

    query_results = index.query(
        namespace="eos-docs",
        # id=ids[0],
        vector=[1.0, 1.5],
        top_k=3,
        include_values=True,
        include_metadata=True
    )

    return " ".join([doc["id"] for doc in query_results["hits"]])

    # ChromaDB query code:
    # 
    # result = collection.query(
    #     query_texts=[summary],
    #     n_results=3
    # )
    # 
    # docs = result.get("documents")[0]
    # return " ".join(docs)
