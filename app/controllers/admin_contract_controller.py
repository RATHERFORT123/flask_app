# from flask import (
#     Blueprint,
#     request,
#     render_template,
#     redirect,
#     url_for,
#     flash,
#     jsonify,
#     abort
# )

# from flask_login import (
#     login_required
# )

# from datetime import datetime

# from sqlalchemy import and_

# from ..forms.contract_form import ContractForm

# from ..repositories import (
#     contract_repository
# )

# from ..models.contract import Contract
# from ..models.seller import Seller

# from .admin_user_controller import admin_required


# admin_contract_bp = Blueprint(
#     "admin_contract",
#     __name__,
#     url_prefix="/admin/contracts"
# )


# # =====================================================
# # DYNAMIC FILTER PARSER
# # =====================================================

# def parse_dynamic_filters(args):

#     filter_fields = [
#         "search",
#         "status",
#         "organization_type",
#         "ministry",
#         "department",
#         "organization_name",
#         "office_zone",
#         "location",
#         "buyer_designation",
#         "buying_mode",
#         "bid_number",
#         "contract_date",
#     ]

#     filters = {}

#     for field in filter_fields:

#         value = args.get(field, None, type=str)

#         if value and value.strip():

#             filters[field] = value.strip()

#     min_total = args.get(
#         "min_total",
#         None,
#         type=float
#     )

#     max_total = args.get(
#         "max_total",
#         None,
#         type=float
#     )

#     if min_total is not None:

#         filters["min_total"] = min_total

#     if max_total is not None:

#         filters["max_total"] = max_total

#     return filters


# # =====================================================
# # APPLY FILTERS
# # =====================================================

# def apply_contract_filters(query, filters):

#     for field, value in filters.items():

#         # =====================================
#         # SEARCH CONTRACT ID
#         # =====================================

#         if field == "search":

#             query = query.filter(
#                 Contract.contract_id == value.strip()
#             )

#             continue

#         # =====================================
#         # CONTRACT DATE
#         # =====================================

#         elif field == "contract_date":

#             try:

#                 date_val = datetime.strptime(
#                     value,
#                     "%Y-%m-%d"
#                 ).date()

#                 query = query.filter(
#                     Contract.contract_date == date_val
#                 )

#             except Exception:

#                 continue

#         # =====================================
#         # MIN TOTAL
#         # =====================================

#         elif field == "min_total":

#             query = query.filter(
#                 Contract.total >= value
#             )

#         # =====================================
#         # MAX TOTAL
#         # =====================================

#         elif field == "max_total":

#             query = query.filter(
#                 Contract.total <= value
#             )

#         # =====================================
#         # GENERIC FILTERS
#         # =====================================

#         else:

#             column = getattr(
#                 Contract,
#                 field,
#                 None
#             )

#             if column is not None:

#                 query = query.filter(
#                     column.ilike(f"%{value}%")
#                 )

#     return query


# # =====================================================
# # CONTRACT MANAGEMENT
# # =====================================================

# @admin_contract_bp.route("/", methods=["GET", "POST"])
# @login_required
# @admin_required
# def manage_contracts():

#     form = ContractForm()

#     page = request.args.get(
#         "page",
#         1,
#         type=int
#     )

#     per_page = 50

#     filters = parse_dynamic_filters(
#         request.args
#     )

#     query = Contract.query

#     # =====================================
#     # APPLY FILTERS
#     # =====================================

#     query = apply_contract_filters(
#         query,
#         filters
#     )

#     # =====================================
#     # ORDER
#     # =====================================

#     query = query.order_by(
#         Contract.contract_date.desc()
#     )

#     # =====================================
#     # PAGINATION
#     # =====================================

#     pagination = query.paginate(
#         page=page,
#         per_page=per_page,
#         error_out=False
#     )

#     contracts = pagination.items

#     # =====================================
#     # ADD CONTRACT
#     # =====================================

#     if form.validate_on_submit():

#         data = form.data.copy()

#         data.pop("csrf_token", None)

#         items = [
#             {
#                 "service": data.get("service"),
#                 "category_name": data.get("category_name"),
#                 "product": data.get("product"),
#                 "brand": data.get("brand"),
#                 "model": data.get("model"),
#                 "hsn_code": data.get("hsn_code"),
#                 "ordered_quantity": data.get("ordered_quantity"),
#                 "price": data.get("price"),
#             }
#         ]

#         data["items"] = items

#         if contract_repository.add_contract(data):

