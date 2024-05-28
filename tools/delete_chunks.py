import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

def delete_all_chunks():
    index_name = "eos-questions"
    index = pc.Index(index_name)
    index.delete(delete_all=True)

if __name__ == "__main__":
    # delete_all_chunks()
    pass
