from flask import (
    Blueprint,
    jsonify,
    request
)

from flask_login import (
    login_required
)

from ..models.brand import Brand
from ..models.category import Category

from .admin_user_controller import admin_required


search_bp = Blueprint(
    "search",
    __name__,
    url_prefix="/admin/search"
)


# =====================================================
# SEARCH BRANDS
# =====================================================

@search_bp.route("/brands")
@login_required
@admin_required
def search_brands():

    term = request.args.get(
        "term",
        ""
    ).lower()

    brands_set = set()

    brands = Brand.query.with_entities(
        Brand.name
    ).all()

    for (name,) in brands:

        if name:
            brands_set.add(name.strip())

    if term:
        result = [
            b for b in brands_set
            if term in b.lower()
        ]
    else:
        result = list(brands_set)

    return jsonify(
        sorted(result)
    )


# =====================================================
# SEARCH CATEGORIES
# =====================================================

@search_bp.route("/categories")
@login_required
@admin_required
def search_categories():

    term = request.args.get(
        "term",
        ""
    ).strip().lower()

    query = Category.query

    if term:

        query = query.filter(
            Category.value.ilike(
                f"%{term}%"
            )
        )

    categories = query.order_by(
        Category.value
    ).limit(20).all()

    return jsonify(
        [c.value for c in categories]
    )