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

# user_bp = Blueprint("user", __name__, url_prefix="/user")
user_bp = Blueprint("user", __name__, url_prefix="/user")

# def safe_to_str(value):
#     if isinstance(value, str):
#         return value.strip().lower()
#     elif value is None:
#         return ""
#     elif isinstance(value, float):
#         import math
#         if math.isnan(value):
#             return ""
#         return str(int(value)) if value.is_integer() else str(value)
#     else:
#         return str(value).strip().lower()

# def parse_list_csv(csv_string):
#     return set([safe_to_str(s) for s in (csv_string or "").split(",") if safe_to_str(s)])

# def parse_dynamic_filters(args):
#     # Maps param names to contract column attributes
#     filter_fields = [
#         "status", "organization_type", "ministry", "department",
#         "organization_name", "office_zone", "location", "buyer_designation",
#         "buying_mode", "bid_number", "contract_date"
#     ]
#     filters = {}
#     for field in filter_fields:
#         value = args.get(field, None, type=str)
#         if value:
#             filters[field] = value.strip()
#     min_total = args.get("min_total", None, type=float)
#     max_total = args.get("max_total", None, type=float)
#     if min_total is not None:
#         filters["min_total"] = min_total
#     if max_total is not None:
#         filters["max_total"] = max_total
#     return filters

# def apply_contract_filters(query, filters):
#     for field, value in filters.items():
#         if field == "contract_date":
#             try:
#                 date_val = datetime.strptime(value, "%Y-%m-%d").date()
#                 query = query.filter(Contract.contract_date == date_val)
#             except Exception:
#                 continue
#         elif field == "min_total":
#             query = query.filter(Contract.total >= value)
#         elif field == "max_total":
#             query = query.filter(Contract.total <= value)
#         else:
#             column = getattr(Contract, field, None)
#             if column is not None:
#                 query = query.filter(column.ilike(f"%{value}%"))
#     return query

# def contract_brand_match(contract, brand_set):
#     contract_items = contract.items or []
#     if not brand_set:
#         return True
#     for item in contract_items:
#         brand = safe_to_str(item.get('brand', ''))
#         if brand and brand in brand_set:
#             return True
#     return False

# class Pagination:
#     def __init__(self, page, per_page, total):
#         self.page = page
#         self.per_page = per_page
#         self.total = total
#         self.pages = (total + per_page - 1) // per_page
#         self.has_prev = page > 1
#         self.has_next = (page * per_page) < total
#         self.prev_num = page - 1
#         self.next_num = page + 1


# @user_bp.route("/contracts")
# @login_required
# def user_contracts():
#     if not current_user.is_verified or current_user.is_blocked:
#         abort(403)

#     # Subscription validation
#     if not current_user.subscription_date or current_user.subscription_date < datetime.utcnow().date():
#         abort(403)

#     brand_set = {
#     b.strip().lower()
#     for b in parse_list_csv(current_user.brand_names)
# }
#     assigned_start = current_user.assigned_date_range_start
#     assigned_end = current_user.assigned_date_range_end

#     page = request.args.get('page', 1, type=int)
#     per_page = 10

#     filters = parse_dynamic_filters(request.args)

#     # ✅ FIX 1: if no brand assigned → show no contracts
#     if not brand_set:
#         # flash("No brand assigned to your account.", "warning")
#         return render_template(
#             "user_contract_info.html",
#             contracts=[],
#             pagination=Pagination(page, per_page, 0),
#             user_brands=[],
#             assigned_start_date=assigned_start,
#             assigned_end_date=assigned_end,
#             filters_applied=filters
#         )

#     base_query = Contract.query

#     # Date range filter
#     contract_date_param = request.args.get("contract_date", None, type=str)
#     contract_date = None
#     if contract_date_param:
#         try:
#             date_obj = datetime.strptime(contract_date_param, "%Y-%m-%d").date()
#             if assigned_start and assigned_end and assigned_start <= date_obj <= assigned_end:
#                 contract_date = date_obj
#                 filters["contract_date"] = contract_date_param
#         except Exception:
#             contract_date = None

#     if not contract_date:
#         if assigned_start and assigned_end:
#             base_query = base_query.filter(
#                 and_(
#                     Contract.contract_date >= assigned_start,
#                     Contract.contract_date <= assigned_end
#                 )
#             )

#     # Apply other dynamic filters
#     base_query = apply_contract_filters(base_query, filters)

#     # Order by contract_date DESC
#     base_query = base_query.order_by(Contract.contract_date.desc())

#     # Fetch contracts
#     contracts = base_query.all()

#     # Brand filtering
#     filtered_contracts = [c for c in contracts if contract_brand_match(c, brand_set)]

#     total = len(filtered_contracts)
#     start = (page - 1) * per_page
#     end = start + per_page
#     paginated_contracts = filtered_contracts[start:end]

#     pagination = Pagination(page, per_page, total)

#     return render_template(
#         "user_contract_info.html",
#         contracts=paginated_contracts,
#         pagination=pagination,
#         user_brands=list(brand_set),
#         assigned_start_date=assigned_start,
#         assigned_end_date=assigned_end,
#         filters_applied=filters
#     )


from datetime import datetime
from flask import request, abort, render_template
from flask_login import login_required, current_user
from sqlalchemy import and_
from app.models.contract import Contract


def safe_to_str(value):
    if isinstance(value, str):
        return value.strip().lower()
    elif value is None:
        return ""
    elif isinstance(value, float):
        import math
        if math.isnan(value):
            return ""
        return str(int(value)) if value.is_integer() else str(value)
    else:
        return str(value).strip().lower()


def parse_list_csv(csv_string):
    return set(
        [safe_to_str(s) for s in (csv_string or "").split(",") if safe_to_str(s)]
    )


# def parse_dynamic_filters(args):

#     filter_fields = [
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
#         if value:
#             filters[field] = value.strip()

#     min_total = args.get("min_total", None, type=float)
#     max_total = args.get("max_total", None, type=float)

#     if min_total is not None:
#         filters["min_total"] = min_total

#     if max_total is not None:
#         filters["max_total"] = max_total

#     return filters


# def apply_contract_filters(query, filters):

#     for field, value in filters.items():

#         if field == "contract_date":
#             try:
#                 date_val = datetime.strptime(value, "%Y-%m-%d").date()
#                 query = query.filter(Contract.contract_date == date_val)
#             except Exception:
#                 continue

#         elif field == "min_total":
#             query = query.filter(Contract.total >= value)

#         elif field == "max_total":
#             query = query.filter(Contract.total <= value)

#         else:
#             column = getattr(Contract, field, None)

#             if column is not None:
#                 query = query.filter(column.ilike(f"%{value}%"))

#     return query

from datetime import datetime


def parse_dynamic_filters(args):

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
        "contract_date",
    ]

    filters = {}

    for field in filter_fields:

        value = args.get(field, None, type=str)

        if value and value.strip():
            filters[field] = value.strip()

    min_total = args.get("min_total", None, type=float)
    max_total = args.get("max_total", None, type=float)

    if min_total is not None:
        filters["min_total"] = min_total

    if max_total is not None:
        filters["max_total"] = max_total

    return filters



# def apply_contract_filters(query, filters):

#     for field, value in filters.items():

#         # -----------------------------
#         # SEARCH -> bid_number
#         # -----------------------------
#         print("SEARCH VALUE =", value)
#         print("COLUMN =", Contract.contract_id)
#         if field == "search":

#             query = query.filter(
#                Contract.contract_id == value.strip()
#             )
#             print("SEARCH FILTER APPLIED")
#             continue

#         # -----------------------------
#         # Exact Contract Date
#         # -----------------------------
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

#         # -----------------------------
#         # Min Total
#         # -----------------------------
#         elif field == "min_total":

#             query = query.filter(
#                 Contract.total >= value
#             )

#         # -----------------------------
#         # Max Total
#         # -----------------------------
#         elif field == "max_total":

#             query = query.filter(
#                 Contract.total <= value
#             )

#         # -----------------------------
#         # Generic Filters
#         # -----------------------------
#         else:

#             column = getattr(Contract, field, None)

#             if column is not None:

#                 query = query.filter(
#                     column.ilike(f"%{value}%")
#                 )

#     return query



