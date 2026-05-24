from ..extensions import db
from ..models.contract import Contract
import pandas as pd
import math

def sanitize_json_value(value):
    """
    Convert pandas NaN to None so PostgreSQL JSON accepts it
    """
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    return value

def parse_value(value, target_type=str):
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    # if target_type == str:
    #     if isinstance(value, str) and value.strip() == "":
    #         return None
    #     return str(value)
    if target_type == str:
       if isinstance(value, (int, float)):
           return str(int(value))
       return str(value).strip() or None

    if target_type == float:
        try:
            return float(value)
        except:
            return None
    if target_type == 'datetime':
        try:
            # dt = pd.to_datetime(value, errors='coerce')
            dt = pd.to_datetime(value, dayfirst=True, errors='coerce')

            if pd.isna(dt):
                return None
            return dt.to_pydatetime()
        except:
            return None
    return value

def get_unique_items(items):
    seen = set()
    unique_items = []
    for item in items:
        raw_service = item.get('service')
        raw_product = item.get('product')

        def clean_key(value):
            if isinstance(value, str):
                return value.strip().lower()
            elif value is None or (isinstance(value, float) and pd.isna(value)):
                return ''
            else:
                return str(value).strip().lower()

        service_key = clean_key(raw_service)
        product_key = clean_key(raw_product)

        # Use service_key if present, else product_key as uniqueness key
        unique_key = service_key or product_key

        if unique_key and unique_key not in seen:
            seen.add(unique_key)
            unique_items.append(item)

    return unique_items


from datetime import datetime, timedelta
from app.models.contract import Contract

def get_contracts_filtered_paginated(filters, page=1, per_page=50):

    query = Contract.query

    for field in [
        'status','organization_type','ministry','department','organization_name',
        'office_zone','location','buyer_designation','buying_mode',
        'bid_number','contract_date','total','contract_id'
    ]:

        val = filters.get(field)

        if not val:
            continue

        col = getattr(Contract, field)

        # DATE FILTER (important fix)
        if field == "contract_date":

            if isinstance(val, str):
                val = datetime.strptime(val, "%Y-%m-%d")

            next_day = val + timedelta(days=1)

            query = query.filter(
                col >= val,
                col < next_day
            )

        elif field == "total":
            query = query.filter(col == val)

        else:
            query = query.filter(col.ilike(f"%{val}%"))

    return query.order_by(Contract.contract_date.desc()).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

import math

def sanitize_json(obj):
    """
    Recursively replace NaN with None (PostgreSQL JSON-safe)
    """
    if isinstance(obj, dict):
        return {k: sanitize_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_json(v) for v in obj]
    elif isinstance(obj, float) and math.isnan(obj):
        return None
    else:
        return obj



def add_contract(contract_data):

    try:

        contract_id = parse_value(contract_data.get('contract_id'), str)

        if not contract_id:
            return False

        raw_items = contract_data.get('items', [])
        clean_items = sanitize_json(raw_items)
        unique_items = get_unique_items(clean_items)

        # =========================
        # EXTRACT ALL BRANDS
        # =========================

        brands = {
            str(
                item.get("brand")
                or item.get("Brand")
                or item.get("brand_name")
                or item.get("Brand Name")
            ).strip()
            for item in unique_items
            if (
                item.get("brand")
                or item.get("Brand")
                or item.get("brand_name")
                or item.get("Brand Name")
            )
        }
        
        brands = list(brands)

        # =========================

        contract = Contract.query.filter_by(contract_id=contract_id).first()

        if contract:

            existing_items = sanitize_json(contract.items or [])
            contract.items = get_unique_items(existing_items + unique_items)

            if brands:
                existing = set(contract.brands or [])
                contract.brands = list(existing.union(brands))

            db.session.commit()

            return True

        # create new contract
        contract = Contract(

            contract_id=contract_id,
            status=parse_value(contract_data.get('status'), str),
            organization_type=parse_value(contract_data.get('organization_type'), str),
            ministry=parse_value(contract_data.get('ministry'), str),
            department=parse_value(contract_data.get('department'), str),
            organization_name=parse_value(contract_data.get('organization_name'), str),
            office_zone=parse_value(contract_data.get('office_zone'), str),
            location=parse_value(contract_data.get('location'), str),
            buyer_designation=parse_value(contract_data.get('buyer_designation'), str),
            buying_mode=parse_value(contract_data.get('buying_mode'), str),
            bid_number=parse_value(contract_data.get('bid_number'), str),
            contract_date=parse_value(contract_data.get('contract_date'), 'datetime'),
            total=parse_value(contract_data.get('total'), float),

            # FIX HERE
            brands=brands,

            items=unique_items
        )

        db.session.add(contract)
        db.session.commit()

        return True

    except Exception as e:

        db.session.rollback()
        print("❌ Contract insert failed:", e)

        return False
def bulk_delete(contract_ids):
    if not contract_ids:
        return 0
    count = Contract.query.filter(Contract.id.in_(contract_ids)).delete(synchronize_session=False)
    db.session.commit()
    return count








def get_contracts_filtered_paginated_user(filters, page=1, per_page=50):
    query = Contract.query

    # Apply generic filters
    for field in ['status', 'organization_type', 'ministry', 'department', 'organization_name',
                  'office_zone', 'location', 'buyer_designation', 'buying_mode', 'bid_number',
                  'contract_id']:
        val = filters.get(field)
        if val:
            col = getattr(Contract, field)
            query = query.filter(col.ilike(f"%{val}%"))

    # Filter by contract_date if precise date given
    contract_date = filters.get('contract_date')
    if contract_date:
        query = query.filter(Contract.contract_date == contract_date)

    # Filter by category_names list (assumed Contract.items contains category_name)
    category_names = filters.get('category_names')
    if category_names:
        # Filter contracts having at least one item with category_name in list
        query = query.filter(
            Contract.items.op('jsonb_path_exists')(
                f"$[*] ? (@.category_name in {category_names})"
            )
        )

    # Filter by brand_names list (assumed Contract.items contains brand)
    # brand_names = filters.get('brand_names')
    # if brand_names:
    #     query = query.filter(
    #         Contract.items.op('jsonb_path_exists')(
    #             f"$[*] ? (@.brand in {brand_names})"
    #         )
    #     )
    brand_names = filters.get('brand_names')
    
    if brand_names:
    
        query = query.filter(
            Contract.brands.overlap(brand_names)
        )
    return query.order_by(Contract.contract_date.desc()).paginate(page=page, per_page=per_page)

