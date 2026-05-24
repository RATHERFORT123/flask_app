# from flask import (
#     Blueprint,
#     render_template,
#     redirect,
#     url_for,
#     flash,
#     request
# )

# from flask_login import (
#     login_required
# )

# import pandas as pd

# import re

# from ..forms.seller_form import SellerForm

# from ..repositories import (
#     seller_repository
# )

# from .admin_user_controller import admin_required


# admin_seller_bp = Blueprint(
#     "admin_seller",
#     __name__,
#     url_prefix="/admin/sellers"
# )


# # =====================================================
# # SELLER MANAGEMENT
# # =====================================================

# # @admin_seller_bp.route(
# #     "/manage",
# #     methods=["GET", "POST"]
# # )
# # @login_required
# # @admin_required
# # def manage_sellers():

# #     form = SellerForm()

# #     page = request.args.get(
# #         "page",
# #         1,
# #         type=int
# #     )

# #     filters = {
# #         k: v
# #         for k, v in {
# #             "contract_no": request.args.get(
# #                 "contract_no",
# #                 type=str
# #             ),

# #             "category_name": request.args.get(
# #                 "category_name",
# #                 type=str
# #             ),

# #             "seller_id": request.args.get(
# #                 "seller_id",
# #                 type=str
# #             ),

# #             "company_name": request.args.get(
# #                 "company_name",
# #                 type=str
# #             ),

# #             "contact_no": request.args.get(
# #                 "contact_no",
# #                 type=str
# #             ),

# #             "email": request.args.get(
# #                 "email",
# #                 type=str
# #             ),

# #             "msme_reg_no": request.args.get(
# #                 "msme_reg_no",
# #                 type=str
# #             ),

# #             "gstin": request.args.get(
# #                 "gstin",
# #                 type=str
# #             ),

# #             "generated_date": request.args.get(
# #                 "generated_date",
# #                 type=str
# #             ),

# #         }.items()

# #         if v
# #     }

# #     sellers_paginated = (
# #         seller_repository.get_sellers_filtered_paginated(
# #             filters,
# #             page=page
# #         )
# #     )

# #     sellers = sellers_paginated.items

# #     if form.validate_on_submit():

# #         data = form.data.copy()

# #         data.pop(
# #             "csrf_token",
# #             None
# #         )

# #         if seller_repository.add_or_update_seller(
# #             data
# #         ):

# #             flash(
# #                 "Seller added/updated successfully.",
# #                 "success"
# #             )

# #         else:

# #             flash(
# #                 "Failed to add/update seller.",
# #                 "danger"
# #             )

# #         return redirect(
# #             url_for(
# #                 "admin_seller.manage_sellers"
# #             )
# #         )

# #     delete_id = request.args.get(
# #         "delete_id",
# #         type=int
# #     )

# #     if delete_id:

# #         deleted_count = (
# #             seller_repository.bulk_delete_sellers(
# #                 [delete_id]
# #             )
# #         )

# #         if deleted_count > 0:

# #             flash(
# #                 "Seller deleted successfully.",
# #                 "success"
# #             )

# #         else:

# #             flash(
# #                 "Seller not found.",
# #                 "warning"
# #             )

# #         return redirect(
# #             url_for(
# #                 "admin_seller.manage_sellers"
# #             )
# #         )

# #     edit_id = request.args.get(
# #         "edit_id",
# #         type=int
# #     )

# #     if edit_id:

# #         seller = next(
# #             (
# #                 s for s in sellers
# #                 if s.id == edit_id
# #             ),
# #             None
# #         )

# #         if seller:

# #             form.contract_no.data = (
# #                 seller.contract_no
# #             )

# #             form.generated_date.data = (
# #                 seller.generated_date
# #             )

# #             form.category_name.data = (
# #                 seller.category_name
# #             )

# #             form.seller_id.data = (
# #                 seller.seller_id
# #             )

# #             form.company_name.data = (
# #                 seller.company_name
# #             )

# #             form.contact_no.data = (
# #                 seller.contact_no
# #             )

# #             form.email.data = (
# #                 seller.email
# #             )

