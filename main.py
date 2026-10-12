import os
import uuid
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_uploads')
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/create", methods=["GET", "POST"])
def create():
    uniqueId = uuid.uuid1()
    if request.method == "POST":
        rec_uuid = request.form.get("uuid")
        if not rec_uuid:
            rec_uuid = str(uniqueId)

        # Create target directory for this uuid inside user_uploads
        target_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(rec_uuid))
        os.makedirs(target_folder, exist_ok=True)

        # Save all uploaded files using secure_filename
        for key in request.files:
            file_list = request.files.getlist(key)
            for file in file_list:
                if file and file.filename != "":
                    filename = secure_filename(file.filename)
                    if filename:
                        file.save(os.path.join(target_folder, filename))

        # Save user text input as text.txt
        text_content = request.form.get("text", "")
        with open(os.path.join(target_folder, "text.txt"), "w", encoding="utf-8") as f:
            f.write(text_content)

        # Refresh uniqueId for the next submission
        uniqueId = uuid.uuid1()
        return render_template("create.html", myid=uniqueId, uuid=uniqueId, alert="Files and text uploaded successfully!")

    return render_template("create.html", myid=uniqueId, uuid=uniqueId)

@app.route("/gallery")
def gallery():
    return render_template("gallery.html")

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)