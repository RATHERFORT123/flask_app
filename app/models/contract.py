







from sqlalchemy.dialects.postgresql import JSON
from ..extensions import db
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String

class Contract(db.Model):
    __tablename__ = 'contracts'

    id = db.Column(db.Integer, primary_key=True)

    # 🔼 was 255
    contract_id = db.Column(db.String(500), unique=True, nullable=False)

    # 🔼 was 100
    status = db.Column(db.String(300))

    # 🔼 was 100
    organization_type = db.Column(db.String(300))

    # 🔼 was 255
    ministry = db.Column(db.String(500))

    # 🔼 was 255
    department = db.Column(db.String(500))

    # 🔼 was 255
    organization_name = db.Column(db.String(800))

    # 🔼 was 100 (this was breaking!)
    office_zone = db.Column(db.String(800))

    # 🔼 was 255
    location = db.Column(db.String(500))

    # 🔼 was 100
    buyer_designation = db.Column(db.String(300))

    # 🔼 was 100
    buying_mode = db.Column(db.String(200))

    # 🔼 was 100
    bid_number = db.Column(db.String(200))

    contract_date = db.Column(db.DateTime)
    total = db.Column(db.Float)

    # ✅ JSON is correct (NO change)
    items = db.Column(JSON)
    brands = db.Column(db.ARRAY(db.String))
    # brand = db.Column(db.String(300), index=True)








# from sqlalchemy.dialects.postgresql import JSON
# from ..extensions import db

# class Contract(db.Model):
#     __tablename__ = 'contracts'
#     id = db.Column(db.Integer, primary_key=True)
#     contract_id = db.Column(db.String(255), unique=True, nullable=False)
#     status = db.Column(db.String(100))
#     organization_type = db.Column(db.String(100))
#     ministry = db.Column(db.String(255))
#     department = db.Column(db.String(255))
#     organization_name = db.Column(db.String(255))
#     office_zone = db.Column(db.String(100))
#     location = db.Column(db.String(255))
#     buyer_designation = db.Column(db.String(100))
#     buying_mode = db.Column(db.String(100))
#     bid_number = db.Column(db.String(100))
#     contract_date = db.Column(db.DateTime)
#     total = db.Column(db.Float)
#     items = db.Column(JSON)  # JSON array of item dicts
