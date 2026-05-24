import os

from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    current_app
)

from werkzeug.utils import secure_filename
from flask_login import login_required

upload_bp = Blueprint(
    "upload",
    __name__,
    url_prefix="/dashboard"
)

ALLOWED_EXTENSIONS = {"xlsx", "xls"}


def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route("/upload-excel", methods=["GET", "POST"])
@login_required
def upload_excel():

    if request.method == "GET":
        return render_template("dashboard/upload_excel.html")

    file_type = request.form.get("file_type")

    if file_type == "contract":
        upload_folder = current_app.config["CONTRACT_FOLDER"]
    else:
        upload_folder = current_app.config["SELLER_FOLDER"]

    files = request.files.getlist("files")

    uploaded = []

    for file in files:

        if file and allowed_file(file.filename):

            filename = secure_filename(file.filename)

            filepath = os.path.join(upload_folder, filename)

            base, ext = os.path.splitext(filename)

            counter = 1

            while os.path.exists(filepath):

                filename = f"{base}_{counter}{ext}"

                filepath = os.path.join(upload_folder, filename)

                counter += 1

            file.save(filepath)

            uploaded.append(filename)

    return jsonify({
        "status": "success",
        "uploaded": uploaded
    })