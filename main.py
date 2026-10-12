from flask import Flask, render_template, request
import uuid

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/create", methods=["GET", "POST"])
def create():
    uniqueId = uuid.uuid1()
    if request.method == "POST":
        print(request.files.keys())
        for key, value in request.files.items():
            print(key, value)

    return render_template("create.html", uuid=uniqueId)

@app.route("/gallery")
def gallery():
    return render_template("gallery.html")

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)