import os
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

def embed_chunk(chunk_text: str):
    model = "text-embedding-3-small"

    # max tokens is 8191
    return client.embeddings.create(
        input=[chunk_text],
        model=model
    ).data[0].embedding

def upload_chunk(doc_name: str) -> None:
    chunks_dir = os.path.join("docs", doc_name, "chunks")

    chunks = []

    for chapter_dir in os.listdir(chunks_dir):

        chapter_dir_path = os.path.join(chunks_dir, chapter_dir)

        for section_file in os.listdir(chapter_dir_path):
            chunk_path = os.path.join(chapter_dir_path, section_file)

            with open(chunk_path, "r") as chunk_file:
                chunk_text = chunk_file.read()
                chunk_embedding = embed_chunk(chunk_text)
                chunks.append({
                    "id": f"{doc_name}#{chapter_dir}#{section_file.removesuffix(".txt")}",
                    "values": chunk_embedding,
                    "metadata": {"text": chunk_text}
                })

    # text = text.replace("\n", " ") # Looks like this only applies to the v1 embedding models which treat new lines differently
    
    if len(chunks) > 100:
        raise Exception("Too many chunks to load at once, should be done in a batch")

    index = pc.Index("eos-questions")

    index.upsert(
        vectors=chunks
        # namespace="eos-docs"
    )

if __name__ == "__main__":
    upload_chunk("get-a-grip")
    # upload_chunk("traction")
    upload_chunk("wth-is-eos")
