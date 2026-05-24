# repositories/analytics_repository.py
from collections import Counter
from collections import defaultdict
from datetime import datetime
from sqlalchemy import extract
from sqlalchemy import func, extract, or_, cast, String
from ..models.contract import Contract

# from sqlalchemy import func, extract
from app.models.contract import Contract
from app import db
# ✅ DEFINE safe_to_str HERE (or import it)
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
from sqlalchemy import func, extract
from app.models.contract import Contract
from app import db
from sqlalchemy import func, extract, or_


class AnalyticsRepository:
     

    @staticmethod
    def get_brand_performance(filters, user_brands):
    
        brand = func.unnest(Contract.brands).label("brand")
    
        query = db.session.query(
            brand,
            func.sum(Contract.total).label("revenue"),
            func.count(Contract.id).label("orders")
        )
    
        # apply existing filters
        query = AnalyticsRepository.apply_filters(query, filters)
    
        query = query.group_by(brand)
    
        data = query.all()
    
        # convert to dict
        result = []
    
        for r in data:
            result.append({
                "brand": r[0],
                "revenue": float(r[1] or 0),
                "orders": int(r[2]),
                "is_user_brand": r[0] in user_brands
            })
    
        # sort by revenue
        result.sort(key=lambda x: x["revenue"], reverse=True)
    
        # take top 5 market brands
        top_market = result[:5]
    
        # add user brands if not already included
        for b in user_brands:
            for r in result:
                if r["brand"] == b and r not in top_market:
                    top_market.append(r)
    
        return top_market
    # -------------------------
    # APPLY FILTERS (FIXED)
    # -------------------------
    @staticmethod
    def apply_filters(query, filters):
        if filters.get("status"):
            query = query.filter(Contract.status == filters["status"])

        if filters.get("buying_mode"):
            query = query.filter(Contract.buying_mode == filters["buying_mode"])

        if filters.get("ministry"):
            query = query.filter(
                Contract.ministry.ilike(f"%{filters['ministry']}%")
            )

        if filters.get("date_from"):
            query = query.filter(Contract.contract_date >= filters["date_from"])

        if filters.get("date_to"):
            query = query.filter(Contract.contract_date <= filters["date_to"])

        if filters.get("min_total") is not None:
            query = query.filter(Contract.total >= filters["min_total"])

        if filters.get("max_total") is not None:
            query = query.filter(Contract.total <= filters["max_total"])

        # return query

        # if filters.get('brands'):
        #         brand_conditions = []
        #         for brand in filters['brands']:
        #             brand_conditions.append(
        #                 Contract.items[0]['brand'].astext == brand
        #             )
        #         query = query.filter(or_(*brand_conditions))
        if filters.get("brands"):
         brands = filters["brands"]
 
         brand_conditions = [
             cast(Contract.items, String).ilike(f'%\"brand\": \"{b}\"%')
             for b in brands
         ]
 
         query = query.filter(or_(*brand_conditions))
        return query
    # -------------------------
    # CONTRACTS BY STATUS
    # -------------------------
    @staticmethod
    def get_contracts_by_status(filters):
        query = db.session.query(
            Contract.status,
            func.count(Contract.id)
        )

        query = AnalyticsRepository.apply_filters(query, filters)

        query = query.group_by(Contract.status)

        return query.all()


    # -------------------------
    # VALUE OVER TIME
    # -------------------------
    @staticmethod
    def get_value_over_time(filters):
        # month_expr = func.strftime('%Y-%m', Contract.contract_date)
        month_expr = func.to_char(Contract.contract_date, 'YYYY-MM')

        query = db.session.query(
            month_expr.label("date"),
            func.sum(Contract.total)
        )

        query = AnalyticsRepository.apply_filters(query, filters)

        query = query.group_by(month_expr).order_by(month_expr)

        return query.all()


    # -------------------------
    # TOP MINISTRIES
    # -------------------------
    @staticmethod
    def get_top_ministries(filters, limit=10):
        query = db.session.query(
            Contract.ministry,
            func.sum(Contract.total)
        )

        query = AnalyticsRepository.apply_filters(query, filters)

        query = query.group_by(Contract.ministry)\
                     .order_by(func.sum(Contract.total).desc())

        return query.limit(limit).all()


    # -------------------------
    # AVG BY BUYING MODE
    # -------------------------
    @staticmethod
    def get_avg_by_buying_mode(filters):
        query = db.session.query(
            Contract.buying_mode,
            func.avg(Contract.total)
        )

        query = AnalyticsRepository.apply_filters(query, filters)

        query = query.group_by(Contract.buying_mode)

        return query.all()


    # -------------------------
    # COUNT BY MONTH
    # -------------------------
    # @staticmethod
    # def get_count_by_month(filters):
    #     query = db.session.query(
    #         extract("year", Contract.contract_date).label("year"),
    #         extract("month", Contract.contract_date).label("month"),
    #         func.count(Contract.id)
    #     )

    #     query = AnalyticsRepository.apply_filters(query, filters)

    #     query = query.group_by("year", "month").order_by("year", "month")

    #     return query.all()
    @staticmethod
    def get_count_by_month(filters):
        query = db.session.query(
            extract("year", Contract.contract_date).label("year"),
            extract("month", Contract.contract_date).label("month"),
            func.count(Contract.id).label("count")
        ).filter(
            Contract.contract_date.isnot(None)   # 🔥 IMPORTANT
        )
    
        query = AnalyticsRepository.apply_filters(query, filters)
    
        query = query.group_by("year", "month").order_by("year", "month")
    
        return query.all()




# ----------------------------------------------------------------------------------------------
# from sqlalchemy import extract


# class AnalyticsRepository:

    @staticmethod
    def compare_brands_monthwise(brand1, brand2, month):
        """
        brand1 and brand2 are EXPECTED to be already normalized (lowercase)
        """

        year, mon = map(int, month.split("-"))

        contracts = (
            Contract.query
            .filter(
                Contract.contract_date.isnot(None),
                extract("year", Contract.contract_date) == year,
                extract("month", Contract.contract_date) == mon
            )
            .all()
        )

        def init(name):
            return {
                "name": name,
                "orders": 0,
                "revenue": 0.0,
                "avg_order_value": 0.0,
                "quantity_sold": 0,
                "status_breakdown": {},
                "buying_modes": {},
                "categories": set()
            }

        result = {
            brand1: init(brand1),
            brand2: init(brand2)
        }

        # 🔥 SINGLE PASS — FAST & SAFE
        for c in contracts:
            for item in c.items or []:
                if not isinstance(item, dict):
                    continue

                item_brand = (item.get("brand") or "").strip().lower()
                if item_brand not in result:
                    continue

                r = result[item_brand]

                r["orders"] += 1
                r["revenue"] += float(c.total or 0)
                r["quantity_sold"] += int(item.get("ordered_quantity") or 0)

                status = (c.status or "unknown").strip().lower()
                r["status_breakdown"][status] = r["status_breakdown"].get(status, 0) + 1

                mode = (c.buying_mode or "unknown").strip().lower()
                r["buying_modes"][mode] = r["buying_modes"].get(mode, 0) + 1

                cat = (item.get("category_name") or "").strip().lower()
                if cat:
                    r["categories"].add(cat)

        # Final formatting
        for r in result.values():
            if r["orders"]:
                r["avg_order_value"] = round(r["revenue"] / r["orders"], 2)
            r["revenue"] = round(r["revenue"], 2)
            r["categories"] = sorted(r["categories"])

        return {
            "brand_1": result[brand1],
            "brand_2": result[brand2]
        }

