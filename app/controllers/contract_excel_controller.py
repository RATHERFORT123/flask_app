import threading

from flask import (
    Blueprint,
    render_template,
    jsonify,
    abort,
    current_app
)

from flask_login import (
    login_required,
    current_user
)

from ..services.contract_excel_worker import (
    process_next_pending,
    retry_all_failed,
    load_progress
)

from .admin_user_controller import admin_required


contract_excel_bp = Blueprint(
    "contract_excel",
    __name__,
    url_prefix="/admin/contracts"
)


# =====================================================
# BACKGROUND THREAD
# =====================================================

_worker_thread = None


def run_bg(task_func):

    global _worker_thread

    if _worker_thread and _worker_thread.is_alive():
        return False

    app = current_app._get_current_object()

    def wrapper():

        with app.app_context():

            task_func()

    _worker_thread = threading.Thread(
        target=wrapper
    )

    _worker_thread.daemon = True

    _worker_thread.start()

    return True


# =====================================================
# CONTRACT WORKER PAGE
# =====================================================

@contract_excel_bp.route(
    "/excel-processor",
    methods=["GET"]
)
@login_required
@admin_required
def admin_contract_worker():

    if not current_user.is_admin:
        abort(403)

    return render_template(
        "admin_contract_worker.html"
    )


# =====================================================
# PROCESS PENDING FILES
# =====================================================

@contract_excel_bp.route(
    "/process-pending",
    methods=["POST"]
)
@login_required
@admin_required
def process_pending():

    if not current_user.is_admin:
        abort(403)

    run_bg(process_next_pending)

    return jsonify({
        "status": "started"
    })


# =====================================================
# RETRY FAILED FILES
# =====================================================

@contract_excel_bp.route(
    "/retry-all",
    methods=["POST"]
)
@login_required
@admin_required
def retry_all():

    if not current_user.is_admin:
        abort(403)

    run_bg(retry_all_failed)

    return jsonify({
        "status": "retry_started"
    })


# =====================================================
# LIVE PROGRESS API
# =====================================================

@contract_excel_bp.route(
    "/progress",
    methods=["GET"]
)
@login_required
@admin_required
def progress():

    if not current_user.is_admin:
        abort(403)

    return jsonify(
        load_progress()
    )