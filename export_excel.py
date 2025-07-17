from models import Asset
import pandas as pd
from datetime import datetime
from flask import current_app

def export_assets_to_excel():
    with current_app.app_context():
        assets = Asset.query.all()
        data = [{
            'Type': a.asset_type,
            'Brand': a.brand,
            'Model': a.model_number,
            'Serial': a.serial_number,
            'Barcode': a.company_barcode,
            'Assigned To': a.assigned_to,
            'Department': a.department,
            'Given Date': a.given_date.strftime('%Y-%m-%d') if a.given_date else '',
            'Status': a.status,
            'Return Date': a.return_date.strftime('%Y-%m-%d') if a.return_date else '',
            'Project Name': a.project_name,
            'Purchase Date': a.purchase_date.strftime('%Y-%m-%d') if a.purchase_date else '',
            'Vendor Name': a.vendor_name,
            'System Details': a.system_details,
            'Remarks': a.remarks
        } for a in assets]

        filename = f'data/assets_export_{datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx'
        pd.DataFrame(data).to_excel(filename, index=False)
        return filename