# #             form.address.data = (
# #                 seller.address
# #             )

# #             form.msme_reg_no.data = (
# #                 seller.msme_reg_no
# #             )

# #             form.gstin.data = (
# #                 seller.gstin
# #             )

# #     return render_template(
# #         "admin_seller_manage.html",
# #         form=form,
# #         sellers=sellers,
# #         pagination=sellers_paginated,
# #         filters=filters
# #     )

# from flask import (
#     render_template,
#     request,
#     redirect,
#     url_for,
#     flash
# )

# from flask_login import login_required

# from sqlalchemy import func

# from app.extensions import db

# from app.models.contract import Contract
# from app.models.seller import Seller

# from app.forms.seller_form import SellerForm

# # from app.auth.decorators import admin_required


# @admin_seller_bp.route(
#     "/manage",
#     methods=["GET", "POST"]
# )
# @login_required
# @admin_required
# def manage_sellers():

#     form = SellerForm()

#     page = request.args.get(
#         "page",
#         1,
#         type=int
#     )

#     # =====================================================
#     # FILTERS
#     # =====================================================

#     filters = {
#         k: v
#         for k, v in {

#             "contract_no": request.args.get(
#                 "contract_no",
#                 type=str
#             ),

#             "category_name": request.args.get(
#                 "category_name",
#                 type=str
#             ),

#             "seller_id": request.args.get(
#                 "seller_id",
#                 type=str
#             ),

#             "company_name": request.args.get(
#                 "company_name",
#                 type=str
#             ),

#             "contact_no": request.args.get(
#                 "contact_no",
#                 type=str
#             ),

#             "email": request.args.get(
#                 "email",
#                 type=str
#             ),

#             "msme_reg_no": request.args.get(
#                 "msme_reg_no",
#                 type=str
#             ),

#             "gstin": request.args.get(
#                 "gstin",
#                 type=str
#             ),

#         }.items()

#         if v
#     }

#     # =====================================================
#     # JOIN QUERY
#     # =====================================================

#     query = (

#         db.session.query(
#             Seller,
#             Contract.total,
#             Contract.contract_date
#         )

#         .outerjoin(
#             Contract,
#             Seller.contract_no == Contract.contract_id
#         )

#     )


#     # records = query.limit(10).all()

#     # for seller, total, contract_date in records:

#     #     print("SELLER CONTRACT :", seller.contract_no)
#     #     print("TOTAL :", total)
#     #     print("DATE :", contract_date)
#     #     print("-" * 50)

#     # =====================================================
#     # FILTERS
#     # =====================================================

#     if filters.get("contract_no"):

#         query = query.filter(
#             Seller.contract_no.ilike(
#                 f"%{filters['contract_no']}%"
#             )
#         )

#     if filters.get("category_name"):

#         query = query.filter(
#             Seller.category_name.ilike(
#                 f"%{filters['category_name']}%"
#             )
#         )

#     if filters.get("seller_id"):

#         query = query.filter(
#             Seller.seller_id.ilike(
#                 f"%{filters['seller_id']}%"
#             )
#         )

#     if filters.get("company_name"):

#         query = query.filter(
#             Seller.company_name.ilike(
#                 f"%{filters['company_name']}%"
#             )
#         )

#     if filters.get("contact_no"):

#         query = query.filter(
#             Seller.contact_no.ilike(
#                 f"%{filters['contact_no']}%"
#             )
#         )

#     if filters.get("email"):

#         query = query.filter(
#             Seller.email.ilike(
#                 f"%{filters['email']}%"
#             )
#         )

#     if filters.get("msme_reg_no"):

#         query = query.filter(
#             Seller.msme_reg_no.ilike(
#                 f"%{filters['msme_reg_no']}%"
#             )
#         )

#     if filters.get("gstin"):

#         query = query.filter(
#             Seller.gstin.ilike(
#                 f"%{filters['gstin']}%"
#             )
#         )

#     # =====================================================
#     # TOTAL SUM
#     # =====================================================

#     total_sum = (

#         query.with_entities(
#             func.sum(Contract.total)
#         ).scalar()

#     ) or 0

