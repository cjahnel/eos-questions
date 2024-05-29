import json
import os
from firebase_functions import https_fn
# from firebase_admin import initialize_app
from flask import render_template_string
from openai import OpenAI
from pinecone import Pinecone

# initialize_app()

client = None
pc = None

template_string = """
<article class="row my-2 rounded-1 border border-3 border-info-subtle p-3">
    {{ userMsg }}
</article>
<article class="row my-2 rounded-1 bg-info text-light p-3">
    {{ assistantMsg }}
</article>
"""

@https_fn.on_request(secrets=["OPENAI_API_KEY", "PINECONE_API_KEY"])
def new_message(req: https_fn.Request) -> https_fn.Response:
    global client
    if not client:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    # Select the OpenAI LLM
    model = "gpt-4o"

    # Supply the System message
    system_message = {
        "role": "system",
        "content": "You are a helpful assistant to business owners who are implementing EOS, the Entrepreneurial Operating System. \
            Your job is to provide concise and accurate answers to any questions they have about EOS. \
            If you already know the answer, you can answer directly. Otherwise, search the official EOS books. \
            If you are listing a series of items, please use new lines to separate them."
    }

    # Equip the assistant with the Function
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

    # Add the system message to the conversation
    messages.insert(0, system_message)

    # Add the user's message to the conversation
    messages.append({
        "role": "user",
        "content": user_msg
    })

    # Ask GPT to generate a response
    assistant_msg = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto"
        # TODO: Play with temperature
        # temperature=0
    ).choices[0].message

    # If GPT generated a response, add it to the conversation and return dialogue
    if assistant_msg.content:
        return render_template_string(template_string, userMsg=user_msg, assistantMsg=assistant_msg.content)

    # No message was given, so get the function
    function = assistant_msg.tool_calls[0].function

    # Get the arguments for the function
    args = json.loads(function.arguments)

    # Make sure that the function is the one we expect
    if function.name == "searchBooks":
        global pc
        if not pc:
            api_key=os.environ.get("PINECONE_API_KEY")
            pc = Pinecone(api_key=api_key)
        
        from functions import searchBooks

        summary = args["summary"]
        
        # Call the function
        result = searchBooks(summary)
        
        # Add the result to the conversation
        messages.append({
            "role": "function",
            "name": "searchBooks",
            "content": result
        })
    else:
        raise ValueError(f"Unknown function: {function.name}")
    
    # Ask GPT to generate a response with the function result in its context
    assistant_msg = client.chat.completions.create(
        model=model,
        messages=messages
    ).choices[0].message
    
    # TODO: Add streamimg?

    # Return the dialogue
    return render_template_string(template_string, userMsg=user_msg, assistantMsg=assistant_msg.content)
