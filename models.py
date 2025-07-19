from extensions import db
from datetime import date

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_type = db.Column(db.String(100))
    brand = db.Column(db.String(100))
    model_number = db.Column(db.String(100))
    serial_number = db.Column(db.String(100))
    company_barcode = db.Column(db.String(100))
    assigned_to = db.Column(db.String(100))
    department = db.Column(db.String(100))
    given_date = db.Column(db.Date)
    status = db.Column(db.String(100))
    return_date = db.Column(db.Date)
    project_name = db.Column(db.String(100))
    purchase_date = db.Column(db.Date)
    vendor_name = db.Column(db.String(100))
    system_details = db.Column(db.Text)
    remarks = db.Column(db.Text)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'admin' or 'user'