def apply_contract_filters(query, filters):
    for field, value in filters.items():
        if not value:  # Skip empty strings or None values early
            continue

        # -----------------------------
        # SEARCH -> contract_id
        # -----------------------------
        if field == "search":
            query = query.filter(
                Contract.contract_id == str(value).strip()
            )
            continue

        # -----------------------------
        # Date Range: From
        # -----------------------------
        elif field == "date_from":
            try:
                date_val = datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
                query = query.filter(Contract.contract_date >= date_val)
            except Exception as e:
                print(f"Error parsing date_from: {e}")
            continue

        # -----------------------------
        # Date Range: To
        # -----------------------------
        elif field == "date_to":
            try:
                date_val = datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
                query = query.filter(Contract.contract_date <= date_val)
            except Exception as e:
                print(f"Error parsing date_to: {e}")
            continue

        # -----------------------------
        # Exact Contract Date (Legacy Fallback)
        # -----------------------------
        elif field == "contract_date":
            try:
                date_val = datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
                query = query.filter(Contract.contract_date == date_val)
            except Exception as e:
                print(f"Error parsing contract_date: {e}")
            continue

        # -----------------------------
        # Min Total
        # -----------------------------
        elif field == "min_total":
            try:
                query = query.filter(Contract.total >= float(value))
            except ValueError:
                pass
            continue

        # -----------------------------
        # Max Total
        # -----------------------------
        elif field == "max_total":
            try:
                query = query.filter(Contract.total <= float(value))
            except ValueError:
                pass
            continue

        # -----------------------------
        # Generic Filters (status, buying_mode, ministry)
        # -----------------------------
        else:
            column = getattr(Contract, field, None)
            if column is not None:
                query = query.filter(
                    column.ilike(f"%{value}%")
                )

    return query

# @user_bp.route("/contracts")
# @login_required
# def user_contracts():

#     if not current_user.is_verified or current_user.is_blocked:
#         abort(403)

#     if (
#         not current_user.subscription_date
#         or current_user.subscription_date < datetime.utcnow().date()
#     ):
#         abort(403)

#     brand_set = {
#     b.strip().lower()
#     for b in parse_list_csv(current_user.brand_names)
#     }

#     assigned_start = current_user.assigned_date_range_start
#     assigned_end = current_user.assigned_date_range_end

#     page = request.args.get("page", 1, type=int)
#     per_page = 10
#     print("USER BRANDS =", brand_set)
#     filters = parse_dynamic_filters(request.args)
#     print("FILTERS =", filters)
   

#     # If user has no brand assigned
#     if not brand_set:

#         return render_template(
#             "user_contract_info.html",
#             contracts=[],
#             pagination=None,
#             user_brands=[],
#             assigned_start_date=assigned_start,
#             assigned_end_date=assigned_end,
#             filters_applied=filters,
#         )

#     # Base query
#     query = Contract.query

#     # Date range restriction
#     contract_date_param = request.args.get("contract_date", None, type=str)

#     contract_date = None

#     if contract_date_param:
#         try:
#             date_obj = datetime.strptime(contract_date_param, "%Y-%m-%d").date()

#             if (
#                 assigned_start
#                 and assigned_end
#                 and assigned_start <= date_obj <= assigned_end
#             ):
#                 contract_date = date_obj
#                 filters["contract_date"] = contract_date_param

#         except Exception:
#             contract_date = None

#     if not contract_date:

#         if assigned_start and assigned_end:

#             query = query.filter(
#                 and_(
#                     Contract.contract_date >= assigned_start,
#                     Contract.contract_date <= assigned_end,
#                 )
#             )

#     # Apply dynamic filters
#     query = apply_contract_filters(query, filters)

#     # Brand filter using indexed column
#     from sqlalchemy import text

#     query = query.filter(
#         text("""
#             EXISTS (
#                 SELECT 1
#                 FROM unnest(contracts.brands) AS b
#                 WHERE lower(b) = ANY(:brands)
#             )
#         """)
#     ).params(
#         brands=[b.lower() for b in brand_set]
#     )

#     # Order
#     query = query.order_by(Contract.contract_date.desc())

#     # Database pagination
#     pagination = query.paginate(
#         page=page,
#         per_page=per_page,
#         error_out=False,
#     )

#     contracts = pagination.items

#     return render_template(
#         "user_contract_info.html",
#         contracts=contracts,
#         pagination=pagination,
#         user_brands=list(brand_set),
#         assigned_start_date=assigned_start,
#         assigned_end_date=assigned_end,
#         filters_applied=filters,
#     )



@user_bp.route("/contracts")
@login_required
def user_contracts():

    if not current_user.is_verified or current_user.is_blocked:
        abort(403)

    if (
        not current_user.subscription_date
        or current_user.subscription_date < datetime.utcnow().date()
    ):
        abort(403)

    brand_set = {
        b.strip().lower()
        for b in parse_list_csv(current_user.brand_names)
    }

    assigned_start = current_user.assigned_date_range_start
    assigned_end = current_user.assigned_date_range_end

    page = request.args.get("page", 1, type=int)
    per_page = 10
    print("USER BRANDS =", brand_set)
    filters = parse_dynamic_filters(request.args)
    print("FILTERS =", filters)

    # If user has no brand assigned
    if not brand_set:
        return render_template(
            "user_contract_info.html",
            contracts=[],
            pagination=None,
            user_brands=[],
            assigned_start_date=assigned_start,
            assigned_end_date=assigned_end,
            filters_applied=filters,
        )

    # Base query
    query = Contract.query

    # ---------------------------------------------------------
    # FIXED: Capture range parameters so they stay in 'filters_applied'
    # ---------------------------------------------------------
    date_from_param = request.args.get("date_from", "", type=str)
    date_to_param = request.args.get("date_to", "", type=str)

    if date_from_param:
        filters["date_from"] = date_from_param
    if date_to_param:
        filters["date_to"] = date_to_param
    # ---------------------------------------------------------

    # Default fallback protection logic for strict user date bounding
    # Only applies if the user didn't specify a custom dynamic date range search
    if not date_from_param and not date_to_param:
        if assigned_start and assigned_end:
            query = query.filter(
                and_(
                    Contract.contract_date >= assigned_start,
                    Contract.contract_date <= assigned_end,
                )
            )

    # Apply dynamic filters (processes your date_from and date_to parameters)
    query = apply_contract_filters(query, filters)

    # Brand filter using indexed column
    from sqlalchemy import text

    query = query.filter(
        text("""
            EXISTS (
                SELECT 1
                FROM unnest(contracts.brands) AS b
                WHERE lower(b) = ANY(:brands)
            )
        """)
    ).params(
        brands=[b.lower() for b in brand_set]
    )

    # Order
    query = query.order_by(Contract.contract_date.desc())

    # Database pagination
    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False,
    )

    contracts = pagination.items

    return render_template(
        "user_contract_info.html",
        contracts=contracts,
        pagination=pagination,
        user_brands=list(brand_set),
        assigned_start_date=assigned_start,
        assigned_end_date=assigned_end,
        filters_applied=filters,
    )

from flask import jsonify

@user_bp.route("/contract/api/<contract_id>")
@login_required
def contract_api(contract_id):
    contract = Contract.query.filter_by(contract_id=contract_id).first()
    print("contract", contract)
    if not contract:
        return jsonify({"error": "Contract not found"}), 404
    
    seller = Seller.query.filter_by(contract_no=contract.contract_id).first()
    print("seller",seller)
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
    
    return jsonify({"contract": contract_data, "seller": seller_data})






from collections import Counter
from flask import request, render_template, abort
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime

def safe_to_str(value):
    if isinstance(value, str):
        return value.strip().lower()
    elif value is None:
        return ""
    elif isinstance(value, float):
        import math
        if math.isnan(value):
            return ""
        return str(int(value)) if value.is_integer() else str(value)
    else:
        return str(value).strip().lower()

def parse_list_csv(csv_string):
    return set([safe_to_str(s) for s in (csv_string or "").split(",") if safe_to_str(s)])

# def parse_seller_filters(args):
#     filter_fields = [
#         "company_name", "category_name", "gstin",
#         "msme_reg_no", "email", "contact_no"
#     ]
#     filters = {}
#     for field in filter_fields:
#         value = args.get(field, None, type=str)
#         if value:
#             filters[field] = value.strip()
#     return filters

# def apply_seller_filters(query, filters):
#     for field, value in filters.items():
#         column = getattr(Seller, field, None)
#         if column is not None:
#             query = query.filter(column.ilike(f"%{value}%"))
#     return query


from datetime import datetime, time
from sqlalchemy import func
from flask import abort, render_template, request

# ==========================================
# 🛠️ HELPER PARSING FUNCTIONS & EXTENSIONS
# ==========================================

def parse_seller_filters(args):
    """
    Extracts explicit field arguments coming from the request query parameters.
    Handles text patterns cleanly and captures multi-select array checkboxes natively.
    """
    filters = {}

    # normal text fields
    text_fields = [
        "company_name",
        "gstin",
        "msme_reg_no",
        "email",
        "contact_no"
    ]

    for field in text_fields:
        value = args.get(field, None, type=str)
        if value:
            filters[field] = value.strip()

    # Match HTML's exact name attribute ("category_name")
    categories = args.getlist("category_name")

    if categories:
        filters["category_name"] = [
            c.strip().lower()
            for c in categories
            if c.strip()
        ]

    return filters