#     # =====================================================
#     # PAGINATION
#     # =====================================================



    

#     sellers_paginated = query.order_by(
#         Seller.id.desc()
#     ).paginate(
#         page=page,
#         per_page=50,
#         error_out=False
#     )

#     sellers = sellers_paginated.items

#     # =====================================================
#     # ADD / UPDATE
#     # =====================================================

#     if form.validate_on_submit():

#         data = form.data.copy()

#         data.pop(
#             "csrf_token",
#             None
#         )

#         if seller_repository.add_or_update_seller(
#             data
#         ):

#             flash(
#                 "Seller added/updated successfully.",
#                 "success"
#             )

#         else:

#             flash(
#                 "Failed to add/update seller.",
#                 "danger"
#             )

#         return redirect(
#             url_for(
#                 "admin_seller.manage_sellers"
#             )
#         )

#     # =====================================================
#     # DELETE
#     # =====================================================

#     delete_id = request.args.get(
#         "delete_id",
#         type=int
#     )

#     if delete_id:

#         deleted_count = (
#             seller_repository.bulk_delete_sellers(
#                 [delete_id]
#             )
#         )

#         if deleted_count > 0:

#             flash(
#                 "Seller deleted successfully.",
#                 "success"
#             )

#         else:

#             flash(
#                 "Seller not found.",
#                 "warning"
#             )

#         return redirect(
#             url_for(
#                 "admin_seller.manage_sellers"
#             )
#         )

#     # =====================================================
#     # EDIT
#     # =====================================================

#     edit_id = request.args.get(
#         "edit_id",
#         type=int
#     )

#     if edit_id:

#         seller = next(
#             (
#                 s[0] for s in sellers
#                 if s[0].id == edit_id
#             ),
#             None
#         )

#         if seller:

#             form.contract_no.data = seller.contract_no
#             form.generated_date.data = seller.generated_date
#             form.category_name.data = seller.category_name
#             form.seller_id.data = seller.seller_id
#             form.company_name.data = seller.company_name
#             form.contact_no.data = seller.contact_no
#             form.email.data = seller.email
#             form.address.data = seller.address
#             form.msme_reg_no.data = seller.msme_reg_no
#             form.gstin.data = seller.gstin

#     return render_template(
#         "admin_seller_manage.html",
#         form=form,
#         sellers=sellers,
#         pagination=sellers_paginated,
#         filters=filters,
#         total_sum=total_sum
#     )
# # =====================================================
# # SELLER EXCEL UPLOAD
# # =====================================================

# @admin_seller_bp.route(
#     "/upload_excel",
#     methods=["GET", "POST"]
# )
# @login_required
# @admin_required
# def upload_sellers_excel():

#     form = SellerForm()

#     if request.method == "POST":

#         file = request.files.get(
#             "excel_file"
#         )

#         if not file or not (
#             file.filename.endswith(".xls")
#             or
#             file.filename.endswith(".xlsx")
#         ):

#             flash(
#                 "Upload a valid Excel file (.xls or .xlsx)",
#                 "danger"
#             )

#             return redirect(request.url)

#         def clean_column_name(c):

#             c = c.strip().lower()

#             c = c.replace(
#                 " ",
#                 "_"
#             )

#             c = re.sub(
#                 r"[^\w]",
#                 "",
#                 c
#             )

#             return c

#         df = pd.read_excel(file)

#         df.columns = [
#             clean_column_name(c)
#             for c in df.columns
#         ]

#         seller_fields = [
#             "contract_no",
#             "generated_date",
#             "category_name",
#             "seller_id",
#             "company_name",
#             "contact_no",
#             "email",
#             "address",
#             "msme_reg_no",
#             "gstin"
#         ]

#         count = 0

#         for _, row in df.iterrows():

#             data = {
#                 field: row.get(field)
#                 for field in seller_fields
#             }

#             if seller_repository.add_or_update_seller(
#                 data
#             ):

#                 count += 1

#         flash(
#             f"Successfully imported {count} sellers.",
#             "success"
#         )

#         return redirect(
#             url_for(
#                 "admin_seller.manage_sellers"
#             )
#         )

