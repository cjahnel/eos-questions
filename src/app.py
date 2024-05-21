from flask import Flask, request
from backend import answer
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.post("/api")
def user():
    user_msg = request.form["userInput"]
    assistant_msg = answer(user_msg)

    return {
        "userMsg": user_msg,
        "assistantMsg": assistant_msg
    }

if __name__ == "__main__":
    app.run(port=8000, debug=True)