def apply_seller_filters(query, filters):
    """
    Dynamically applies string-based wildcard ILIKE filters 
    against columns present on the Seller database model blueprint.
    """
    for field, value in filters.items():
        column = getattr(Seller, field, None)
        if column is not None:
            query = query.filter(
                column.ilike(f"%{value}%")
            )

    return query


class Pagination:
    """
    A lightweight data utility container mimicking Flask-SQLAlchemy's built-in 
    pagination object structure for seamless frontend rendering.
    """
    def __init__(self, page, per_page, total):
        self.page = page
        self.per_page = per_page
        self.total = total
        self.pages = (total + per_page - 1) // per_page
        self.has_prev = page > 1
        self.has_next = (page * per_page) < total
        self.prev_num = page - 1
        self.next_num = page + 1


# ==========================================
# 🚀 CORE ROUTE ROUTINE IMPLEMENTATION
# ==========================================

@user_bp.route("/sellers")
@login_required
def user_sellers():

    # -----------------------------
    # 🔐 USER ACCESS CHECKS
    # -----------------------------
    if not current_user.is_verified or current_user.is_blocked:
        abort(403)

    if not current_user.subscription_date or current_user.subscription_date < datetime.utcnow().date():
        abort(403)

    # -----------------------------
    # 📌 PAGINATION SETUP
    # -----------------------------
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # -----------------------------
    # 📌 USER ASSIGNED CATEGORIES
    # -----------------------------
    raw_categories = parse_list_csv(current_user.category_names)
    category_set = {cat.lower().strip() for cat in raw_categories if cat}

    # 🔒 HARD RULE: no category → no data
    if not category_set:
        pagination = Pagination(page, per_page, 0)
        return render_template(
            "user_seller_info.html",
            sellers=[],
            unique_sellers=[],
            pagination=pagination,
            user_categories=[],
            filters_applied={}
        )

    # -----------------------------
    # 📌 USER ASSIGNED DATE RANGE
    # -----------------------------
    assigned_start = current_user.assigned_date_range_start
    assigned_end = current_user.assigned_date_range_end

    # 🔒 HARD RULE: no date range → no data
    if not assigned_start or not assigned_end:
        pagination = Pagination(page, per_page, 0)
        return render_template(
            "user_seller_info.html",
            sellers=[],
            unique_sellers=[],
            pagination=pagination,
            user_categories=list(raw_categories),
            filters_applied={}
        )

    # Normalize dates to handle a full-day window smoothly (00:00:00 to 23:59:59)
    start_dt = datetime.combine(assigned_start, time.min)
    end_dt = datetime.combine(assigned_end, time.max)

    # -----------------------------
    # 📌 APPLY FILTERS & CONSTRAINTS
    # -----------------------------
    filters = parse_seller_filters(request.args)
    base_query = Seller.query
    
    # DYNAMIC CATEGORY INTERSECTION
    selected_categories = filters.get("category_name", [])
    if selected_categories:
        allowed_filters = [c for c in selected_categories if c in category_set]
        if allowed_filters:
            base_query = base_query.filter(func.lower(Seller.category_name).in_(allowed_filters))
        else:
            base_query = base_query.filter(False)
    else:
        base_query = base_query.filter(func.lower(Seller.category_name).in_(list(category_set)))

    # Apply standard remaining text searches
    text_filters = {k: v for k, v in filters.items() if k != "category_name"}
    base_query = apply_seller_filters(base_query, text_filters)

    # DATE RANGE FILTER
    base_query = base_query.filter(
        Seller.generated_date >= start_dt,
        Seller.generated_date <= end_dt
    )

    # -----------------------------
    # 🔁 GLOBAL DISTINCT GROUPING SUBSYSTEM
    # -----------------------------
    # Create an explicit isolated tracking subquery matching our base filter options.
    # Grouping by Company Name globally allows calculations to remain accurate across pages.
    group_subquery = (
        db.session.query(
            Seller.company_name,
            func.count(Seller.id).label('global_count'),
            func.max(Seller.id).label('representative_id')
        )
        .filter(base_query.whereclause)
        .group_by(Seller.company_name)
        .subquery()
    )

    # Calculate global distinct match counts using our isolated subset layout
    total_distinct_companies = db.session.query(func.count(group_subquery.c.company_name)).scalar() or 0

    # Execute structured paginated slice operations over grouped records
    paginated_groups = (
        db.session.query(
            group_subquery.c.company_name,
            group_subquery.c.global_count,
            group_subquery.c.representative_id
        )
        .order_by(group_subquery.c.representative_id.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    # Resolve primary active model entities matching our sliced representation targets
    target_ids = [g.representative_id for g in paginated_groups if g.representative_id]
    sellers_map = {s.id: s for s in Seller.query.filter(Seller.id.in_(target_ids)).all()} if target_ids else {}

    # Extract all related transactions context for our mapped viewport entries
    unique_sellers = []
    for group in paginated_groups:
        seller_obj = sellers_map.get(group.representative_id)
        if not seller_obj:
            continue

        # Fetch contract identifiers related to this distinct company name globally
        associated_contracts = [
            row[0] for row in db.session.query(Seller.contract_no)
            .filter(base_query.whereclause)
            .filter(Seller.company_name == group.company_name)
            .filter(Seller.contract_no.isnot(None))
            .all()
        ]

        unique_sellers.append({
            'company_name': group.company_name.strip() if group.company_name else '',
            'count': group.global_count,
            'seller': seller_obj,
            'contract_nos': associated_contracts
        })

    pagination = Pagination(page, per_page, total_distinct_companies)

    return render_template(
        "user_seller_info.html",
        sellers=[],  # Legacy variable bypassed cleanly
        unique_sellers=unique_sellers,
        pagination=pagination,
        user_categories=list(raw_categories),
        filters_applied=filters
    )

# from sqlalchemy import func

# def parse_seller_filters(args):

#     filters = {}

#     # normal text fields
#     text_fields = [
#         "company_name",
#         "gstin",
#         "msme_reg_no",
#         "email",
#         "contact_no"
#     ]

#     for field in text_fields:
#         value = args.get(field, None, type=str)

#         if value:
#             filters[field] = value.strip()

#     # ✅ MULTI CATEGORY SUPPORT
#     categories = args.getlist("category_name[]")

#     if categories:
#         filters["category_name"] = [
#             c.strip().lower()
#             for c in categories
#             if c.strip()
#         ]

#     return filters


# def apply_seller_filters(query, filters):

#     for field, value in filters.items():

#         # ✅ CATEGORY FILTER
#         if field == "category_name":

#             query = query.filter(
#                 func.lower(Seller.category_name).in_(value)
#             )

#             continue

#         # normal fields
#         column = getattr(Seller, field, None)

#         if column is not None:
#             query = query.filter(
#                 column.ilike(f"%{value}%")
#             )

#     return query



# class Pagination:
#     def __init__(self, page, per_page, total):
#         self.page = page
#         self.per_page = per_page
#         self.total = total
#         self.pages = (total + per_page - 1) // per_page
#         self.has_prev = page > 1
#         self.has_next = (page * per_page) < total
#         self.prev_num = page - 1
#         self.next_num = page + 1

# from datetime import datetime, time
# from collections import Counter
# from sqlalchemy import func

# @user_bp.route("/sellers")
# @login_required
# def user_sellers():

#     # -----------------------------
#     # 🔐 USER ACCESS CHECKS
#     # -----------------------------
#     if not current_user.is_verified or current_user.is_blocked:
#         abort(403)

#     if not current_user.subscription_date or current_user.subscription_date < datetime.utcnow().date():
#         abort(403)

#     # -----------------------------
#     # 📌 PAGINATION
#     # -----------------------------
#     page = request.args.get('page', 1, type=int)
#     per_page = 10

#     # -----------------------------
#     # 📌 USER ASSIGNED CATEGORIES
#     # -----------------------------
#     category_set = parse_list_csv(current_user.category_names)

#     # 🔒 HARD RULE: no category → no data
#     if not category_set:
#         pagination = Pagination(page, per_page, 0)
#         return render_template(
#             "user_seller_info.html",
#             sellers=[],
#             unique_sellers=[],
#             pagination=pagination,
#             user_categories=[],
#             filters_applied={}
#         )

#     # -----------------------------
#     # 📌 USER ASSIGNED DATE RANGE (REAL FIELDS)
#     # -----------------------------
#     assigned_start = current_user.assigned_date_range_start
#     assigned_end = current_user.assigned_date_range_end

#     # 🔒 HARD RULE: no date range → no data
#     if not assigned_start or not assigned_end:
#         pagination = Pagination(page, per_page, 0)
#         return render_template(
#             "user_seller_info.html",
#             sellers=[],
#             unique_sellers=[],
#             pagination=pagination,
#             user_categories=list(category_set),
#             filters_applied={}
#         )

#     # Normalize to full-day window
#     start_dt = datetime.combine(assigned_start, time.min)
#     end_dt = datetime.combine(assigned_end, time.max)

#     # -----------------------------
#     # 📌 APPLY FILTERS
#     # -----------------------------
#     filters = parse_seller_filters(request.args)
#     base_query = Seller.query
#     base_query = apply_seller_filters(base_query, filters)

#     # -----------------------------
#     # ✅ CATEGORY FILTER
#     # -----------------------------
#     base_query = base_query.filter(
#         func.lower(Seller.category_name).in_(category_set)
#     )

#     # -----------------------------
#     # ✅ DATE RANGE FILTER (Seller table)
#     # -----------------------------
#     base_query = base_query.filter(
#         Seller.generated_date >= start_dt,
#         Seller.generated_date <= end_dt
#     )

#     # -----------------------------
#     # 📊 COUNT + FETCH DATA
#     # -----------------------------
#     total = base_query.count()

#     sellers = (
#         base_query
#         .order_by(Seller.id.desc())
#         .offset((page - 1) * per_page)
#         .limit(per_page)
#         .all()
#     )

#     # -----------------------------
#     # 🔁 UNIQUE COMPANY GROUPING
#     # -----------------------------
#     company_list = [
#         s.company_name.strip() if s.company_name else ''
#         for s in sellers
#     ]
#     company_counts = Counter(company_list)

#     unique_sellers = []

#     for name, count in company_counts.items():
#         seller_obj = next(
#             (s for s in sellers if (s.company_name or '').strip() == name),
#             None
#         )

#         if seller_obj:
#             contract_nos = [
#                 s.contract_no
#                 for s in sellers
#                 if (s.company_name or '').strip() == name and s.contract_no
#             ]

#             unique_sellers.append({
#                 'company_name': name,
#                 'count': count,
#                 'seller': seller_obj,
#                 'contract_nos': contract_nos
#             })

#     pagination = Pagination(page, per_page, total)

#     return render_template(
#         "user_seller_info.html",
#         sellers=sellers,
#         unique_sellers=unique_sellers,
#         pagination=pagination,
#         user_categories=list(category_set),
#         filters_applied=filters
#     )











# from flask_wtf.csrf import csrf_exempt
import math

def sanitize_json(obj):
    """
    Recursively replace NaN with None (null in JSON)
    """
    if isinstance(obj, dict):
        return {k: sanitize_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_json(v) for v in obj]
    elif isinstance(obj, float) and math.isnan(obj):
        return None
    else:
        return obj

from ..extensions import csrf
@user_bp.route("/api/contracts/by-contract-nos", methods=["POST"])
@login_required
@csrf.exempt
def get_contracts_by_contract_nos():

    #  SAME RESTRICTIONS AS /contracts
    if not current_user.is_verified or current_user.is_blocked:
        abort(403)

    if not current_user.subscription_date or current_user.subscription_date < datetime.utcnow().date():
        abort(403)

    data = request.get_json()
    # print(data)
    contract_nos = data.get("contract_nos", [])
    # print(contract_nos)
    if not contract_nos or not isinstance(contract_nos, list):
        abort(400, "Invalid contract numbers")

    brand_set = {
    b.strip().lower()
    for b in parse_list_csv(current_user.brand_names)
}
    assigned_start = current_user.assigned_date_range_start
    assigned_end = current_user.assigned_date_range_end

    # ✅ Fetch contracts
    query = Contract.query.filter(Contract.contract_id.in_(contract_nos))
    # print(query)
    # Date range restriction
    if assigned_start and assigned_end:
        query = query.filter(
            Contract.contract_date.between(assigned_start, assigned_end)
        )

    contracts = query.order_by(Contract.contract_date.desc()).all()

    # Brand restriction (same logic you already use)
    def contract_brand_match(contract):
        for item in contract.items or []:
            if isinstance(item, dict):
                brand = safe_to_str(item.get("brand"))
                if brand and brand in brand_set:
                    return True
        return True

    filtered_contracts = [c for c in contracts if contract_brand_match(c)]

    # 🔄 Serialize
    return jsonify([
        {
            "contract_id": c.contract_id,
            "status": c.status,
            "organization_type": c.organization_type,
            "ministry": c.ministry,
            "department": c.department,
            "organization_name": c.organization_name,
            "office_zone": c.office_zone,
            "location": c.location,
            "buyer_designation": c.buyer_designation,
            "buying_mode": c.buying_mode,
            "bid_number": c.bid_number,
            "contract_date": c.contract_date.strftime("%Y-%m-%d") if c.contract_date else None,
            "total": c.total,
            "items": sanitize_json(c.items)
        }
        for c in filtered_contracts
    ])















import json
from datetime import datetime

from flask import (
    Blueprint,
    jsonify,
    request
)

from flask_login import (
    login_required,
    current_user
)

from ..extensions import (
    db,
    csrf
)

from ..models.contract import Contract
from ..models.seller import Seller


# ---------------------------------------------------------
# SINGLE CONTRACT API
# ---------------------------------------------------------
@user_bp.route(
    "/api/contracts/<contract_id>",
    methods=["GET"]
)
@login_required
def get_single_contract(contract_id):

    print("\n====================================", flush=True)
    print(f"[API HIT] SINGLE CONTRACT => {contract_id}", flush=True)
    print("====================================\n", flush=True)

    # ---------------------------------------------------------
    # USER VALIDATION
    # ---------------------------------------------------------
    print("USER VERIFIED:", current_user.is_verified)
    print("USER BLOCKED:", current_user.is_blocked)
    print("SUB DATE:", current_user.subscription_date)
    print("TODAY:", datetime.utcnow().date())

    if not current_user.is_verified or current_user.is_blocked:
        return jsonify({
            "error": "Access denied."
        }), 403

    if (
        not current_user.subscription_date or
        current_user.subscription_date < datetime.utcnow().date()
    ):
        return jsonify({
            "error": "Subscription expired."
        }), 403

    # ---------------------------------------------------------
    # USER BRAND ACCESS
    # ---------------------------------------------------------
    brand_set = set()

    if getattr(current_user, "brand_names", None):

        brand_set = {
            b.strip().lower()
            for b in current_user.brand_names.split(",")
            if b.strip()
        }

    print("USER BRANDS:", brand_set)

    assigned_start = current_user.assigned_date_range_start
    assigned_end = current_user.assigned_date_range_end

    # ---------------------------------------------------------
    # DATABASE QUERY
    # ---------------------------------------------------------
    query = db.session.query(
        Contract,
        Seller
    ).outerjoin(
        Seller,
        Contract.contract_id == Seller.contract_no
    ).filter(
        Contract.contract_id == contract_id
    )

    # ---------------------------------------------------------
    # DATE FILTER
    # ---------------------------------------------------------
    if assigned_start and assigned_end:

        query = query.filter(
            Contract.contract_date.between(
                assigned_start,
                assigned_end
            )
        )

    result = query.first()

    if not result:

        return jsonify({
            "error": "Contract not found."
        }), 404

    contract, seller = result

    # ---------------------------------------------------------
    # ITEMS PARSE
    # ---------------------------------------------------------
    items_list = contract.items

    if isinstance(items_list, str):

        try:
            items_list = json.loads(items_list)

        except Exception as e:

            print("JSON PARSE ERROR:", e)

            items_list = []

    if not isinstance(items_list, list):
        items_list = []

    # ---------------------------------------------------------
    # BRAND VALIDATION
    # ---------------------------------------------------------
# ---------------------------------------------------------
# BRAND VALIDATION
# AT LEAST ONE BRAND SHOULD MATCH
# ---------------------------------------------------------
    if brand_set:

        matched_items = []

        for item in items_list:

           

            if not isinstance(item, dict):
                continue

            item_brand = str(
                item.get("brand", "")
            ).strip().lower()

           

            # ---------------------------------------------------------
            # IF USER HAS ACCESS TO THIS BRAND
            # ---------------------------------------------------------
            if item_brand in brand_set:

                matched_items.append(item)

        # ---------------------------------------------------------
        # NO MATCH FOUND
        # ---------------------------------------------------------
        if len(matched_items) == 0:

            

            return jsonify({
                "error": "Unauthorized brand access."
            }), 403

    # ---------------------------------------------------------
    # ONLY SEND MATCHED ITEMS
    # ---------------------------------------------------------
    items_list = matched_items

    # ---------------------------------------------------------
    # RESPONSE PAYLOAD
    # ---------------------------------------------------------
    payload = {

        "id": contract.id,

        "contract_id": contract.contract_id,

        "status": contract.status or "N/A",

        "organization_type": (
            contract.organization_type or "N/A"
        ),

        "ministry": (
            contract.ministry or "N/A"
        ),

        "department": (
            contract.department or "N/A"
        ),

        "organization_name": (
            contract.organization_name or "N/A"
        ),

        "office_zone": (
            contract.office_zone or "N/A"
        ),

        "location": (
            contract.location or "N/A"
        ),

        "buyer_designation": (
            contract.buyer_designation or "N/A"
        ),

        "buying_mode": (
            contract.buying_mode or "N/A"
        ),

        "bid_number": (
            contract.bid_number or "N/A"
        ),

        "contract_date": (
            contract.contract_date.strftime("%Y-%m-%d")
            if contract.contract_date
            else "N/A"
        ),

        "total": contract.total or 0.0,

        "items": items_list,

        # ---------------------------------------------------------
        # SELLER DETAILS
        # ---------------------------------------------------------
        "seller_id": (
            seller.seller_id
            if seller else "N/A"
        ),

        "seller_company_name": (
            seller.company_name
            if seller else "N/A"
        ),

        "seller_contact_no": (
            seller.contact_no
            if seller else "N/A"
        ),

        "seller_email": (
            seller.email
            if seller else "N/A"
        ),

        "seller_address": (
            seller.address
            if seller else "N/A"
        ),

        "seller_category_name": (
            seller.category_name
            if seller else "N/A"
        ),

        "seller_msme_reg_no": (
            seller.msme_reg_no
            if seller else "N/A"
        ),

        "seller_gstin": (
            seller.gstin
            if seller else "N/A"
        ),

        "service_start_date": (
            seller.service_start_date.strftime("%Y-%m-%d")
            if (
                seller and
                seller.service_start_date
            )
            else "N/A"
        ),

        "service_end_date": (
            seller.service_end_date.strftime("%Y-%m-%d")
            if (
                seller and
                seller.service_end_date
            )
            else "N/A"
        )
    }

   

    return jsonify(payload), 200

@login_required
@user_bp.route("/dashboard")
def user_dashboard():
    return render_template("user_dashboard.html", user=current_user)


from math import ceil
import json
from ..models.user import UserHistory

@user_bp.route("/profile")
@login_required
def profile():

    user = current_user

    # ---------------- PAGINATION CONFIG ----------------
    page = request.args.get("page", 1, type=int)
    per_page = 5

    query = UserHistory.query.filter_by(user_id=user.id)\
                             .order_by(UserHistory.changed_at.desc())

    total = query.count()
    history_rows = query.offset((page - 1) * per_page)\
                         .limit(per_page)\
                         .all()

    # Convert JSON snapshot → dict
    history = []
    for h in history_rows:
        history.append({
            "changed_at": h.changed_at,
            "snapshot": json.loads(h.data_snapshot)
        })

    pagination = {
        "page": page,
        "pages": ceil(total / per_page),
        "has_prev": page > 1,
        "has_next": page < ceil(total / per_page),
        "prev_num": page - 1,
        "next_num": page + 1
    }

    return render_template(
        "user_profile.html",
        user=user,
        history=history,
        pagination=pagination
    )



@user_bp.route("/sellers")
@login_required
def sellers():
    """Show current logged-in user's profile (read-only) chetan athore"""
    return render_template("user_seller_info.html", user=current_user)




# -------------------------------------------------------------------------
from flask import request, jsonify, render_template
from flask_login import login_required, current_user
from app.repositories.analytics_repository import AnalyticsRepository
# from app.blueprints.user import user_bp
# from sqlalchemy import func, extract, or_


@user_bp.route("/analytics")
@login_required
def analytics():
    return render_template("user_analytics_info.html", user=current_user)


# -------------------------
# FILTER PARSER (FIXED)
# -------------------------
def parse_filters(args):
    filters = {
        "status": args.get("status") or None,
        "buying_mode": args.get("buying_mode") or None,
        "ministry": args.get("ministry") or None,
        "date_from": args.get("date_from") or None,
        "date_to": args.get("date_to") or None,
        "min_total": float(args["min_total"]) if args.get("min_total") else None,
        "max_total": float(args["max_total"]) if args.get("max_total") else None,
        'brands': args.getlist('brands[]')
    }

    # print("Filters received:", filters)
    return filters


# -------------------------
# ANALYTICS APIs
# -------------------------
@user_bp.route("/api/analytics/contracts_by_status")
def analytics_contracts_by_status():
    filters = parse_filters(request.args)
    data = AnalyticsRepository.get_contracts_by_status(filters)
    return jsonify([{"status": r[0], "count": r[1]} for r in data])


@user_bp.route("/api/analytics/value_over_time")
def analytics_value_over_time():
    filters = parse_filters(request.args)
    data = AnalyticsRepository.get_value_over_time(filters)
    return jsonify([{"date": r[0], "total": float(r[1] or 0)} for r in data])


@user_bp.route("/api/analytics/top_ministries")
def analytics_top_ministries():
    filters = parse_filters(request.args)
    data = AnalyticsRepository.get_top_ministries(filters)
    return jsonify([{"ministry": r[0], "value": float(r[1] or 0)} for r in data])


@user_bp.route("/api/analytics/avg_by_buying_mode")
def analytics_avg_by_buying_mode():
    filters = parse_filters(request.args)
    data = AnalyticsRepository.get_avg_by_buying_mode(filters)
    return jsonify([{"buying_mode": r[0], "avg_value": float(r[1] or 0)} for r in data])


@user_bp.route("/api/analytics/count_by_month")
def analytics_count_by_month():
    filters = parse_filters(request.args)
    data = AnalyticsRepository.get_count_by_month(filters)

    result = []
    for r in data:
        if r[0] is None or r[1] is None:
            continue   # skip invalid rows

        result.append({
            "year": int(r[0]),
            "month": int(r[1]),
            "count": int(r[2])
        })

    return jsonify(result)

@user_bp.route("/api/analytics/brand_performance")
@login_required
def analytics_brand_performance():

    filters = parse_filters(request.args)

    user_brands = parse_list_csv(current_user.brand_names)

    data = AnalyticsRepository.get_brand_performance(filters, user_brands)

    return jsonify(data)
# -----------------------------------------------------------------------------------
@user_bp.route('/user_compare_brand_info')
@login_required
def user_compare_brand_info():
    """Show current logged-in user's profile (read-only)"""
    return render_template("user_compare_brand_info.html", user=current_user)


@user_bp.route("/api/brands/user")
@login_required
def user_brands():
    print(current_user.brand_names)
    return jsonify(sorted(list(parse_list_csv(current_user.brand_names))))


@user_bp.route("/api/categories/user")
@login_required
def user_categories():
    print(current_user.category_names)
    return jsonify(sorted(list(parse_list_csv(current_user.category_names))))


@user_bp.route("/api/brands/select2")
@login_required
def brands_select2():
    term = request.args.get("term", "").lower()
    brands_set = set()

    brands = Brand.query.all()
    for b in brands:
        brand_name = safe_to_str(b.name)
        if brand_name:
            brands_set.add(brand_name.upper())

    if term:
        brands = [b for b in brands_set if term in b.lower()]
    else:
        brands = list(brands_set)

    return jsonify([
        {"id": b, "text": b}
        for b in sorted(brands)
    ])






@user_bp.route("/api/analytics/brand-compare")
@login_required
def brand_compare():

    # 🔐 Subscription validation
    if not current_user.subscription_date or current_user.subscription_date < datetime.utcnow().date():
        abort(403)

    # 🔹 Read params
    brand1 = safe_to_str(request.args.get("brand1"))
    brand2 = safe_to_str(request.args.get("brand2"))
    month = request.args.get("month")

    if not brand1 or not brand2 or not month:
        abort(400)

    # 🔐 User brand authorization
    user_brands = parse_list_csv(current_user.brand_names)
    if brand1 not in user_brands:
        abort(403)

    # ✅ FAST competitor existence check (SAFE for ALL DBs)
    competitor_exists = False

    contracts = (
        Contract.query
        .with_entities(Contract.items)
        .filter(Contract.items.isnot(None))
        .all()
    )

    for c in contracts:
        for item in c.items or []:
            if isinstance(item, dict) and safe_to_str(item.get("brand")) == brand2:
                competitor_exists = True
                break
        if competitor_exists:
            break

    if not competitor_exists:
        abort(404)

    # 🚀 ANALYTICS (single-pass, optimized)
    data = AnalyticsRepository.compare_brands_monthwise(
        brand1=brand1,
        brand2=brand2,
        month=month
    )

    return jsonify(data)




# --------------------------------------------------------------PDF DOWNLOD------------------------------------


from flask import jsonify
import re
import requests

@user_bp.route("/contracts/<contract_id>/pdf")
@login_required
def get_contract_pdf_url(contract_id):

    try:
        session = requests.Session()

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://gem.gov.in/"
        }

        r = session.post(
            "https://gem.gov.in/view_contracts/sbtCaptcha",
            data={"oid": contract_id},
            headers=headers,
            timeout=10
        )

        data = r.json()

        m = re.search(r"orderId=([^\"&]+)", data.get("code", ""))

        if not m:
            return jsonify({
                "success": False,
                "message": "PDF not found"
            }), 404

        order_id = m.group(1)

        pdf_url = f"https://fulfilment.gem.gov.in/contract/fds?orderId={order_id}"

        return jsonify({
            "success": True,
            "pdf_url": pdf_url
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
# import re
# import requests
# from flask import send_file, abort
# from io import BytesIO

# @user_bp.route("/contracts/<contract_id>/pdf")
# @login_required
# def download_contract_pdf(contract_id):

#     try:
#         session = requests.Session()

#         # Step 1: get orderId
#         r = session.post(
#             "https://gem.gov.in/view_contracts/sbtCaptcha",
#             data={"oid": contract_id},
#             timeout=10
#         )

#         data = r.json()

#         m = re.search(r"orderId=([^\"&]+)", data.get("code", ""))

#         if not m:
#             abort(404)

#         order_id = m.group(1)

#         # Step 2: download pdf
#         pdf_url = f"https://fulfilment.gem.gov.in/contract/fds?orderId={order_id}"

#         pdf = session.get(pdf_url, timeout=20)

#         if "pdf" not in pdf.headers.get("Content-Type", ""):
#             abort(404)

#         return send_file(
#             BytesIO(pdf.content),
#             mimetype="application/pdf",
#             download_name=f"{contract_id}.pdf",
#             as_attachment=True
#         )

#     except Exception:
#         abort(500)





        from flask import send_file
from openpyxl import Workbook
from io import BytesIO
from datetime import datetime, time
from sqlalchemy import func

# @user_bp.route("/sellers/export")
# @login_required
# def export_sellers_excel():

#     # -----------------------------
#     # 🔐 USER ACCESS CHECKS
#     # -----------------------------
#     if not current_user.is_verified or current_user.is_blocked:
#         abort(403)

#     if not current_user.subscription_date or current_user.subscription_date < datetime.utcnow().date():
#         abort(403)

#     # -----------------------------
#     # 📌 USER CATEGORIES
#     # -----------------------------
#     category_set = parse_list_csv(current_user.category_names)

#     if not category_set:
#         abort(403)

#     # -----------------------------
#     # 📌 USER DATE RANGE
#     # -----------------------------
#     assigned_start = current_user.assigned_date_range_start
#     assigned_end = current_user.assigned_date_range_end

#     if not assigned_start or not assigned_end:
#         abort(403)

#     start_dt = datetime.combine(assigned_start, time.min)
#     end_dt = datetime.combine(assigned_end, time.max)

#     # -----------------------------
#     # 📌 FILTERS
#     # -----------------------------
#     filters = parse_seller_filters(request.args)

#     query = Seller.query

#     # apply frontend filters
#     query = apply_seller_filters(query, filters)

#     # 🔐 SECURITY CATEGORY FILTER
#     query = query.filter(
#         func.lower(Seller.category_name).in_(category_set)
#     )

#     # 🔐 SECURITY DATE FILTER
#     query = query.filter(
#         Seller.generated_date >= start_dt,
#         Seller.generated_date <= end_dt
#     )

#     sellers = query.order_by(Seller.id.desc()).all()

#     # -----------------------------
#     # 📌 CREATE EXCEL
#     # -----------------------------
#     wb = Workbook()
#     ws = wb.active
#     ws.title = "Sellers"

#     # Header
#     headers = [
#         "Company Name",
#         "Category",
#         "Email",
#         "GSTIN",
#         "MSME Reg No",
#         "Contact No",
#         "Contract No",
#         "Generated Date"
#     ]

#     ws.append(headers)

#     # Data rows
#     for s in sellers:

#         ws.append([
#             s.company_name,
#             s.category_name,
#             s.email,
#             s.gstin,
#             s.msme_reg_no,
#             s.contact_no,
#             s.contract_no,
#             str(s.generated_date) if s.generated_date else ""
#         ])

#     # -----------------------------
#     # 📌 AUTO WIDTH
#     # -----------------------------
#     for column_cells in ws.columns:

#         length = max(
#             len(str(cell.value or ""))
#             for cell in column_cells
#         )

#         ws.column_dimensions[column_cells[0].column_letter].width = length + 5

#     # -----------------------------
#     # 📌 SAVE MEMORY FILE
#     # -----------------------------
#     output = BytesIO()

#     wb.save(output)

#     output.seek(0)

#     filename = f"sellers_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"

#     return send_file(
#         output,
#         as_attachment=True,
#         download_name=filename,
#         mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     )

@user_bp.route("/sellers/export/excel")
@login_required
def export_sellers_excel():

    # -----------------------------------
    # IMPORTS
    # -----------------------------------

    from io import BytesIO
    import pandas as pd

    # -----------------------------------
    # SECURITY CHECKS
    # -----------------------------------

    if not current_user.is_verified or current_user.is_blocked:
        abort(403)

    if (
        not current_user.subscription_date
        or current_user.subscription_date < datetime.utcnow().date()
    ):
        abort(403)

    # -----------------------------------
    # USER ASSIGNED CATEGORIES
    # -----------------------------------

    category_set = parse_list_csv(
        current_user.category_names
    )

    if not category_set:
        abort(403)

    # -----------------------------------
    # USER ASSIGNED DATE RANGE
    # -----------------------------------

    assigned_start = (
        current_user.assigned_date_range_start
    )

    assigned_end = (
        current_user.assigned_date_range_end
    )

    if not assigned_start or not assigned_end:
        abort(403)

    start_dt = datetime.combine(
        assigned_start,
        time.min
    )

    end_dt = datetime.combine(
        assigned_end,
        time.max
    )

    # -----------------------------------
    # FILTERS
    # -----------------------------------

    filters = parse_seller_filters(
        request.args
    )

    # -----------------------------------
    # BASE QUERY + JOIN
    # -----------------------------------

    query = db.session.query(
        Seller,
        Contract
    ).outerjoin(

        Contract,

        Seller.contract_no
        == Contract.contract_id
    )

    # -----------------------------------
    # APPLY FILTERS
    # -----------------------------------

    query = apply_seller_filters(
        query,
        filters
    )

    # -----------------------------------
    # CATEGORY SECURITY
    # -----------------------------------

    query = query.filter(
        func.lower(
            Seller.category_name
        ).in_(category_set)
    )

    # -----------------------------------
    # DATE SECURITY
    # -----------------------------------

    query = query.filter(

        Seller.generated_date
        >= start_dt,

        Seller.generated_date
        <= end_dt
    )

    # -----------------------------------
    # ORDERING
    # -----------------------------------

    query = query.order_by(
        Seller.id.desc()
    )

    # -----------------------------------
    # FETCH DATA
    # -----------------------------------

    results = query.all()

    # -----------------------------------
    # EXCEL DATA
    # -----------------------------------

    data = []

    for seller, contract in results:

        items = []

        if contract and contract.items:
            items = contract.items

        # if no items still export
        if not items:
            items = [None]

        # -----------------------------------
        # MULTIPLE ITEM ROWS
        # -----------------------------------

        for item in items:

            data.append({

                # -----------------------------------
                # SELLER TABLE
                # -----------------------------------

                "Seller ID":
                seller.id,

                "Company Name":
                seller.company_name,

                "Category":
                seller.category_name,

                "Email":
                seller.email,

                "GSTIN":
                seller.gstin,

                "MSME Reg No":
                seller.msme_reg_no,

                "Contact No":
                seller.contact_no,

                "Contract No":
                seller.contract_no,

                "Generated Date":
                seller.generated_date,

                # -----------------------------------
                # CONTRACT TABLE
                # -----------------------------------

                "Contract ID":
                contract.contract_id
                if contract else "",

                "Status":
                contract.status
                if contract else "",

                "Organization Type":
                contract.organization_type
                if contract else "",

                "Ministry":
                contract.ministry
                if contract else "",

                "Department":
                contract.department
                if contract else "",

                "Organization Name":
                contract.organization_name
                if contract else "",

                "Buying Mode":
                contract.buying_mode
                if contract else "",

                "Contract Date":
                contract.contract_date
                if contract else "",

                "Total":
                contract.total
                if contract else "",

                "Buyer Designation":
                contract.buyer_designation
                if contract else "",

                "Office Zone":
                contract.office_zone
                if contract else "",

                "Bid Number":
                contract.bid_number
                if contract else "",

                "Location":
                contract.location
                if contract else "",

                # -----------------------------------
                # ITEM DETAILS
                # -----------------------------------

                "Brand":
                item.get("brand")
                if item else "",

                "Product":
                item.get("product")
                if item else "",

                "Model":
                item.get("model")
                if item else "",

                "Ordered Quantity":
                item.get("ordered_quantity")
                if item else "",

                "Price":
                item.get("price")
                if item else "",

                "HSN Code":
                item.get("hsn_code")
                if item else "",

                "Service":
                item.get("service")
                if item else "",

                "Item Category":
                item.get("category_name")
                if item else ""

            })

    # -----------------------------------
    # DATAFRAME
    # -----------------------------------

    df = pd.DataFrame(data)

    # -----------------------------------
    # EXCEL FILE
    # -----------------------------------

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Sellers"
        )

        # -----------------------------------
        # AUTO WIDTH
        # -----------------------------------

        worksheet = writer.sheets["Sellers"]

        for column_cells in worksheet.columns:

            length = max(
                len(str(cell.value or ""))
                for cell in column_cells
            )

            worksheet.column_dimensions[
                column_cells[0].column_letter
            ].width = min(length + 5, 50)

    output.seek(0)

    # -----------------------------------
    # RESPONSE
    # -----------------------------------

    response = make_response(
        output.getvalue()
    )

    response.headers[
        "Content-Disposition"
    ] = (
        "attachment; "
        "filename=sellers.xlsx"
    )

    response.headers[
        "Content-Type"
    ] = (
        "application/vnd.openxmlformats-"
        "officedocument.spreadsheetml.sheet"
    )

    return response


from io import BytesIO
import pandas as pd

from flask import (
    request,
    make_response,
    abort,
)

from flask_login import (
    login_required,
    current_user,
)

# from sqlalchemy import and_
# from datetime import datetime


# @user_bp.route("/contracts/export/excel")
# @login_required
# def export_contracts_excel():

#     # -----------------------------------
#     # SECURITY CHECKS
#     # -----------------------------------

#     if not current_user.is_verified or current_user.is_blocked:
#         abort(403)

#     if (
#         not current_user.subscription_date
#         or current_user.subscription_date < datetime.utcnow().date()
#     ):
#         abort(403)

#     # -----------------------------------
#     # USER ASSIGNED BRANDS
#     # -----------------------------------

#     brand_set = parse_list_csv(
#         current_user.brand_names
#     )

#     if not brand_set:
#         abort(403)

#     # -----------------------------------
#     # USER ASSIGNED DATE RANGE
#     # -----------------------------------

#     assigned_start = current_user.assigned_date_range_start
#     assigned_end = current_user.assigned_date_range_end

#     # -----------------------------------
#     # FILTERS
#     # -----------------------------------

#     filters = parse_dynamic_filters(
#         request.args
#     )

#     # -----------------------------------
#     # BASE QUERY
#     # -----------------------------------

#     query = Contract.query

#     # -----------------------------------
#     # DATE RANGE SECURITY
#     # -----------------------------------

#     contract_date_param = request.args.get(
#         "contract_date",
#         None,
#         type=str
#     )

#     contract_date = None

#     if contract_date_param:

#         try:

#             date_obj = datetime.strptime(
#                 contract_date_param,
#                 "%Y-%m-%d"
#             ).date()

#             if (
#                 assigned_start
#                 and assigned_end
#                 and assigned_start <= date_obj <= assigned_end
#             ):

#                 contract_date = date_obj
#                 filters["contract_date"] = (
#                     contract_date_param
#                 )

#         except Exception:

#             contract_date = None

#     # -----------------------------------
#     # ASSIGNED DATE RANGE FILTER
#     # -----------------------------------

#     if not contract_date:

#         if assigned_start and assigned_end:

#             query = query.filter(
#                 and_(
#                     Contract.contract_date
#                     >= assigned_start,

#                     Contract.contract_date
#                     <= assigned_end,
#                 )
#             )

#     # -----------------------------------
#     # APPLY USER FILTERS
#     # -----------------------------------

#     query = apply_contract_filters(
#         query,
#         filters
#     )

#     # -----------------------------------
#     # ASSIGNED BRAND SECURITY
#     # -----------------------------------

#     query = query.filter(
#         Contract.brands.op("&&")(
#             list(brand_set)
#         )
#     )

#     # -----------------------------------
#     # ORDERING
#     # -----------------------------------

#     query = query.order_by(
#         Contract.contract_date.desc()
#     )

#     # -----------------------------------
#     # FETCH DATA
#     # -----------------------------------

#     contracts = query.all()

#     # -----------------------------------
#     # EXCEL DATA
#     # -----------------------------------

#     data = []

#     for contract in contracts:

#         data.append({

#             "ID": contract.id,

#             "Contract ID":
#             contract.contract_id,

#             "Status":
#             contract.status,

#             "Organization Type":
#             contract.organization_type,

#             "Ministry":
#             contract.ministry,

#             "Department":
#             contract.department,

#             "Organization Name":
#             contract.organization_name,

#             "Buying Mode":
#             contract.buying_mode,

#             "Contract Date":
#             contract.contract_date,

#             "Total":
#             contract.total,
#         })

#     # -----------------------------------
#     # DATAFRAME
#     # -----------------------------------

#     df = pd.DataFrame(data)

#     # -----------------------------------
#     # EXCEL FILE
#     # -----------------------------------

#     output = BytesIO()

#     with pd.ExcelWriter(
#         output,
#         engine="openpyxl"
#     ) as writer:

#         df.to_excel(
#             writer,
#             index=False,
#             sheet_name="Contracts"
#         )

#     output.seek(0)

#     # -----------------------------------
#     # RESPONSE
#     # -----------------------------------

#     response = make_response(
#         output.getvalue()
#     )

#     response.headers[
#         "Content-Disposition"
#     ] = (
#         "attachment; "
#         "filename=contracts.xlsx"
#     )

#     response.headers[
#         "Content-Type"
#     ] = (
#         "application/vnd.openxmlformats-"
#         "officedocument.spreadsheetml.sheet"
#     )

#     return response
# @user_bp.route("/contracts/export/excel")
# @login_required
# def export_contracts_excel():

#     # -----------------------------------
#     # IMPORTS
#     # -----------------------------------
#     from io import BytesIO
#     import pandas as pd
#     from sqlalchemy import and_

#     # -----------------------------------
#     # SECURITY CHECKS
#     # -----------------------------------
#     if not current_user.is_verified or current_user.is_blocked:
#         abort(403)

#     if (
#         not current_user.subscription_date
#         or current_user.subscription_date < datetime.utcnow().date()
#     ):
#         abort(403)

#     # -----------------------------------
#     # USER ASSIGNED BRANDS
#     # -----------------------------------
#     brand_set = {
#     b.strip().lower()
#     for b in parse_list_csv(current_user.brand_names)
# }

#     if not brand_set:
#         abort(403)

#     # -----------------------------------
#     # USER ASSIGNED DATE RANGE
#     # -----------------------------------
#     assigned_start = current_user.assigned_date_range_start
#     assigned_end = current_user.assigned_date_range_end

#     # -----------------------------------
#     # FILTERS
#     # -----------------------------------
#     filters = parse_dynamic_filters(request.args)

#     # -----------------------------------
#     # BASE QUERY + JOIN
#     # -----------------------------------
#     query = db.session.query(Contract, Seller).outerjoin(
#         Seller, Contract.contract_id == Seller.contract_no
#     )

#     # -----------------------------------
#     # DATE RANGE SECURITY
#     # -----------------------------------
#     contract_date_param = request.args.get("contract_date", None, type=str)
#     contract_date = None

#     if contract_date_param:
#         try:
#             date_obj = datetime.strptime(contract_date_param, "%Y-%m-%d").date()

#             if (
#                 assigned_start
#                 and assigned_end
#                 and assigned_start <= date_obj <= assigned_end
#             ):
#                 contract_date = date_obj
#                 filters["contract_date"] = contract_date_param

#         except Exception:
#             contract_date = None

#     # -----------------------------------
#     # ASSIGNED DATE RANGE FILTER
#     # -----------------------------------
#     if not contract_date:
#         if assigned_start and assigned_end:
#             query = query.filter(
#                 and_(
#                     Contract.contract_date >= assigned_start,
#                     Contract.contract_date <= assigned_end,
#                 )
#             )

#     # -----------------------------------
#     # APPLY USER FILTERS
#     # -----------------------------------
#     query = apply_contract_filters(query, filters)

#     # -----------------------------------
#     # ASSIGNED BRAND SECURITY
#     # -----------------------------------
#     # query = query.filter(Contract.brands.op("&&")(list(brand_set)))
#     from sqlalchemy import text

#     query = query.filter(
#         text("""
#             EXISTS (
#                 SELECT 1
#                 FROM unnest(contracts.brands) AS b
#                 WHERE lower(b) = ANY(:brands)
#             )
#         """)
#     ).params(
#         brands=[b.lower() for b in brand_set]
#     )
#     # -----------------------------------
#     # ORDERING
#     # -----------------------------------
#     query = query.order_by(Contract.contract_date.desc())

#     # -----------------------------------
#     # FETCH DATA
#     # -----------------------------------
#     results = query.all()

#     # -----------------------------------
#     # EXCEL DATA
#     # -----------------------------------
#     data = []

#     for contract, seller in results:
        
#         # Pull item arrays from the contract row
#         items = []
#         if contract and contract.items:
#             items = contract.items

#         # If a contract has no sub-items, we still want to export it once
#         if not items:
#             items = [None]

#         # Loop through each individual item inside the contract
#         for item in items:
#             data.append(
#                 {
#                     # -----------------------------------
#                     # CONTRACT DETAILS
#                     # -----------------------------------
#                     "ID": contract.id,
#                     "Contract ID": contract.contract_id,
#                     "Status": contract.status,
#                     "Organization Type": contract.organization_type,
#                     "Ministry": contract.ministry,
#                     "Department": contract.department,
#                     "Organization Name": contract.organization_name,
#                     "Buying Mode": contract.buying_mode,
#                     "Contract Date": contract.contract_date,
#                     "Total": contract.total,
                    
#                     # -----------------------------------
#                     # SELLER DETAILS
#                     # -----------------------------------
#                     "Seller ID": seller.id if seller else "",
#                     "Company Name": seller.company_name if seller else "",
#                     "Seller Category": seller.category_name if seller else "",
#                     "Seller Email": seller.email if seller else "",
#                     "GSTIN": seller.gstin if seller else "",
#                     "MSME Reg No": seller.msme_reg_no if seller else "",
#                     "Contact No": seller.contact_no if seller else "",

#                     # -----------------------------------
#                     # ITEM DETAILS (Added Here)
#                     # -----------------------------------
#                     "Brand": item.get("brand") if item else "",
#                     "Product": item.get("product") if item else "",
#                     "Model": item.get("model") if item else "",
#                     "Ordered Quantity": item.get("ordered_quantity") if item else "",
#                     "Price": item.get("price") if item else "",
#                     "HSN Code": item.get("hsn_code") if item else "",
#                     "Service": item.get("service") if item else "",
#                     "Item Category": item.get("category_name") if item else ""
#                 }
#             )

#     # -----------------------------------
#     # DATAFRAME
#     # -----------------------------------
#     df = pd.DataFrame(data)

#     # -----------------------------------
#     # EXCEL FILE GENERATION
#     # -----------------------------------
#     output = BytesIO()

#     with pd.ExcelWriter(output, engine="openpyxl") as writer:
#         df.to_excel(writer, index=False, sheet_name="Contracts")

#         # -----------------------------------
#         # AUTO COLUMN WIDTH
#         # -----------------------------------
#         worksheet = writer.sheets["Contracts"]

#         for column_cells in worksheet.columns:
#             length = max(
#                 len(str(cell.value or "")) for cell in column_cells
#             )
#             worksheet.column_dimensions[
#                 column_cells[0].column_letter
#             ].width = min(length + 5, 50)

#     output.seek(0)

#     # -----------------------------------
#     # RESPONSE
#     # -----------------------------------
#     response = make_response(output.getvalue())
#     response.headers["Content-Disposition"] = (
#         "attachment; filename=contracts.xlsx"
#     )
#     response.headers["Content-Type"] = (
#         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     )

#     return response




@user_bp.route("/contracts/export/excel")
@login_required
def export_contracts_excel():

    # -----------------------------------
    # IMPORTS
    # -----------------------------------
    from io import BytesIO
    import pandas as pd
    from sqlalchemy import and_
    from datetime import datetime

    # -----------------------------------
    # SECURITY CHECKS
    # -----------------------------------
    if not current_user.is_verified or current_user.is_blocked:
        abort(403)

    if (
        not current_user.subscription_date
        or current_user.subscription_date < datetime.utcnow().date()
    ):
        abort(403)

    # -----------------------------------
    # USER ASSIGNED BRANDS
    # -----------------------------------
    brand_set = {
        b.strip().lower()
        for b in parse_list_csv(current_user.brand_names)
    }

    if not brand_set:
        abort(403)

    # -----------------------------------
    # USER ASSIGNED DATE RANGE
    # -----------------------------------
    assigned_start = current_user.assigned_date_range_start
    assigned_end = current_user.assigned_date_range_end

    # -----------------------------------
    # FILTERS
    # -----------------------------------
    filters = parse_dynamic_filters(request.args)

    # -----------------------------------
    # BASE QUERY + JOIN
    # -----------------------------------
    query = db.session.query(Contract, Seller).outerjoin(
        Seller, Contract.contract_id == Seller.contract_no
    )

    # -----------------------------------
    # FIXED: Capture range parameters from UI for Excel Export
    # -----------------------------------
    date_from_param = request.args.get("date_from", "", type=str)
    date_to_param = request.args.get("date_to", "", type=str)

    if date_from_param:
        filters["date_from"] = date_from_param
    if date_to_param:
        filters["date_to"] = date_to_param

    # Global Profile Fallback Restriction: Only applies if user DID NOT provide search dates
    if not date_from_param and not date_to_param:
        if assigned_start and assigned_end:
            query = query.filter(
                and_(
                    Contract.contract_date >= assigned_start,
                    Contract.contract_date <= assigned_end,
                )
            )

    # -----------------------------------
    # APPLY USER FILTERS (Processes your date ranges via updated filter helper)
    # -----------------------------------
    query = apply_contract_filters(query, filters)

    # -----------------------------------
    # ASSIGNED BRAND SECURITY
    # -----------------------------------
    from sqlalchemy import text

    query = query.filter(
        text("""
            EXISTS (
                SELECT 1
                FROM unnest(contracts.brands) AS b
                WHERE lower(b) = ANY(:brands)
            )
        """)
    ).params(
        brands=[b.lower() for b in brand_set]
    )

    # -----------------------------------
    # ORDERING
    # -----------------------------------
    query = query.order_by(Contract.contract_date.desc())

    # -----------------------------------
    # FETCH DATA
    # -----------------------------------
    results = query.all()

    # -----------------------------------
    # EXCEL DATA
    # -----------------------------------
    data = []

    for contract, seller in results:
        
        # Pull item arrays from the contract row
        items = []
        if contract and contract.items:
            items = contract.items

        # If a contract has no sub-items, we still want to export it once
        if not items:
            items = [None]

        # Loop through each individual item inside the contract
        for item in items:
            data.append(
                {
                    # -----------------------------------
                    # CONTRACT DETAILS
                    # -----------------------------------
                    "ID": contract.id,
                    "Contract ID": contract.contract_id,
                    "Status": contract.status,
                    "Organization Type": contract.organization_type,
                    "Ministry": contract.ministry,
                    "Department": contract.department,
                    "Organization Name": contract.organization_name,
                    "Buying Mode": contract.buying_mode,
                    "Contract Date": contract.contract_date,
                    "Total": contract.total,
                    
                    # -----------------------------------
                    # SELLER DETAILS
                    # -----------------------------------
                    "Seller ID": seller.id if seller else "",
                    "Company Name": seller.company_name if seller else "",
                    "Seller Category": seller.category_name if seller else "",
                    "Seller Email": seller.email if seller else "",
                    "GSTIN": seller.gstin if seller else "",
                    "MSME Reg No": seller.msme_reg_no if seller else "",
                    "Contact No": seller.contact_no if seller else "",

                    # -----------------------------------
                    # ITEM DETAILS
                    # -----------------------------------
                    "Brand": item.get("brand") if item else "",
                    "Product": item.get("product") if item else "",
                    "Model": item.get("model") if item else "",
                    "Ordered Quantity": item.get("ordered_quantity") if item else "",
                    "Price": item.get("price") if item else "",
                    "HSN Code": item.get("hsn_code") if item else "",
                    "Service": item.get("service") if item else "",
                    "Item Category": item.get("category_name") if item else ""
                }
            )

    # -----------------------------------
    # DATAFRAME & EXCEL FILE GENERATION
    # -----------------------------------
    if not data:
        # Create an empty DataFrame with headers if no records match to prevent download errors
        df = pd.DataFrame(columns=[
            "ID", "Contract ID", "Status", "Organization Type", "Ministry", "Department",
            "Organization Name", "Buying Mode", "Contract Date", "Total", "Seller ID",
            "Company Name", "Seller Category", "Seller Email", "GSTIN", "MSME Reg No",
            "Contact No", "Brand", "Product", "Model", "Ordered Quantity", "Price",
            "HSN Code", "Service", "Item Category"
        ])
    else:
        df = pd.DataFrame(data)

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Contracts")

        # -----------------------------------
        # AUTO COLUMN WIDTH
        # -----------------------------------
        worksheet = writer.sheets["Contracts"]

        for column_cells in worksheet.columns:
            length = max(
                len(str(cell.value or "")) for cell in column_cells
            )
            worksheet.column_dimensions[
                column_cells[0].column_letter
            ].width = min(length + 5, 50)

    output.seek(0)

    # -----------------------------------
    # RESPONSE
    # -----------------------------------
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = (
        "attachment; filename=contracts.xlsx"
    )
    response.headers["Content-Type"] = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    return response