#             flash(
#                 "Contract added successfully.",
#                 "success"
#             )

#         else:

#             flash(
#                 "Failed to add contract.",
#                 "danger"
#             )

#         return redirect(
#             url_for(
#                 "admin_contract.manage_contracts"
#             )
#         )

#     return render_template(
#         "admin_contracts.html",
#         form=form,
#         contracts=contracts,
#         pagination=pagination,
#         filters_applied=filters,
#     )


# # =====================================================
# # CONTRACT API
# # =====================================================

# @admin_contract_bp.route("/api/<contract_id>")
# @login_required
# @admin_required
# def contract_api(contract_id):

#     contract = Contract.query.filter_by(
#         contract_id=contract_id
#     ).first()

#     if not contract:

#         return jsonify(
#             {
#                 "error": "Contract not found"
#             }
#         ), 404

#     seller = Seller.query.filter_by(
#         contract_no=contract.contract_id
#     ).first()

#     contract_data = {
#         "contract_id": contract.contract_id,
#         "status": contract.status,
#         "organization_name": contract.organization_name,
#         "contract_date": (
#             contract.contract_date.strftime("%Y-%m-%d")
#             if contract.contract_date
#             else ""
#         ),
#         "total": contract.total,
#         "items": contract.items or []
#     }

#     seller_data = None

#     if seller:

#         seller_data = {
#             "company_name": seller.company_name,
#             "seller_id": seller.seller_id,
#             "contact_no": seller.contact_no,
#             "email": seller.email,
#             "address": seller.address,
#             "msme_reg_no": seller.msme_reg_no,
#             "gstin": seller.gstin
#         }

#     return jsonify(
#         {
#             "contract": contract_data,
#             "seller": seller_data
#         }
#     )



from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for,
    flash,
    jsonify,
    abort
)
from flask_login import login_required
from datetime import datetime
import openpyxl
from sqlalchemy import String, and_
from ..forms.contract_form import ContractForm
from ..repositories import contract_repository
from ..models.contract import Contract
from ..models.seller import Seller
from .admin_user_controller import admin_required

admin_contract_bp = Blueprint(
    "admin_contract",
    __name__,
    url_prefix="/admin/contracts"
)

# =====================================================
# DYNAMIC FILTER PARSER
# =====================================================
def parse_dynamic_filters(args):
    # Base attributes matching core model columns exactly
    filter_fields = [
        "search",
        "status",
        "organization_type",
        "ministry",
        "department",
        "organization_name",
        "office_zone",
        "location",
        "buyer_designation",
        "buying_mode",
        "bid_number",
    ]

    filters = {}
    for field in filter_fields:
        value = args.get(field, None, type=str)
        if value and value.strip():
            filters[field] = value.strip()

    # Brand intercept mapping (JSON cross-table data lookup)
    brand_val = args.get("brand", None, type=str)
    if brand_val and brand_val.strip():
        filters["brand"] = brand_val.strip()

    # Explicit handling for UI range fields
    date_from = args.get("date_from", None, type=str)
    date_to = args.get("date_to", None, type=str)
    min_total = args.get("min_total", None, type=float)
    max_total = args.get("max_total", None, type=float)

    if date_from and date_from.strip():
        filters["date_from"] = date_from.strip()
    if date_to and date_to.strip():
        filters["date_to"] = date_to.strip()
    if min_total is not None:
        filters["min_total"] = min_total
    if max_total is not None:
        filters["max_total"] = max_total

    return filters

# =====================================================
# APPLY FILTERS
# =====================================================
def apply_contract_filters(query, filters):
    for field, value in filters.items():
        if field == "search":
            query = query.filter(Contract.contract_id == value)

        elif field == "date_from":
            try:
                date_val = datetime.strptime(value, "%Y-%m-%d").date()
                query = query.filter(Contract.contract_date >= date_val)
            except (ValueError, TypeError):
                continue

        elif field == "date_to":
            try:
                date_val = datetime.strptime(value, "%Y-%m-%d").date()
                query = query.filter(Contract.contract_date <= date_val)
            except (ValueError, TypeError):
                continue

        elif field == "min_total":
            query = query.filter(Contract.total >= value)

        elif field == "max_total":
            query = query.filter(Contract.total <= value)

        elif field == "brand":
            query = query.filter(
                Contract.items.cast(String).ilike(f"%{value}%")
            )

        else:
            column = getattr(Contract, field, None)
            if column is not None:
                query = query.filter(column.ilike(f"%{value}%"))

    return query

