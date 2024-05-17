from flask import Flask, render_template, request
from backend import answer

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.post("/clicked")
def user():
    user_msg = request.form["userInput"]
    assistant_msg = answer(user_msg)

    return render_template(
        "filler.html",
        user_msg=user_msg,
        assistant_msg=assistant_msg
    )

if __name__ == "__main__":
    app.run(port=8000, debug=True)
