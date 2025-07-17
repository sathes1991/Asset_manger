from flask import Flask, render_template, request, redirect, send_file, flash, url_for
from extensions import db
from models import Asset
from export_excel import export_assets_to_excel
import os
from datetime import date, datetime

# 1. Create Flask app and set config
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data', 'assets.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Required for flashing messages

# 2. Initialize the DB
db.init_app(app)

# 3. Create tables inside app context
with app.app_context():
    db.create_all()

# 4. Routes
@app.route('/')
def index():
    filters = {
        'asset_type': request.args.get('asset_type'),
        'assigned_to': request.args.get('assigned_to'),
        'department': request.args.get('department'),
        'vendor_name': request.args.get('vendor_name'),
        'project_name': request.args.get('project_name')
    }

    query = Asset.query
    for field, value in filters.items():
        if value:
            query = query.filter(getattr(Asset, field).ilike(f'%{value}%'))

    assets = query.all()
    return render_template('index.html', assets=assets, filters=filters)

@app.route('/add', methods=['GET', 'POST'])
def add_asset():
    if request.method == 'POST':
        try:
            asset = Asset(
                asset_type=request.form['asset_type'],
                brand=request.form['brand'],
                model_number=request.form['model_number'],
                serial_number=request.form['serial_number'],
                company_barcode=request.form['company_barcode'],
                assigned_to=request.form['assigned_to'],
                department=request.form['department'],
                given_date=datetime.strptime(request.form['given_date'], '%Y-%m-%d').date() if request.form['given_date'] else None,
                status=request.form['status'],
                return_date=datetime.strptime(request.form['return_date'], '%Y-%m-%d').date() if request.form['return_date'] else None,
                project_name=request.form['project_name'],
                purchase_date=datetime.strptime(request.form['purchase_date'], '%Y-%m-%d').date() if request.form['purchase_date'] else None,
                vendor_name=request.form['vendor_name'],
                system_details=request.form['system_details'],
                remarks=request.form['remarks']
            )
            db.session.add(asset)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            db.session.rollback()
            return f"Error adding asset: {e}", 500

    return render_template('add_asset.html')

@app.route('/edit/<int:asset_id>', methods=['GET', 'POST'])
def edit_asset(asset_id):
    asset = Asset.query.get_or_404(asset_id)
    if request.method == 'POST':
        asset.asset_type = request.form['asset_type']
        asset.brand = request.form['brand']
        asset.model_number = request.form['model_number']
        asset.serial_number = request.form['serial_number']
        asset.company_barcode = request.form['company_barcode']
        asset.assigned_to = request.form['assigned_to']
        asset.department = request.form['department']
        asset.given_date = datetime.strptime(request.form['given_date'], '%Y-%m-%d').date() if request.form['given_date'] else None
        asset.return_date = datetime.strptime(request.form['return_date'], '%Y-%m-%d').date() if request.form['return_date'] else None
        asset.purchase_date = datetime.strptime(request.form['purchase_date'], '%Y-%m-%d').date() if request.form['purchase_date'] else None
        asset.status = request.form['status']
        asset.project_name = request.form['project_name']
        asset.vendor_name = request.form['vendor_name']
        asset.system_details = request.form['system_details']
        asset.remarks = request.form['remarks']

        db.session.commit()
        return redirect('/')
    return render_template('edit_asset.html', asset=asset)

# @app.route('/bulk_action', methods=['POST'])
# def bulk_action():
#     selected_ids = request.form.getlist('selected_ids')
#     action = request.form.get('action')

#     if not selected_ids:
#         flash("No asset selected.", "warning")
#         return redirect(url_for('index'))

#     if action == 'delete':
#         for asset_id in selected_ids:
#             asset = Asset.query.get(asset_id)
#             if asset:
#                 db.session.delete(asset)
#         db.session.commit()
#         flash(f"Deleted {len(selected_ids)} asset(s).", "success")

#     elif action == 'edit':
#         if len(selected_ids) == 1:
#             return redirect(url_for('edit_asset', asset_id=selected_ids[0]))
#         else:
#             flash("You can only edit one asset at a time.", "warning")

#     return redirect(url_for('index'))



@app.route('/delete/<int:id>', methods=['POST'])
def delete_asset(id):
    asset = Asset.query.get_or_404(id)
    db.session.delete(asset)
    db.session.commit()
    flash('Asset deleted successfully.')
    return redirect(url_for('index'))

@app.route('/export')
def export():
    filepath = export_assets_to_excel()
    return send_file(filepath, as_attachment=True)

# 5. Run server if script is main
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
