from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.post("/user")
def user():
    user_input = request.form["user"]
    return redirect("/")

if __name__ == "__main__":
    app.run()
