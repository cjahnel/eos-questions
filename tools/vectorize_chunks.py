import os
import re
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

def tag_chunk(chunk_file: str, book_name: str, chapter_name: str, section_name: str, subsection_name: str = None):
    id = f"{book_name}#{chapter_name}#{section_name}"
    if subsection_name:
        id += f"#{subsection_name}"

    if book_name == "get-a-grip":
        book_name = "Get a Grip"
    elif book_name == "traction":
        book_name = "Traction"
    elif book_name == "wth-is-eos":
        book_name = "What the Heck is EOS?"

    chapter_regex = re.compile(r"(chapter)(\d+)")
    appendix_regex = re.compile(r"(appendix)([ABC])")

    if chapter_name == "intro":
        chapter_name= "Introduction"
    elif chapter_regex.match(chapter_name):
        chapter_number = int(chapter_regex.search(chapter_name).group(2))
        chapter_name = f"Chapter {chapter_number}"
    elif appendix_regex.match(chapter_name):
        appendix_letter = appendix_regex.search(chapter_name).group(2)
        chapter_name = f"Appendix {appendix_letter}"

    with open(chunk_file, "r") as chunk:
        chunk_text = chunk.read()

    return {
        "id": id,
        "metadata": {"book": book_name, "chapter": chapter_name, "text": chunk_text}
    }

def upload_chunk(book_name: str) -> None:
    chunks_dir = os.path.join("books", book_name, "chunks")

    chunks = []

    for chapter_name in os.listdir(chunks_dir):
        chapter_dir = os.path.join(chunks_dir, chapter_name)
        for section_name in os.listdir(chapter_dir):
            section = os.path.join(chapter_dir, section_name)

            if os.path.isdir(section):
                for subsection_name in os.listdir(section):
                    subsection_file = os.path.join(section, subsection_name)
                    tagged_subsection = tag_chunk(subsection_file, book_name, chapter_name, section_name, subsection_name)
                    chunks.append(tagged_subsection)
            else:
                tagged_chunk = tag_chunk(section, book_name, chapter_name, section_name)
                chunks.append(tagged_chunk)

    input = [chunk["metadata"]["text"] for chunk in chunks]

    model = "text-embedding-3-small"

    data = client.embeddings.create(
        input=input,
        model=model
    ).data

    for i, chunk in enumerate(chunks):
        chunk.update({"values": data[i].embedding})

    index = pc.Index("eos-questions")
    index.upsert(vectors=chunks)

if __name__ == "__main__":
    upload_chunk("get-a-grip")
    upload_chunk("traction")
    upload_chunk("wth-is-eos")
