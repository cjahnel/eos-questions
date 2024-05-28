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
<article class="message row my-2 rounded-1 bg-primary text-light p-3" data-role="user">
    {{ userMsg }}
</article>
<article class="message row my-2 rounded-1 bg-secondary text-light p-3" data-role="assistant">
    {{ assistantMsg }}
</article>
"""

@https_fn.on_request(secrets=["OPENAI_API_KEY", "PINECONE_API_KEY"])
def new_message(req: https_fn.Request) -> https_fn.Response:
    global client
    if not client:
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    # Select the OpenAI LLM
    model = "gpt-3.5-turbo"

    # Supply the System message
    system_message = {
        "role": "system",
        "content": "You are a helpful assistant to business owners who are implementing EOS, the Entrepreneurial Operating System. \
            Your job is to answer any questions they have about EOS by searching the official EOS books. \
            If you already know the answer, or their question is too vague, you can answer directly."
    }

    # Equip the assistant with the Function
    tools = [{
        "type": "function",
        "function": {
            "name": "searchDocs",
            "description": "Retrieve information about EOS from the official books",
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
    if function.name == "searchDocs":
        global pc
        if not pc:
            api_key=os.environ.get("PINECONE_API_KEY")
            pc = Pinecone(api_key=api_key)
        
        from functions import searchDocs

        summary = args["summary"]
        
        # Call the function
        result = searchDocs(summary)
        
        # Add the result to the conversation
        messages.append({
            "role": "function",
            "name": "searchDocs",
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
