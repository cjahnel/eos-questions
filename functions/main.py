import json
import markdown
import os
from firebase_functions import https_fn
from flask import render_template_string
from openai import OpenAI
from pinecone import Pinecone

client = None
pc = None

template_string = """
<article class="row my-2 rounded-1 border border-3 border-info-subtle p-3">
    {{ user_msg }}
</article>
<article class="row my-2 rounded-1 bg-info text-light p-3">
    {{ assistant_msg|safe }}
</article>
"""

@https_fn.on_request(secrets=["OPENAI_API_KEY", "PINECONE_API_KEY"])
def new_message(req: https_fn.Request) -> https_fn.Response:
    global client
    if not client:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    # Select the OpenAI LLM; "gpt-3.5-turbo" is a more cost-effective choice
    model = "gpt-4o"

    # Inform the Assistant that its purpose is to answer questions about EOS
    system_message = {
        "role": "system",
        "content": "You are a helpful assistant to business owners who are implementing EOS, the Entrepreneurial Operating System. \
                    Your job is to provide concise and accurate answers to any questions they have about EOS."
    }

    # Provide the Assistant with the `searchBooks` function to fetch text from the EOS books
    tools = [{
        "type": "function",
        "function": {
            "name": "searchBooks",
            "description": "Retrieve information about EOS from the official books",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "The keywords in the user's question",
                    },
                    "book": {
                        "type": "string",
                        "description": "If specified, the book title to consult"
                    },
                    "chapter": {
                        "type": "string",
                        "description":
                            "If specified, the chapter number, appendix letter and/or introduction in the following format, respectively: \
                            'chapter1', 'appendixA', 'intro'"
                    }
                },
                "required": ["summary"]
            }
        }
    }]
    
    # Get the user's message from the textbox in the form
    user_msg = req.form["userInput"]

    # Get the conversation from the hidden input in the form
    if req.form["messages"]:
        messages = json.loads(req.form["messages"])
    else:
        messages = []

    # Add the system message to the beginning of the conversation
    messages.insert(0, system_message)

    # Add the user's message to the end of the conversation
    messages.append({
        "role": "user",
        "content": user_msg
    })

    # Generate a response from the LLM
    assistant_msg = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        max_tokens=1024,
        temperature=0
    ).choices[0].message

    # If GPT generated a response, format it and return the HTML to the client
    if assistant_msg.content:
        assistant_msg_formatted = markdown.markdown(assistant_msg.content)
        return render_template_string(template_string, user_msg=user_msg, assistant_msg=assistant_msg_formatted)

    # No message was given, so get the function
    function = assistant_msg.tool_calls[0].function

    # Get the arguments for the function
    args = json.loads(function.arguments)

    global pc
    if not pc:
        api_key=os.environ.get("PINECONE_API_KEY")
        pc = Pinecone(api_key=api_key)
    
    from functions import searchBooks

    # Get the arguments that were supplied by the LLM
    summary = args["summary"]
    book = args.get("book")
    chapter = args.get("chapter")
    
    # Call the function with its argument(s)
    result = searchBooks(summary, book, chapter)
    
    # Add the result to the conversation
    messages.append({
        "role": "function",
        "name": "searchBooks",
        "content": result
    })
    
    # Ask GPT to generate a response now that is has the function result in its context
    assistant_msg = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=1024,
        temperature=0
    ).choices[0].message

    # Format the response and return the HTML to the client
    assistant_msg_formatted = markdown.markdown(assistant_msg.content)
    return render_template_string(template_string, user_msg=user_msg, assistant_msg=assistant_msg_formatted)
