from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for
)

from flask_login import (
    login_required
)

common_bp = Blueprint(
    "common",
    __name__
)


# =====================================================
# PUBLIC PAGES (Home, About, Contact)
# =====================================================

@common_bp.route("/home")
def home():
    return render_template("home.html")


@common_bp.route("/about")
def about():
    return render_template("about.html")


@common_bp.route("/contact")
def contact():
    return render_template("contact.html")


# =====================================================
# ROOT
# =====================================================

@common_bp.route("/")
def root():
    # Option A: Redirect to the new home page instead of forcing a login dashboard
    return redirect(url_for("common.home"))
    
    # Option B: Keep your original logic (uncomment below if you prefer it)
    # return redirect(url_for("common.user_dashboard"))


# =====================================================
# USER DASHBOARD
# =====================================================

@common_bp.route("/dashboard")
@login_required
def user_dashboard():
    return render_template("user_dashboard.html")


# =====================================================
# ADMIN MAIN DASHBOARD PAGE
# =====================================================

@common_bp.route("/dashboard2")
@login_required
def dashboard2():
    return render_template("admin_main_dashboard.html")