# =====================================================
# CONTRACT MANAGEMENT ROUTE
# =====================================================
@admin_contract_bp.route("/", methods=["GET", "POST"])
@login_required
@admin_required
def manage_contracts():
    form = ContractForm()
    
    # Isolate extraction mechanics exclusively to GET arguments processing maps
    page = request.args.get("page", 1, type=int)
    per_page = 50
    filters = parse_dynamic_filters(request.args)

    # Process Form Insertions (POST Context Execution)
    if request.method == "POST" and form.validate_on_submit():
        data = form.data.copy()
        data.pop("csrf_token", None)

        # Standard construction for relational mapping
        items = [{
            "service": data.get("service"),
            "category_name": data.get("category_name"),
            "product": data.get("product"),
            "brand": data.get("brand"),
            "model": data.get("model"),
            "hsn_code": data.get("hsn_code"),
            "ordered_quantity": data.get("ordered_quantity"),
            "price": data.get("price"),
        }]
        data["items"] = items

        if contract_repository.add_contract(data):
            flash("Contract added successfully.", "success")
            return redirect(url_for("admin_contract.manage_contracts"))
        else:
            flash("Failed to add contract structural reference layer.", "danger")

    # Evaluate display queries securely
    query = Contract.query
    query = apply_contract_filters(query, filters)
    query = query.order_by(Contract.contract_date.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        "admin_contracts.html",
        form=form,
        contracts=pagination.items,
        pagination=pagination,
        filters_applied=filters
    )

# =====================================================
# SECURE CONTRACT DETAIL API 
# =====================================================
@admin_contract_bp.route("/api/<contract_id>")
@login_required
@admin_required
def contract_api(contract_id):
    contract = Contract.query.filter_by(contract_id=contract_id).first()
    if not contract:
        return jsonify({"error": "Contract target profile index entry not found"}), 404

    seller = Seller.query.filter_by(contract_no=contract.contract_id).first()

    contract_data = {
        "contract_id": contract.contract_id,
        "status": contract.status,
        "organization_name": contract.organization_name,
        "contract_date": contract.contract_date.strftime("%Y-%m-%d") if contract.contract_date else "",
        "total": contract.total,
        "items": contract.items or []
    }

    seller_data = None
    if seller:
        seller_data = {
            "company_name": seller.company_name,
            "seller_id": seller.seller_id,
            "contact_no": seller.contact_no,
            "email": seller.email,
            "address": seller.address,
            "msme_reg_no": seller.msme_reg_no,
            "gstin": seller.gstin
        }

    return jsonify({
        "contract": contract_data,
        "seller": seller_data
    })




# =====================================================
# RENAME THE ROUTE AND THE FUNCTION TO AVOID CONFLICTS
# =====================================================
@admin_contract_bp.route("/contract/modal-api/<contract_id>") # <-- Changed path slightly
@login_required
@admin_required
def contract_modal_api(contract_id): # <-- Changed function name here!
    contract = Contract.query.filter_by(contract_id=contract_id).first()
    if not contract:
        return jsonify({"error": "Contract not found"}), 404
    
    seller = Seller.query.filter_by(contract_no=contract.contract_id).first()
    
    contract_data = {
        "contract_id": contract.contract_id,
        "status": contract.status,
        "organization_name": contract.organization_name,
        "contract_date": contract.contract_date.strftime("%Y-%m-%d") if contract.contract_date else "",
        "total": contract.total,
        "items": contract.items or []
    }
    
    seller_data = None
    if seller:
        seller_data = {
            "company_name": seller.company_name or "N/A",
            "seller_id": seller.seller_id or "N/A",
            "contact_no": seller.contact_no or "N/A",
            "email": seller.email or "N/A",
            "address": seller.address or "N/A",
            "msme_reg_no": seller.msme_reg_no or "N/A",
            "gstin": seller.gstin or "N/A"
        }
    
    return jsonify({"contract": contract_data, "seller": seller_data})




from flask import Blueprint, render_template, request, send_file, url_for
from io import BytesIO
import pandas as pd
from datetime import datetime
# from your_app.models import Contract, db  # Adjust import names to your project structure

user = Blueprint('user', __name__)

