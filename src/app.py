from flask import Flask, render_template, request
from embeddings import completion

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.post("/clicked")
def user():
    user_text = request.form["user-input"]
    assistant_text = completion(user_text)
    return render_template("filler.html", user_text=user_text, assistant_text=assistant_text)

if __name__ == "__main__":
    app.run(debug=True)
