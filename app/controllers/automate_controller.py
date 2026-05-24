

from functools import wraps
from flask import Blueprint, render_template, request, abort
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy import and_
from ..models.seller import Seller
from ..models.brand import Brand

from ..models.contract import Contract
from flask import Blueprint, render_template, request, jsonify
from ..repositories.analytics_repository import AnalyticsRepository
from ..extensions import db


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
# Create Blueprint
automate_bp = Blueprint(
    "automate",
    __name__,
    url_prefix="/automate"
)   

@automate_bp.route("/", methods=["GET"])
@login_required
def automate_home():
    return jsonify({
        "status": "success",
        "message": "Automate controller working"
    })

@automate_bp.route("/run", methods=["POST"])
@login_required
def run_automation():
    data = request.json or {}

    task_name = data.get("task_name", "default_task")

    #  automation logic here
    result = {
        "task": task_name,
        "status": "completed"
    }

    return jsonify(result)



from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required
from app.tasks.automate_tasks import run_gem_scraper_task

automate_bp = Blueprint("automate", __name__, url_prefix="/automate")

@automate_bp.route("/", methods=["GET"])
@login_required
def automate_page():
    return render_template("automate.html")

@automate_bp.route("/start", methods=["POST"])
@login_required
def start_automation():
    data = request.json or {}
    start_date = data.get("start_date")
    category = data.get("category", "")

    if not start_date:
        return jsonify({"error": "start_date required"}), 400

    job = run_gem_scraper_task.delay(start_date, category)

    return jsonify({
        "status": "started",
        "task_id": job.id
    })
