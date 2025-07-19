from flask import Flask, render_template, request, redirect, send_file, flash, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import Asset
from export_excel import export_assets_to_excel
import os
from datetime import date, datetime
from functools import wraps
from models import User

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

# --- Decorators ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Login required", "warning")
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash("Admin access only", "danger")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---
@app.route('/')
@login_required
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    next_page = request.args.get('next')  # Get "next" URL if present
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        #      # ✅ Debugging output
        # print(f"Trying to log in as: {username}")
        # print(f"User found: {user.username if user else 'None'}")

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return redirect(next_page or url_for('index'))     # Redirect to original page or index
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/add', methods=['GET', 'POST'])
@admin_required
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
@admin_required
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

@app.route('/delete/<int:id>', methods=['POST'])
@admin_required
def delete_asset(id):
    asset = Asset.query.get_or_404(id)
    db.session.delete(asset)
    db.session.commit()
    flash('Asset deleted successfully.')
    return redirect(url_for('index'))

@app.route('/export')
@admin_required
def export():
    filepath = export_assets_to_excel()
    return send_file(filepath, as_attachment=True)


@app.route('/users')
@admin_required
def users():
    all_users = User.query.all()
    return render_template('users.html', users=all_users)

@app.route('/add_user', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'warning')
            return redirect(url_for('add_user'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash('User created successfully', 'success')
        return redirect(url_for('users'))

    return render_template('add_user.html')

@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.role = request.form['role']
        if request.form['password']:
            user.password = generate_password_hash(request.form['password'])
        db.session.commit()
        flash('User updated successfully.')
        return redirect(url_for('users'))
    return render_template('edit_user.html', user=user)


@app.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.username == 'admin':
        flash("Can't delete admin user.", 'warning')
        return redirect(url_for('users'))
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.')
    return redirect(url_for('users'))


@app.route('/reset_password/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def reset_password(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        new_password = request.form['new_password']
        user.password = generate_password_hash(new_password)
        db.session.commit()
        flash('Password updated successfully', 'success')
        return redirect(url_for('users'))
    return render_template('reset_password.html', user=user)


# 5. Run server if script is main
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