#     return render_template(
#         "admin_seller_upload.html",
#         form=form
#     )
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request
)
from flask_login import login_required
import pandas as pd
import re

from ..extensions import db
from ..models.seller import Seller
from ..forms.seller_form import SellerForm
from ..repositories import seller_repository
from .admin_user_controller import admin_required

admin_seller_bp = Blueprint(
    "admin_seller",
    __name__,
    url_prefix="/admin/sellers"
)

# =====================================================
# SELLER MANAGEMENT (NO JOINS - MAXIMUM PERFORMANCE)
# =====================================================

@admin_seller_bp.route("/manage", methods=["GET", "POST"])
@login_required
@admin_required
def manage_sellers():
    form = SellerForm()
    page = request.args.get("page", 1, type=int)

    # 1. Gather filter criteria from query parameters
    filters = {
        k: v
        for k, v in {
            "contract_no": request.args.get("contract_no", type=str),
            "category_name": request.args.get("category_name", type=str),
            "seller_id": request.args.get("seller_id", type=str),
            "company_name": request.args.get("company_name", type=str),
            "contact_no": request.args.get("contact_no", type=str),
            "email": request.args.get("email", type=str),
            "msme_reg_no": request.args.get("msme_reg_no", type=str),
            "gstin": request.args.get("gstin", type=str),
            "generated_date": request.args.get("generated_date", type=str),
        }.items()
        if v
    }

    # 2. Pure Seller Table Query (No Contract joins)
    query = Seller.query

    # 3. Apply search filters dynamically directly to the Seller table
    if filters.get("contract_no"):
        query = query.filter(Seller.contract_no.ilike(f"%{filters['contract_no']}%"))
    if filters.get("category_name"):
        query = query.filter(Seller.category_name.ilike(f"%{filters['category_name']}%"))
    if filters.get("seller_id"):
        query = query.filter(Seller.seller_id == filters['seller_id'])
    if filters.get("company_name"):
        query = query.filter(Seller.company_name.ilike(f"%{filters['company_name']}%"))
    if filters.get("contact_no"):
        query = query.filter(Seller.contact_no.ilike(f"%{filters['contact_no']}%"))
    if filters.get("email"):
        query = query.filter(Seller.email.ilike(f"%{filters['email']}%"))
    if filters.get("msme_reg_no"):
        query = query.filter(Seller.msme_reg_no.ilike(f"%{filters['msme_reg_no']}%"))
    if filters.get("gstin"):
        query = query.filter(Seller.gstin.ilike(f"%{filters['gstin']}%"))
    if filters.get("generated_date"):
        query = query.filter(Seller.generated_date == filters['generated_date'])

    # 4. Paginate directly from the sellers table (loads instantly)
    sellers_paginated = query.order_by(Seller.id.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    sellers = sellers_paginated.items

    # 5. Process New Entries or Direct Edits via UI Submission
    if form.validate_on_submit():
        data = form.data.copy()
        data.pop("csrf_token", None)

        if seller_repository.add_or_update_seller(data):
            flash("Seller added/updated successfully.", "success")
        else:
            flash("Failed to add/update seller.", "danger")
        return redirect(url_for("admin_seller.manage_sellers"))

    # 6. Handle Individual Record Deletion Tasks
    delete_id = request.args.get("delete_id", type=int)
    if delete_id:
        deleted_count = seller_repository.bulk_delete_sellers([delete_id])
        if deleted_count > 0:
            flash("Seller deleted successfully.", "success")
        else:
            flash("Seller not found.", "warning")
        return redirect(url_for("admin_seller.manage_sellers"))

    # 7. Repopulate Form with Entity Data when Modifying a Record
    edit_id = request.args.get("edit_id", type=int)
    if edit_id:
        # Note: 's' is now directly a Seller object, not a tuple (s[0]) because there is no join.
        seller = next((s for s in sellers if s.id == edit_id), None)
        if seller:
            form.contract_no.data = seller.contract_no
            form.generated_date.data = seller.generated_date
            form.category_name.data = seller.category_name
            form.seller_id.data = seller.seller_id
            form.company_name.data = seller.company_name
            form.contact_no.data = seller.contact_no
            form.email.data = seller.email
            form.address.data = seller.address
            form.msme_reg_no.data = seller.msme_reg_no
            form.gstin.data = seller.gstin
            
            if hasattr(form, 'service_start_date'):
                form.service_start_date.data = getattr(seller, 'service_start_date', None)
            if hasattr(form, 'service_end_date'):
                form.service_end_date.data = getattr(seller, 'service_end_date', None)

    # 8. Render Template without total_sum
    return render_template(
        "admin_seller_manage.html",
        form=form,
        sellers=sellers,
        pagination=sellers_paginated,
        filters=filters
    )

# =====================================================
# SELLER EXCEL UPLOAD
# =====================================================

@admin_seller_bp.route("/upload_excel", methods=["GET", "POST"])
@login_required
@admin_required
def upload_sellers_excel():
    form = SellerForm()

    if request.method == "POST":
        file = request.files.get("excel_file")
        if not file or not (file.filename.endswith(".xls") or file.filename.endswith(".xlsx")):
            flash("Upload a valid Excel file (.xls or .xlsx)", "danger")
            return redirect(request.url)

        def clean_column_name(c):
            c = c.strip().lower()
            c = c.replace(" ", "_")
            return re.sub(r"[^\w]", "", c)

        try:
            df = pd.read_excel(file)
            df.columns = [clean_column_name(c) for c in df.columns]

            seller_fields = [
                "contract_no", "generated_date", "category_name", 
                "seller_id", "company_name", "contact_no", "email", 
                "address", "msme_reg_no", "gstin", "service_start_date", "service_end_date"
            ]

            count = 0
            for _, row in df.iterrows():
                data = {}
                for field in seller_fields:
                    val = row.get(field)
                    if pd.isna(val):
                        if field == "service_start_date":
                            val = row.get("start_date")
                        elif field == "service_end_date":
                            val = row.get("end_date")
                        else:
                            val = None
                    data[field] = val

                if not data.get("contract_no"):
                    continue

                if seller_repository.add_or_update_seller(data):
                    count += 1

            flash(f"Successfully imported {count} sellers.", "success")
        except Exception as e:
            flash(f"Error reading file structure: {str(e)}", "danger")

        return redirect(url_for("admin_seller.manage_sellers"))

    return render_template(
        "admin_seller_upload.html",
        form=form
    )


# @login_required
# @admin_required
# def upload_sellers_excel():
#     form = SellerForm()

#     if request.method == "POST":
#         file = request.files.get("excel_file")

#         if not file or not (file.filename.endswith(".xls") or file.filename.endswith(".xlsx")):
#             flash("Upload a valid Excel file (.xls or .xlsx)", "danger")
#             return redirect(request.url)

#         try:
#             df = pd.read_excel(file)
#             df.columns = [clean_column_name(c) for c in df.columns]

#             # Extended fields tracking across all metrics
#             seller_fields = [
#                 "contract_no", "generated_date", "category_name",
#                 "seller_id", "company_name", "contact_no",
#                 "email", "address", "msme_reg_no", "gstin",
#                 "service_start_date", "service_end_date"
#             ]

#             count = 0
#             for _, row in df.iterrows():
#                 data = {field: row.get(field) for field in seller_fields}
                
#                 # Verify that mandatory index conditions are satisfied
#                 if not data.get("contract_no") or pd.isna(data["contract_no"]):
#                     continue

#                 # Parse chronological records into database date objects
#                 data["generated_date"] = safe_parse_date(data.get("generated_date"))
#                 data["service_start_date"] = safe_parse_date(data.get("service_start_date"))
#                 data["service_end_date"] = safe_parse_date(data.get("service_end_date"))

#                 if seller_repository.add_or_update_seller(data):
#                     count += 1

#             flash(f"Successfully imported {count} sellers.", "success")
#         except Exception as e:
#             flash(f"An error occurred while processing the file: {str(e)}", "danger")

#         return redirect(url_for("admin_seller.manage_sellers"))

#     return render_template(
#         "admin_seller_upload.html",
#         form=form
#     )