from flask import (
    Blueprint,
    render_template,
    jsonify,
    abort
)

from flask_login import (
    login_required,
    current_user
)

from ..services.seller_excel_worker import (
    process_next_pending as process_seller_pending,
    retry_all_failed as retry_seller_failed,
    load_progress as seller_progress
)

from .contract_excel_controller import run_bg

seller_excel_bp = Blueprint(
    "seller_excel",
    __name__,
    url_prefix="/admin/sellers"
)


@seller_excel_bp.route("/excel-processor", methods=["GET"])
@login_required
def admin_seller_worker():

    if not current_user.is_admin:
        abort(403)

    return render_template("admin_seller_worker.html")


@seller_excel_bp.route("/process-pending", methods=["POST"])
@login_required
def process_seller_excel():

    if not current_user.is_admin:
        abort(403)

    run_bg(process_seller_pending)

    return jsonify({"status": "started"})


@seller_excel_bp.route("/retry-all", methods=["POST"])
@login_required
def retry_seller_excel():

    if not current_user.is_admin:
        abort(403)

    run_bg(retry_seller_failed)

    return jsonify({"status": "retry_started"})


@seller_excel_bp.route("/progress", methods=["GET"])
@login_required
def seller_progress_api():

    if not current_user.is_admin:
        abort(403)

    return jsonify(seller_progress())