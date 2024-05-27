import json
import os
from firebase_functions import https_fn
# from firebase_admin import initialize_app
from openai import OpenAI

# initialize_app()


@https_fn.on_request(secrets=["OPENAI_API_KEY", "PINECONE_API_KEY"])
def new_message(req: https_fn.Request) -> https_fn.Response:
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    # Select the OpenAI LLM
    model = "gpt-3.5-turbo"

    # Supply the System message
    messages = [{
        "role": "system",
        "content": "You are an assistant to employees at Jahnel Group. \
                    Your job is to answer questions about the company."
    }]

    # Equip the assistant with the Function
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
    
    # Get the user's message from the textbox in the form
    user_msg = req.form["userInput"]

    # Add the user's message to the conversation
    messages.append({"role": "user", "content": user_msg})

    # Ask GPT to generate a response
    completion = openai_client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    # Get the message from GPT
    assistant_msg = completion.choices[0].message

    # If GPT generated a response, add it to the conversation and return dialogue
    if assistant_msg.content:
        messages.append({"role": "assistant", "content": assistant_msg.content})
        return {
            "userMsg": user_msg,
            "assistantMsg": assistant_msg.content
        }

    # No message was given, so get the function
    function = assistant_msg.tool_calls[0].function

    # Make sure that the function is the one we expect
    if function.name == "searchDocs":
        import functions

        # Get the argument for the function
        args = json.loads(function.arguments)
        summary = args["summary"]
        
        # Call the function
        result = functions.searchDocs(summary)
        
        # Add the result to the conversation
        messages.append({
            "role": "function",
            "name": "searchDocs",
            "content": result
        })
    else:
        raise ValueError(f"Unknown function: {function.name}")
    
    # Ask GPT to generate a response with the function result in its context
    completion = openai_client.chat.completions.create(
        model=model,
        messages=messages
    )

    # Get the message from GPT
    assistant_msg = completion.choices[0].message

    # Add the assistant's message to the conversation
    messages.append({"role": "assistant", "content": assistant_msg.content})
    
    # Return the dialogue
    return {
        "userMsg": user_msg,
        "assistantMsg": assistant_msg.content
    }
