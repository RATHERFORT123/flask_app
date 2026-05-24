from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    abort,
    request,
    current_app
)

from flask_login import (
    login_required,
    current_user
)

from ..forms.auth import UserForm

from ..repositories import user_repository

from ..extensions import db

from functools import wraps


admin_user_bp = Blueprint(
    "admin_user",
    __name__,
    url_prefix="/admin/users"
)


# =====================================================
# ADMIN REQUIRED
# =====================================================

def admin_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)

        return f(*args, **kwargs)

    return decorated_function


# =====================================================
# ADMIN DASHBOARD
# =====================================================

@admin_user_bp.route("/dashboard")
@login_required
@admin_required
def admin_dashboard():

    q = request.args.get("q", "").strip().lower()

    users = user_repository.get_all()

    if q:
        users = [
            u for u in users
            if q in u.username.lower() or q in u.email.lower()
        ]

    return render_template(
        "admin_dashboard.html",
        users=users,
        q=q
    )


# =====================================================
# CREATE USER
# =====================================================

@admin_user_bp.route("/create", methods=["GET", "POST"])
@login_required
@admin_required
def admin_user_create():

    form = UserForm()

    if form.validate_on_submit():

        user_repository.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data or "changeme123",
            is_admin=form.is_admin.data,
            is_verified=form.is_verified.data,
            is_blocked=form.is_blocked.data,
            address=form.address.data,
            number=form.number.data,
            comment=form.comment.data,
            category_names=form.category_names.data,
            brand_names=form.brand_names.data,
            assigned_date_range_start=form.assigned_date_range_start.data,
            assigned_date_range_end=form.assigned_date_range_end.data,
            subscription_date=form.subscription_date.data,
            amount=form.amount.data,
            payment_status=form.payment_status.data,
            subscription_plan=form.subscription_plan.data
        )

        flash("User created.", "success")

        return redirect(
            url_for("admin_user.admin_dashboard")
        )

    return render_template(
        "admin_user_form.html",
        form=form,
        action="Create"
    )


# =====================================================
# EDIT USER
# =====================================================

@admin_user_bp.route("/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def admin_user_edit(user_id):

    u = user_repository.get_by_id(user_id)

    if not u:
        abort(404)

    form = UserForm(obj=u)

    if request.method == "GET":

        form.category_names.data = u.category_names
        form.brand_names.data = u.brand_names

        form.assigned_date_range_start.data = u.assigned_date_range_start

        form.assigned_date_range_end.data = u.assigned_date_range_end

        form.subscription_date.data = u.subscription_date

        form.amount.data = u.amount

        form.payment_status.data = u.payment_status

        form.subscription_plan.data = u.subscription_plan

    if form.validate_on_submit():

        try:

            user_repository.update_user(
                u,
                username=form.username.data,
                email=form.email.data,
                password=form.password.data or None,
                is_admin=form.is_admin.data,
                is_verified=form.is_verified.data,
                is_blocked=form.is_blocked.data,
                address=form.address.data,
                number=form.number.data,
                comment=form.comment.data,
                category_names=form.category_names.data,
                brand_names=form.brand_names.data,
                assigned_date_range_start=form.assigned_date_range_start.data,
                assigned_date_range_end=form.assigned_date_range_end.data,
                subscription_date=form.subscription_date.data,
                amount=form.amount.data,
                payment_status=form.payment_status.data,
                subscription_plan=form.subscription_plan.data
            )

            flash("User updated.", "success")

            return redirect(
                url_for("admin_user.admin_dashboard")
            )

        except Exception:

            db.session.rollback()

            current_app.logger.exception(
                "User update failed"
            )

            flash(
                "Update failed. Please try again.",
                "danger"
            )

    return render_template(
        "admin_user_form.html",
        form=form,
        action="Update"
    )


# =====================================================
# DELETE USER
# =====================================================

@admin_user_bp.route("/<int:user_id>/delete", methods=["POST"])
@login_required
@admin_required
def admin_user_delete(user_id):

    u = user_repository.get_by_id(user_id)

    if not u:
        abort(404)

    if u.id == current_user.id:

        flash(
            "You cannot delete your own admin account.",
            "warning"
        )

        return redirect(
            url_for("admin_user.admin_dashboard")
        )

    user_repository.delete_user(u)

    flash("User deleted.", "success")

    return redirect(
        url_for("admin_user.admin_dashboard")
    )


# =====================================================
# TOGGLE VERIFY
# =====================================================

@admin_user_bp.route("/<int:user_id>/toggle-verify", methods=["POST"])
@login_required
@admin_required
def admin_user_toggle_verify(user_id):

    u = user_repository.get_by_id(user_id)

    if not u:
        abort(404)

    u.is_verified = not u.is_verified

    db.session.commit()

    flash(
        "Verification status updated.",
        "success"
    )

    return redirect(
        url_for("admin_user.admin_dashboard")
    )


# =====================================================
# TOGGLE BLOCK
# =====================================================

@admin_user_bp.route("/<int:user_id>/toggle-block", methods=["POST"])
@login_required
@admin_required
def admin_user_toggle_block(user_id):

    u = user_repository.get_by_id(user_id)

    if not u:
        abort(404)

    if u.id == current_user.id:

        flash(
            "You cannot block/unblock your own admin account.",
            "warning"
        )

        return redirect(
            url_for("admin_user.admin_dashboard")
        )

    u.is_blocked = not u.is_blocked

    db.session.commit()

    flash(
        "User block status updated.",
        "success"
    )

    return redirect(
        url_for("admin_user.admin_dashboard")
    )