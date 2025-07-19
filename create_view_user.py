# create_view_user.py
from app import app
from werkzeug.security import generate_password_hash
import sqlite3
import os

db_path = os.path.join(app.root_path, 'data', 'assets.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the user
username = 'htic'
password = 'htic@123'
role = 'viewer'

hashed_password = generate_password_hash(password)

cursor.execute("INSERT INTO user (username, password, role) VALUES (?, ?, ?)", (username, hashed_password, role))
conn.commit()
conn.close()
print("User added successfully.")
