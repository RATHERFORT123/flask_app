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

from ..extensions import db

from ..models.brand import Brand
from ..models.contract import Contract

from ..forms.brand_form import BrandForm

from ..repositories import (
    brand_repository
)

from .admin_user_controller import admin_required


admin_brand_bp = Blueprint(
    "admin_brand",
    __name__,
    url_prefix="/admin/brands"
)


# =====================================================
# BRAND MANAGEMENT
# =====================================================

@admin_brand_bp.route("/manage", methods=["GET", "POST"])
@login_required
@admin_required
def admin_brand_manage():

    form = BrandForm()

    brands = brand_repository.get_all_brands()

    if form.validate_on_submit():

        if form.id.data:

            success = brand_repository.update_brand(
                form.id.data,
                form.code.data,
                form.product_count.data,
                form.name.data
            )

            if success:

                flash(
                    "Brand updated.",
                    "success"
                )

            else:

                flash(
                    "Failed to update brand.",
                    "danger"
                )

        else:

            if brand_repository.add_brand(
                form.code.data,
                form.product_count.data,
                form.name.data
            ):

                flash(
                    "Brand added.",
                    "success"
                )

            else:

                flash(
                    "Brand with this code already exists.",
                    "warning"
                )

        return redirect(
            url_for(
                "admin_brand.admin_brand_manage"
            )
        )

    delete_id = request.args.get("delete_id")

    if delete_id:

        if brand_repository.delete_brand(delete_id):

            flash(
                "Brand deleted.",
                "success"
            )

        else:

            flash(
                "Brand not found.",
                "warning"
            )

        return redirect(
            url_for(
                "admin_brand.admin_brand_manage"
            )
        )

    edit_id = request.args.get("edit_id")

    if edit_id:

        brand = next(
            (
                b for b in brands
                if str(b.id) == edit_id
            ),
            None
        )

        if brand:

            form.id.data = brand.id

            form.code.data = brand.code

            form.product_count.data = brand.product_count

            form.name.data = brand.name

    return render_template(
        "admin_brand_manage.html",
        form=form,
        brands=brands
    )


# =====================================================
# BRAND EXCEL UPLOAD
# =====================================================

@admin_brand_bp.route(
    "/upload_excel",
    methods=["GET", "POST"]
)
@login_required
@admin_required
def admin_brand_upload_excel():

    if request.method == "POST":

        file = request.files.get(
            "excel_file"
        )

        if not file or not (
            file.filename.endswith(".xls")
            or
            file.filename.endswith(".xlsx")
        ):

            flash(
                "Please upload a valid Excel file (.xls or .xlsx)",
                "danger"
            )

            return redirect(request.url)

        df = pd.read_excel(file)

        df.columns = [
            c.strip().lower().replace(" ", "_")
            for c in df.columns
        ]

        required_cols = {
            "code",
            "product_count",
            "brand"
        }

        if not required_cols.issubset(
            df.columns
        ):

            flash(
                "Excel file missing required columns: code, product_count, brand",
                "danger"
            )

            return redirect(request.url)

        count = 0

        for _, row in df.iterrows():

            code_val = (
                row["code"]
                if not pd.isna(row["code"])
                else "Unknown"
            )

            product_count_val = (
                int(row["product_count"])
                if not pd.isna(
                    row["product_count"]
                )
                else 0
            )

            brand_val = (
                row["brand"]
                if not pd.isna(row["brand"])
                else "Unknown"
            )

            brand_repository.add_brand(
                code_val,
                product_count_val,
                brand_val
            )

            count += 1

        flash(
            f"Successfully imported {count} brands.",
            "success"
        )

        return redirect(
            url_for(
                "admin_brand.admin_brand_manage"
            )
        )

    return render_template(
        "admin_brand_upload.html"
    )


# =====================================================
# EXTRACT EXACT BRANDS
# =====================================================

def extract_exact_brands_from_contracts():

    brands = set()

    contracts = Contract.query.with_entities(
        Contract.items
    ).all()

    for (items,) in contracts:

        if not items:
            continue

        for item in items:

            if isinstance(item, dict):

                brand = item.get("brand")

                if isinstance(brand, str):

                    brand = brand.strip()

                    if brand:
                        brands.add(brand)

    return brands


# =====================================================
# UPLOAD BRANDS FROM CONTRACTS
# =====================================================

def upload_brands_from_contracts_exact():

    existing = {
        b.name
        for b in Brand.query.with_entities(
            Brand.name
        ).all()
    }

    found = extract_exact_brands_from_contracts()

    inserted = 0

    for brand_name in found:

        if brand_name in existing:
            continue

        db.session.add(
            Brand(
                code=brand_name[:200],
                name=brand_name,
                product_count=0
            )
        )

        inserted += 1

    db.session.commit()

    return len(found), inserted


# =====================================================
# BRAND MANAGEMENT PAGE
# =====================================================

@admin_brand_bp.route("/", methods=["GET", "POST"])
@login_required
@admin_required
def admin_brand_manage_page():

    form = BrandForm()

    edit_id = request.args.get(
        "edit_id",
        type=int
    )

    delete_id = request.args.get(
        "delete_id",
        type=int
    )

    # DELETE

    if delete_id:

        brand = Brand.query.get_or_404(
            delete_id
        )

        db.session.delete(brand)

        db.session.commit()

        flash(
            "Brand deleted successfully.",
            "success"
        )

        return redirect(
            url_for(
                "admin_brand.admin_brand_manage_page"
            )
        )

    # EDIT

    editing_brand = None

    if edit_id:

        editing_brand = Brand.query.get_or_404(
            edit_id
        )

        form.code.data = editing_brand.code

        form.product_count.data = (
            editing_brand.product_count
        )

        form.name.data = editing_brand.name

    # SAVE

    if form.validate_on_submit():

        if editing_brand:

            editing_brand.code = form.code.data

            editing_brand.product_count = (
                form.product_count.data
            )

            editing_brand.name = form.name.data

        else:

            db.session.add(
                Brand(
                    code=form.code.data,
                    product_count=form.product_count.data,
                    name=form.name.data
                )
            )

        db.session.commit()

        flash(
            "Brand saved successfully.",
            "success"
        )

        return redirect(
            url_for(
                "admin_brand.admin_brand_manage_page"
            )
        )

    brands = Brand.query.order_by(
        Brand.name
    ).all()

    return render_template(
        "admin_brand_manage.html",
        brands=brands,
        form=form,
        edit_brand=editing_brand
    )


# =====================================================
# UPLOAD FROM CONTRACTS
# =====================================================

@admin_brand_bp.route(
    "/upload-from-contracts",
    methods=["POST"]
)
@login_required
@admin_required
def admin_upload_brands_from_contracts_exact():

    total_found, inserted = (
        upload_brands_from_contracts_exact()
    )

    flash(
        f"Upload completed. Found {total_found} brands in contracts, inserted {inserted} new brands.",
        "success"
    )

    return redirect(
        url_for(
            "admin_brand.admin_brand_manage_page"
        )
    )