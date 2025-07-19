from werkzeug.security import generate_password_hash
from extensions import db
from models import User
from app import app

with app.app_context():
    db.create_all()  # Ensure all tables exist

    # Change username and password as needed
    username = 'admin'
    password = 'admin123'
    role = 'admin'

    if User.query.filter_by(username=username).first():
        print("Admin user already exists.")
    else:
        hashed_password = generate_password_hash(password)
        admin_user = User(username=username, password=hashed_password, role=role)
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created successfully.")
