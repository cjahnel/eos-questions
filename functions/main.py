from firebase_functions import https_fn
from firebase_admin import initialize_app

initialize_app()


@https_fn.on_request()
def new_message(req: https_fn.Request) -> https_fn.Response:
    user_msg = req.form["userInput"]
    # assistant_msg = answer(user_msg)

    # return https_fn.Response("Hello world!")
    return {
        "userMsg": user_msg,
        "assistantMsg": "Hello, world!"
    }
