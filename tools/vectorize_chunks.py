import os
import re
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

def upload_chunk(book_dir: str) -> None:
    chunks_dir_path = os.path.join("books", book_dir, "chunks")

    chunks = []

    for chapter_dir in os.listdir(chunks_dir_path):

        chapter_dir_path = os.path.join(chunks_dir_path, chapter_dir)

        for section_file in os.listdir(chapter_dir_path):
            chunk_path = os.path.join(chapter_dir_path, section_file)

            with open(chunk_path, "r") as chunk_file:
                chunk_text = chunk_file.read()

                if book_dir == "get-a-grip":
                    book_name = "Get a Grip"
                elif book_dir == "traction":
                    book_name = "Traction"
                elif book_dir == "wth-is-eos":
                    book_name = "What the Heck is EOS?"

                chapter_regex = re.compile(r"(chapter)(\d+)")
                appendix_regex = re.compile(r"(appendix)([ABC])")

                if chapter_dir == "intro":
                    chapter_name= "Introduction"
                elif chapter_regex.match(chapter_dir):
                    chapter_number = int(chapter_regex.search(chapter_dir).group(2))
                    chapter_name = f"Chapter {chapter_number}"
                elif appendix_regex.match(chapter_dir):
                    appendix_letter = appendix_regex.search(chapter_dir).group(2)
                    chapter_name = f"Appendix {appendix_letter}"

                chunks.append({
                    "id": f"{book_dir}#{chapter_dir}#{section_file.removesuffix(".txt")}",
                    "metadata": {"book": book_name, "chapter": chapter_name, "text": chunk_text}
                })

    input = [chunk["metadata"]["text"] for chunk in chunks]

    model = "text-embedding-3-small"

    # max tokens is 8191
    data = client.embeddings.create(
        input=input,
        model=model
    ).data

    for i, chunk in enumerate(chunks):
        chunk.update({"values": data[i].embedding})
    
    if len(chunks) > 100:
        raise Exception("Too many chunks to load at once, should be done in a batch")

    index = pc.Index("eos-questions")

    index.upsert(
        vectors=chunks
        # namespace="eos-books"
    )

if __name__ == "__main__":
    upload_chunk("get-a-grip")
    # upload_chunk("traction")
    upload_chunk("wth-is-eos")
