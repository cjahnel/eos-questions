import json
import os
from openai import OpenAI
from chromadb import Client, QueryResult
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

openai_client = OpenAI()
chroma_client = Client()
openai_ef = OpenAIEmbeddingFunction(os.getenv("OPENAI_API_KEY"))
collection = chroma_client.get_or_create_collection("jahnel-group-docs", embedding_function=openai_ef)

collection.upsert(
    documents=[
        "The CEO, Darrin Jahnel, was born in 1976.",
        "Jahnel Group was founded by the CEO and his brother.",
        "Darrin used to play basketball with his brother, Jason."
    ],
    ids=["id1", "id2", "id3"]
)

messages = [{
    "role": "system",
    "content": "You are an assistant to employees at Jahnel Group. \
                Your job is to answer questions about the company."
}]

def answer(content: str) -> str:
    tools = [{
        "type": "function",
        "function": {
            "name": "searchDocs",
            "description": "Retrieve information about Jahnel Group from company documents",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "The keywords in the user's question",
                    }
                },
                "required": ["summary"]
            }
        }
    }]

    messages.append({"role": "user", "content": content})

    completion = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    message = completion.choices[0].message

    if message.content:
        messages.append({"role": "assistant", "content": message.content})
        return message.content
    
    function = message.tool_calls[0].function

    if function.name == "searchDocs":
        arguments = json.loads(function.arguments)
        summary = arguments["summary"]
        documents = searchDocs(summary).get("documents")[0]
        result = " ".join(documents)
        messages.append({
            "role": "function",
            "name": "searchDocs",
            "content": result
        })
    else:
        raise ValueError(f"Unknown function: {function.name}")
    
    completion = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    # repeating code, should probably abstract this as a function
    message = completion.choices[0].message

    messages.append({"role": "assistant", "content": message.content})
    return message.content
    
def searchDocs(summary: str) -> QueryResult:
    return collection.query(
        query_texts=[summary],
        n_results=3
    )
