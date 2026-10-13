import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'videosnap-secret-key-123')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        rec_uuid = request.form.get("uuid")
        if not rec_uuid:
            rec_uuid = str(uuid.uuid1())

        # Collect and validate files
        files_to_save = []
        for key in request.files:
            file_list = request.files.getlist(key)
            for file in file_list:
                if file and file.filename != "":
                    filename = secure_filename(file.filename)
                    if filename:
                        files_to_save.append((file, filename))

        text_content = request.form.get("text", "").strip()
        engine_choice = request.form.get("engine", "ffmpeg").strip().lower()
        if engine_choice not in {"ffmpeg", "moviepy"}:
            engine_choice = "ffmpeg"

        # Ensure at least one file is actually uploaded
        if not files_to_save:
            flash("Please upload at least one video file before submitting.", "danger")
            return redirect(url_for("create"))

        # Create target directory for this uuid inside user_uploads
        target_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(rec_uuid))
        os.makedirs(target_folder, exist_ok=True)

        # Save all uploaded files using secure_filename
        for file, filename in files_to_save:
            file.save(os.path.join(target_folder, filename))

        # Save user text input as text.txt
        with open(os.path.join(target_folder, "text.txt"), "w", encoding="utf-8") as f:
            f.write(text_content)

        # Save engine preference as engine.txt
        with open(os.path.join(target_folder, "engine.txt"), "w", encoding="utf-8") as f:
            f.write(engine_choice)

        flash("Files and text uploaded successfully!", "success")
        return redirect(url_for("create"))

    uniqueId = uuid.uuid1()
    return render_template("create.html", myid=uniqueId, uuid=uniqueId)

@app.route("/gallery")
def gallery():
    return render_template("gallery.html")

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)