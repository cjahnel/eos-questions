import hashlib
import os
import pickle


from openai import OpenAI
client = OpenAI()

import chromadb
chroma_client = chromadb.Client()
openai_ef = chromadb.utils.embedding_functions.OpenAIEmbeddingFunction(os.getenv("OPENAI_API_KEY"))
collection = chroma_client.get_or_create_collection("jahnel-group-docs", embedding_function=openai_ef)

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

def completion(content: str):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "searchDocs",
                "description": "Retrieve external information about Jahnel Group from company documents",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "The keywords picked out from the user's input",
                        }
                    },
                    "required": ["summary"]
                }
            }
        }
    ]

    messages=[
        {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
        {"role": "user", "content": content}
    ]

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    message = completion.choices[0].message

    return message.content or message.tool_calls[0].function

def main():
    # switch `add` to `upsert` to avoid adding the same documents every time
    collection.upsert(
        documents=[
            "This is a document about pineapple",
            "This is a document about oranges"
        ],
        ids=["id1", "id2"]
    )

    results = collection.query(
        query_texts=["This is a query document about florida"], # Chroma will embed this for you
        n_results=2 # how many results to return
    )

    print(results)

if __name__ == "__main__":
    main()