def build_filtered_contracts_query(filters):
    """
    Constructs a reusable SQLAlchemy query structure based on frontend filter values.
    """
    # Start with a base query (and load items relationship eagerly if available)
    query = Contract.query
    
    # 1. Search Filter (Contract ID match)
    if filters.get('search'):
        query = query.filter(Contract.contract_id.ilike(f"%{filters['search']}%"))
        
    # 2. Brand Filter (Assuming contract.items relationship with item.brand column)
    if filters.get('brand'):
        query = query.join(Contract.items).filter(Item.brand.ilike(f"%{filters['brand']}%")).distinct()
        
    # 3. Date Range From
    if filters.get('date_from'):
        try:
            date_from_obj = datetime.strptime(filters['date_from'], '%Y-%m-%d')
            query = query.filter(Contract.contract_date >= date_from_obj)
        except ValueError:
            pass
            
    # 4. Date Range To
    if filters.get('date_to'):
        try:
            date_to_obj = datetime.strptime(filters['date_to'], '%Y-%m-%d')
            query = query.filter(Contract.contract_date <= date_to_obj)
        except ValueError:
            pass

    # 5. Status Filter
    if filters.get('status'):
        query = query.filter(Contract.status == filters['status'])
        
    # 6. Buying Mode Filter
    if filters.get('buying_mode'):
        query = query.filter(Contract.buying_mode == filters['buying_mode'])
        
    # 7. Value Range (Min & Max Total)
    if filters.get('min_total'):
        query = query.filter(Contract.total >= float(filters['min_total']))
    if filters.get('max_total'):
        query = query.filter(Contract.total <= float(filters['max_total']))
        
    # 8. Ministry Filter
    if filters.get('ministry'):
        query = query.filter(Contract.ministry == filters['ministry'])
        
    return query


@user.route('/contracts', methods=['GET'])
def user_contracts():
    # Extract all parameters to re-inject back into template forms and paginations
    filters_applied = {
        'search': request.args.get('search', '').strip(),
        'brand': request.args.get('brand', '').strip(),
        'date_from': request.args.get('date_from', '').strip(),
        'date_to': request.args.get('date_to', '').strip(),
        'status': request.args.get('status', '').strip(),
        'buying_mode': request.args.get('buying_mode', '').strip(),
        'min_total': request.args.get('min_total', '').strip(),
        'max_total': request.args.get('max_total', '').strip(),
        'ministry': request.args.get('ministry', '').strip()
    }

    # Generate query based on applied filters
    query = build_filtered_contracts_query(filters_applied)
    
    # Simple Pagination configuration
    page = request.args.get('page', 1, type=int)
    per_page = 15
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    contracts = pagination.items

    return render_template(
        'user_contract_info.html', 
        contracts=contracts, 
        pagination=pagination, 
        filters_applied=filters_applied
    )


@user.route('/contracts/export/excel', methods=['GET'])
def export_contracts_excel():
    # Collect same active query parameters
    filters_applied = {
        'search': request.args.get('search', '').strip(),
        'brand': request.args.get('brand', '').strip(),
        'date_from': request.args.get('date_from', '').strip(),
        'date_to': request.args.get('date_to', '').strip(),
        'status': request.args.get('status', '').strip(),
        'buying_mode': request.args.get('buying_mode', '').strip(),
        'min_total': request.args.get('min_total', '').strip(),
        'max_total': request.args.get('max_total', '').strip(),
        'ministry': request.args.get('ministry', '').strip()
    }

    # Pull un-paginated matching records
    query = build_filtered_contracts_query(filters_applied)
    matching_contracts = query.all()

    # Formulate tabular data structured for Excel cells
    data_list = []
    for c in matching_contracts:
        # Extract unique list of brands from related items
        brands = ", ".join(list(set([item.brand for item in c.items if item.brand]))) if c.items else "-"
        
        data_list.append({
            "Database ID": c.id,
            "Contract ID": c.contract_id,
            "Status": c.status,
            "Brand Summary": brands,
            "Total Value": c.total,
            "Organization Type": c.organization_type,
            "Organization Name": c.organization_name,
            "Execution Date": c.contract_date.strftime('%Y-%m-%d') if c.contract_date else "-",
            "Buying Mode": c.buying_mode,
            "Ministry": getattr(c, 'ministry', '-')
        })

    # Build spreadsheet using Pandas safely in-memory
    df = pd.DataFrame(data_list)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Filtered Contracts')
    
    output.seek(0)
    
    filename = f"contracts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=filename
    )


# ==========================================
# IMPORT CORE PYTHON MODULES AT THE VERY TOP
# ==========================================
import io  # <-- THIS IS WHAT IS MISSING!
import openpyxl
from datetime import datetime

# ... Your existing Flask imports (Blueprint, request, render_template, etc.) ...
from flask import Blueprint, request, render_template, redirect, url_for, flash, send_file


