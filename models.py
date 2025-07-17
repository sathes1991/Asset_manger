from extensions import db
from datetime import date

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset_type = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    model_number = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    company_barcode = db.Column(db.String(100), unique=True, nullable=False)
    assigned_to = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))
    given_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(50), nullable=False, default='In Stock')
    return_date = db.Column(db.Date)
    project_name = db.Column(db.String(100))
    purchase_date = db.Column(db.Date)
    vendor_name = db.Column(db.String(100))
    system_details = db.Column(db.String(255))
    remarks = db.Column(db.Text)
    