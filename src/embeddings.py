import hashlib
import os
import pickle

from openai import OpenAI

import chromadb
chroma_client = chromadb.Client()

collection = chroma_client.get_or_create_collection("jahnel-group-docs")
client = OpenAI()

def vectorize(data, model="text-embedding-ada-002") -> list[list[float]]:
    embeddings = client.embeddings.create(
        input=data,
        model=model
    )
    return [embedding.embedding for embedding in embeddings.data]

def generate_embeddings(data, model="text-embedding-ada-002") -> list[list[float]]:
    # Get embeddings
    embeddings = vectorize(data, model)

    # Compute the MD5 hash of the data
    m = hashlib.md5()
    m.update(str(data).encode("utf-8"))
    hash_value = m.hexdigest()

    # Create directory if it does not exist
    os.makedirs("./embedding_checkpoints/", exist_ok=True)

    # Pickle and save the embeddings
    with open(f"./embedding_checkpoints/{hash_value}.pkl", "wb") as f:
        pickle.dump(embeddings, f)
    print(f"Embeddings saved to ./embedding_checkpoints/{hash_value}.pkl")
    return embeddings

def load_embeddings(data, engine="text-embedding-ada-002"):
    hash_value = hashlib.md5(str(data).encode("utf-8")).hexdigest()

    try:
        with open(f"./embedding_checkpoints/{hash_value}.pkl", "rb") as f:
            embeddings = pickle.load(f)
        print(f"Embeddings loaded from ./embedding_checkpoints/{hash_value}.pkl")
    except:
        print("Embeddings not found. Computing embeddings...")
        embeddings = generate_embeddings(data, engine)
    
    return embeddings

data = {
    "model": "gpt-3.5-turbo-0613",
    "messages": [
        {"role": "user", "content": "Who is the CEO of Jahnel Group?"}
    ],
    "functions": [
        {
            "name": "searchDocs",
            "description": "Retrieve external information about Jahnel Group from company documents",
            "parameters": {
                "type": "string"
            }
        }
    ]
}

def main():
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
            {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
        ]
    )

    print(completion.choices[0].message)

if __name__ == "__main__":
    main()
