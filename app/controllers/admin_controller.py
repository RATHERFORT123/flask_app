from urllib import request
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from ..models.contract import Contract
from ..models.seller import Seller
from ..models.ucfd import UCFD
from ..extensions import db
from functools import wraps
from flask import request

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def extract_unique_contract_fields():
    fields = [
        'status','organization_type','ministry','department','organization_name','office_zone',
        'location','buyer_designation','buying_mode','bid_number','contract_date','total'
    ]
    unique_values = set()
    contracts = Contract.query.all()
    for contract in contracts:
        row = tuple(getattr(contract, f) for f in fields)
        unique_values.add(row)
    return [dict(zip(fields, row)) for row in unique_values]

def extract_unique_items_fields():
    item_fields = ['service','product','brand','model','hsn_code','ordered_quantity','price']
    unique_items = set()
    contracts = Contract.query.all()
    for contract in contracts:
        if contract.items:
            for item in contract.items:
                row = tuple(item.get(f) for f in item_fields)
                unique_items.add(row)
    return [dict(zip(item_fields, row)) for row in unique_items]

def extract_unique_seller_fields():
    seller_fields = [
        'generated_date','category_name','seller_id','company_name','contact_no',
        'email','address','msme_reg_no','gstin'
    ]
    unique_sellers = set()
    sellers = Seller.query.all()
    for seller in sellers:
        row = tuple(getattr(seller, f) for f in seller_fields)
        unique_sellers.add(row)
    return [dict(zip(seller_fields, row)) for row in unique_sellers]




@admin_bp.route("/ucfd_view", methods=["GET"])
@login_required
@admin_required
def ucfd_view():
    if request.args.get('fetch'):
        contract_uniques = extract_unique_contract_fields()
        items_uniques = extract_unique_items_fields()
        seller_uniques = extract_unique_seller_fields()
        all_rows = contract_uniques + items_uniques + seller_uniques
        for data in all_rows:
            try:
                ucfd_row = UCFD(**data)
                db.session.add(ucfd_row)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
    page = int(request.args.get("page", 1))
    per_page = 50
    ucfd_rows = UCFD.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template("admin_ucfd_filter.html", ucfd=ucfd_rows.items, pagination=ucfd_rows)





from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy import func, extract
from datetime import datetime

from ..extensions import db
from ..models.contract import Contract
from ..models.seller import Seller



@admin_bp.route("/delete-month-dashboard")
@login_required
@admin_required
def delete_month_dashboard():

    # CONTRACT MONTH COUNTS
    contract_year = extract("year", Contract.contract_date)
    contract_month = extract("month", Contract.contract_date)

    contract_counts = db.session.query(
        contract_year.label("year"),
        contract_month.label("month"),
        func.count(Contract.id).label("count")
    ).filter(
        Contract.contract_date != None
    ).group_by(
        contract_year,
        contract_month
    ).order_by(
        contract_year.desc(),
        contract_month.desc()
    ).all()


    # SELLER MONTH COUNTS
    seller_year = extract("year", Seller.generated_date)
    seller_month = extract("month", Seller.generated_date)

    seller_counts = db.session.query(
        seller_year.label("year"),
        seller_month.label("month"),
        func.count(Seller.id).label("count")
    ).filter(
        Seller.generated_date != None
    ).group_by(
        seller_year,
        seller_month
    ).order_by(
        seller_year.desc(),
        seller_month.desc()
    ).all()


    return render_template(
        "delete_month_dashboard.html",
        contract_counts=contract_counts,
        seller_counts=seller_counts
    )


@admin_bp.route("/delete-month/<data_type>/<int:year>/<int:month>")
@login_required
@admin_required
def delete_month(data_type, year, month):

    start_date = datetime(year, month, 1)

    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    deleted_rows = 0

    if data_type == "contracts":

        deleted_rows = Contract.query.filter(
            Contract.contract_date >= start_date,
            Contract.contract_date < end_date
        ).delete()

    elif data_type == "sellers":

        deleted_rows = Seller.query.filter(
            Seller.generated_date >= start_date,
            Seller.generated_date < end_date
        ).delete()

    db.session.commit()

    flash(f"{deleted_rows} {data_type} deleted for {month}-{year}", "success")

    return redirect(url_for("admin.delete_month_dashboard"))