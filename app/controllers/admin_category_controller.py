from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request
)

from flask_login import (
    login_required
)

import pandas as pd

from ..forms.auth import UserForm
from ..forms.category_form import CategoryForm

from ..repositories import (
    category_repository
)

from ..extensions import db

from ..models.category import Category
from ..models.seller import Seller

from .admin_user_controller import admin_required


admin_category_bp = Blueprint(
    "admin_category",
    __name__,
    url_prefix="/admin/categories"
)


# =====================================================
# CATEGORY EXCEL UPLOAD
# =====================================================

@admin_category_bp.route("/upload_excel", methods=["GET", "POST"])
@login_required
@admin_required
def admin_category_upload_excel():

    form = UserForm()

    imported_categories = []

    if request.method == "POST":

        if "excel_file" not in request.files:

            flash(
                "No file part",
                "danger"
            )

            return redirect(request.url)

        file = request.files["excel_file"]

        if file.filename == "":

            flash(
                "No selected file",
                "danger"
            )

            return redirect(request.url)

        if not (
            file.filename.endswith(".xls")
            or
            file.filename.endswith(".xlsx")
        ):

            flash(
                "Please upload an Excel file (.xls or .xlsx)",
                "danger"
            )

            return redirect(request.url)

        try:

            df = pd.read_excel(file)

            required_columns = {
                "value",
                "text"
            }

            if not required_columns.issubset(
                df.columns.str.lower()
            ):

                flash(
                    f"Excel must contain columns: {', '.join(required_columns)}",
                    "danger"
                )

                return redirect(request.url)

            df.columns = df.columns.str.lower()

            count = 0

            for _, row in df.iterrows():

                category_repository.add_category(
                    row["value"],
                    row["text"]
                )

                count += 1

            flash(
                f"Successfully imported {count} categories.",
                "success"
            )

            imported_categories = df.to_dict(
                orient="records"
            )

        except Exception as e:

            flash(
                f"Failed to process Excel file: {str(e)}",
                "danger"
            )

    return render_template(
        "admin_user_upload_excel.html",
        form=form,
        action="Upload Categories",
        categories=imported_categories
    )


# =====================================================
# CATEGORY MANAGEMENT
# =====================================================

@admin_category_bp.route("/manage", methods=["GET", "POST"])
@login_required
@admin_required
def admin_category_manage():

    form = CategoryForm()

    categories = category_repository.get_all_categories()

    if form.validate_on_submit():

        if form.id.data:

            success = category_repository.update_category(
                form.id.data,
                form.value.data,
                form.text.data
            )

            if success:

                flash(
                    "Category updated.",
                    "success"
                )

            else:

                flash(
                    "Failed to update category.",
                    "danger"
                )

        else:

            if category_repository.add_category(
                form.value.data,
                form.text.data
            ):

                flash(
                    "Category added.",
                    "success"
                )

            else:

                flash(
                    "Category with this value already exists.",
                    "warning"
                )

        return redirect(
            url_for(
                "admin_category.admin_category_manage"
            )
        )

    delete_id = request.args.get("delete_id")

    if delete_id:

        if category_repository.delete_category(delete_id):

            flash(
                "Category deleted.",
                "success"
            )

        else:

            flash(
                "Category not found.",
                "warning"
            )

        return redirect(
            url_for(
                "admin_category.admin_category_manage"
            )
        )

    edit_id = request.args.get("edit_id")

    if edit_id:

        category = next(
            (
                c for c in categories
                if str(c.id) == edit_id
            ),
            None
        )

        if category:

            form.id.data = category.id

            form.value.data = category.value

            form.text.data = category.text

    return render_template(
        "admin_category_manage.html",
        form=form,
        categories=categories
    )


# =====================================================
# HELPER: EXACT CATEGORY EXTRACTION
# =====================================================

def extract_exact_categories_from_sellers():

    categories = set()

    seller_categories = db.session.query(
        Seller.category_name
    ).distinct().all()

    for (cat,) in seller_categories:

        if isinstance(cat, str):

            cat = cat.strip()

            if cat:
                categories.add(cat)

    return categories


# =====================================================
# UPLOAD CATEGORIES FROM SELLERS
# =====================================================

def upload_categories_from_sellers_exact():

    existing = {
        c.value
        for c in Category.query.with_entities(
            Category.value
        ).all()
    }

    found = extract_exact_categories_from_sellers()

    inserted = 0

    for category_name in found:

        if category_name in existing:
            continue

        db.session.add(
            Category(
                value=category_name[:255],
                text=category_name
            )
        )

        inserted += 1

    db.session.commit()

    return len(found), inserted


# =====================================================
# ADMIN ACTION
# =====================================================

@admin_category_bp.route(
    "/upload-from-sellers",
    methods=["POST"]
)
@login_required
@admin_required
def admin_upload_categories_from_sellers_exact():

    total_found, inserted = (
        upload_categories_from_sellers_exact()
    )

    flash(
        f"Upload completed. Found {total_found} categories in sellers, inserted {inserted} new categories.",
        "success"
    )

    return redirect(
        url_for(
            "admin_category.admin_category_manage"
        )
    )