# Place this directly in your admin contract blueprint controller file!
@admin_contract_bp.route("/export/excel", methods=["GET"])
@login_required
@admin_required # This is why it might trip a 403/404 if your session roles mismatch!
def export_contracts_excel():
    # 1. Grab all parameters sent via request.args using your original parser
    filters = parse_dynamic_filters(request.args)
    
    # 2. Query data using your original application filters
    query = Contract.query
    query = apply_contract_filters(query, filters)
    query = query.order_by(Contract.contract_date.desc())
    contracts = query.all()

    if not contracts:
        flash("No matching contracts found to export.", "warning")
        return redirect(url_for("admin_contract.manage_contracts"))

    # 3. Initialize workbook using openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Filtered Export"

    # Headers matching the column requirements
    headers = [
        "ID", "Contract ID", "Status", "Brand Summary", 
        "Total Value", "Organization Type", "Ministry"
    ]
    ws.append(headers)

    # 4. Populate rows
    for c in contracts:
        # Replicate your template's unique brand aggregation logic
        brand_list = []
        if c.items and isinstance(c.items, list):
            for item in c.items:
                b = item.get("brand")
                if b and b not in brand_list:
                    brand_list.append(b)
        brand_summary = ", ".join(brand_list) if brand_list else "-"

        ws.append([
            c.id,
            c.contract_id,
            c.status or "-",
            brand_summary,
            c.total or 0.0,
            c.organization_type or "-",
            c.ministry or "-"
        ])

    # 5. Pack and return stream
    excel_buffer = io.BytesIO()
    wb.save(excel_buffer)
    excel_buffer.seek(0)

    filename = f"contracts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return send_file(
        excel_buffer,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=filename
    )
# from flask import (
#     Blueprint,
#     request,
#     render_template,
#     redirect,
#     url_for,
#     flash
# )

# from flask_login import (
#     login_required
# )

# from datetime import datetime

# import pandas as pd

# from ..forms.contract_form import ContractForm

# from ..repositories import (
#     contract_repository
# )

# from .admin_user_controller import admin_required


# admin_contract_bp = Blueprint(
#     "admin_contract",
#     __name__,
#     url_prefix="/admin/contracts"
# )


# # =====================================================
# # CONTRACT MANAGEMENT
# # =====================================================

# @admin_contract_bp.route("/", methods=["GET", "POST"])
# @login_required
# @admin_required
# def manage_contracts():

#     form = ContractForm()

#     page = request.args.get(
#         "page",
#         1,
#         type=int
#     )

#     contract_date = request.args.get(
#         "contract_date"
#     )

#     if contract_date:

#         try:

#             contract_date = datetime.strptime(
#                 contract_date,
#                 "%Y-%m-%d"
#             ).date()

#         except ValueError:

#             contract_date = None

#     filters = {
#         "status": request.args.get("status"),
#         "organization_type": request.args.get("organization_type"),
#         "ministry": request.args.get("ministry"),
#         "department": request.args.get("department"),
#         "organization_name": request.args.get("organization_name"),
#         "office_zone": request.args.get("office_zone"),
#         "location": request.args.get("location"),
#         "buyer_designation": request.args.get("buyer_designation"),
#         "buying_mode": request.args.get("buying_mode"),
#         "bid_number": request.args.get("bid_number"),
#         "contract_date": contract_date,
#         "total": request.args.get(
#             "total",
#             type=float
#         ),
#     }

#     filters = {
#         k: v
#         for k, v in filters.items()
#         if v not in [None, ""]
#     }

#     contracts_paginated = (
#         contract_repository.get_contracts_filtered_paginated(
#             filters,
#             page=page,
#             per_page=50
#         )
#     )

#     contracts = contracts_paginated.items

#     if form.validate_on_submit():

#         data = form.data.copy()

#         data.pop("csrf_token", None)

#         items = [
#             {
#                 "service": data.get("service"),
#                 "category_name": data.get("category_name"),
#                 "product": data.get("product"),
#                 "brand": data.get("brand"),
#                 "model": data.get("model"),
#                 "hsn_code": data.get("hsn_code"),
#                 "ordered_quantity": data.get("ordered_quantity"),
#                 "price": data.get("price"),
#             }
#         ]

#         data["items"] = items

#         if contract_repository.add_contract(data):

#             flash(
#                 "Contract added successfully.",
#                 "success"
#             )

#         else:

