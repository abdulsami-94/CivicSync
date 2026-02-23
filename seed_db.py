import os
from datetime import datetime, timedelta
import random

from app import create_app, db, bcrypt
from app.models import User, Complaint, ComplaintHistory
from config import Config

# Ensure instance folder exists
os.makedirs(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance'), exist_ok=True)
os.makedirs(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app', 'static', 'uploads'), exist_ok=True)

app = create_app()

with app.app_context():
    # Create tables
    db.drop_all()
    db.create_all()

    print("Created database tables.")

    # Create users
    admin_pw = bcrypt.generate_password_hash('CampusAdmin@2026').decode('utf-8')
    admin_user = User(username='campus_admin', email='admin@campus.edu', password=admin_pw, role='admin')
    
    staff_pw = bcrypt.generate_password_hash('Maintenance@2026').decode('utf-8')
    staff1 = User(username='tech_support', email='it.support@campus.edu', password=staff_pw, role='staff')
    staff2 = User(username='estate_office', email='maintenance@campus.edu', password=staff_pw, role='staff')

    student_pw = bcrypt.generate_password_hash('Student@2026').decode('utf-8')
    student1 = User(username='student_alice', email='alice.cs@student.campus.edu', password=student_pw, role='student')
    student2 = User(username='student_bob', email='bob.ee@student.campus.edu', password=student_pw, role='student')

    db.session.add_all([admin_user, staff1, staff2, student1, student2])
    db.session.commit()
    print("Created sample users (Admin, Staff, Students).")
    print("Database seeding completed successfully.")
