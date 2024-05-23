from firebase_functions import https_fn
from firebase_functions.params import SecretParam

# from firebase_admin import initialize_app

# initialize_app()

OPENAI_API_KEY = SecretParam("OPENAI_API_KEY")
PINECONE_API_KEY = SecretParam("PINECONE_API_KEY")

@https_fn.on_request(secrets=[OPENAI_API_KEY, PINECONE_API_KEY])
def new_message(req: https_fn.Request) -> https_fn.Response:
    from backend import answer
    
    user_msg = req.form["userInput"]
    assistant_msg = answer(user_msg)

    return {
        "userMsg": user_msg,
        "assistantMsg": "Hello, World!"
    }
