from firebase_functions import https_fn
from firebase_admin import initialize_app

initialize_app()


@https_fn.on_request()
def new_message(req: https_fn.Request) -> https_fn.Response:
    user_msg = req.form["userInput"]
    # assistant_msg = answer(user_msg)

    return {
        "userMsg": user_msg,
        "assistantMsg": "Hello, World!"
    }