#             flash(
#                 "Failed to add contract.",
#                 "danger"
#             )

#         return redirect(
#             url_for(
#                 "admin_contract.manage_contracts"
#             )
#         )

#     return render_template(
#         "admin_contracts.html",
#         form=form,
#         contracts=contracts,
#         pagination=contracts_paginated,
#         filters=filters,
#     )


# =====================================================
# BULK DELETE
# =====================================================

@admin_contract_bp.route(
    "/delete",
    methods=["POST"]
)
@login_required
@admin_required
def bulk_delete_contracts():

    contract_ids = request.form.getlist(
        "contract_ids"
    )

    contract_ids = (
        list(map(int, contract_ids))
        if contract_ids
        else []
    )

    deleted_count = (
        contract_repository.bulk_delete(
            contract_ids
        )
    )

    flash(
        f"Deleted {deleted_count} contracts.",
        "success"
    )

    return redirect(
        url_for(
            "admin_contract.manage_contracts"
        )
    )


# =====================================================
# UNIQUE ITEMS HELPER
# =====================================================

def get_unique_items(items):

    seen = set()

    unique_items = []

    for item in items:

        raw_service = item.get("service")

        raw_product = item.get("product")

        def clean_key(value):

            if isinstance(value, str):

                return value.strip().lower()

            elif value is None or (
                isinstance(value, float)
                and pd.isna(value)
            ):

                return ""

            else:

                return str(value).strip().lower()

        service_key = clean_key(raw_service)

        product_key = clean_key(raw_product)

        unique_key = (
            service_key
            or
            product_key
        )

        if unique_key and unique_key not in seen:

            seen.add(unique_key)

            unique_items.append(item)

    return unique_items


# =====================================================
# CONTRACT EXCEL UPLOAD
# =====================================================

@admin_contract_bp.route(
    "/upload_excel",
    methods=["GET", "POST"]
)
@login_required
@admin_required
def upload_contracts_excel():

    form = ContractForm()

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
                "Upload a valid Excel file (.xls or .xlsx)",
                "danger"
            )

            return redirect(request.url)

        file.stream.seek(0)

        try:

            df = pd.read_excel(
                file,
                engine="openpyxl"
            )

        except Exception as e:

            flash(
                f"Failed to read Excel file: {str(e)}",
                "danger"
            )

            return redirect(request.url)

        if df.empty:

            flash(
                "Uploaded Excel file is empty.",
                "danger"
            )

            return redirect(request.url)

        df.columns = [
            c.strip().lower().replace(" ", "_")
            for c in df.columns
        ]

        required_columns = {
            "contract_id",
            "status",
            "organization_type",
            "ministry",
            "department",
            "organization_name",
            "office_zone",
            "location",
            "buyer_designation",
            "buying_mode",
            "bid_number",
            "contract_date",
            "total",
            "service",
            "category_name",
            "product",
            "brand",
            "model",
            "hsn_code",
            "ordered_quantity",
            "price"
        }

        missing = (
            required_columns
            - set(df.columns)
        )

        if missing:

            flash(
                f"Missing required columns: {', '.join(missing)}",
                "danger"
            )

            return redirect(request.url)

        contract_map = {}

        contract_fields = [
            "contract_id",
            "status",
            "organization_type",
            "ministry",
            "department",
            "organization_name",
            "office_zone",
            "location",
            "buyer_designation",
            "buying_mode",
            "bid_number",
            "contract_date",
            "total"
        ]

        item_fields = [
            "service",
            "category_name",
            "product",
            "brand",
            "model",
            "hsn_code",
            "ordered_quantity",
            "price"
        ]

        for _, row in df.iterrows():

            cid = row["contract_id"]

            if cid not in contract_map:

                contract_map[cid] = {
                    f: row.get(f)
                    for f in contract_fields
                }

                contract_map[cid]["items"] = []

            item = {
                f: row.get(f)
                for f in item_fields
            }

            contract_map[cid]["items"].append(
                item
            )

        contracts = []

        for cid, contract_data in contract_map.items():

            contract_data["items"] = (
                get_unique_items(
                    contract_data["items"]
                )
            )

            contracts.append(contract_data)

        count = 0

        failed = 0

        for contract_data in contracts:

            if contract_repository.add_contract(
                contract_data
            ):

                count += 1

            else:

                failed += 1

        flash(
            f"Import completed. Inserted/updated: {count}, Failed: {failed}",
            "success" if count else "warning"
        )

    return render_template(
        "admin_contract_upload.html",
        form=form
    )