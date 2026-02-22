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
    admin_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
    admin_user = User(username='admin', email='admin@civicsync.com', password=admin_pw, role='admin')
    
    staff_pw = bcrypt.generate_password_hash('staff123').decode('utf-8')
    staff1 = User(username='staff_john', email='john.staff@civicsync.com', password=staff_pw, role='staff')
    staff2 = User(username='staff_jane', email='jane.staff@civicsync.com', password=staff_pw, role='staff')

    citizen_pw = bcrypt.generate_password_hash('citizen123').decode('utf-8')
    citizen1 = User(username='citizen_alice', email='alice@example.com', password=citizen_pw, role='citizen')
    citizen2 = User(username='citizen_bob', email='bob@example.com', password=citizen_pw, role='citizen')

    db.session.add_all([admin_user, staff1, staff2, citizen1, citizen2])
    db.session.commit()
    print("Created sample users (Admin, Staff, Citizens).")

    # Sample categories and locations
    categories = ['Roads & Streets', 'Water Supply', 'Electricity', 'Sanitation & Garbage', 'Public Transport']
    locations = ['Main Street, Area 1', 'North Avenue, Area 2', 'West End, Area 3', 'East Side, Area 4', 'South Park, Area 5']

    # Create dummy complaints
    for i in range(15):
        category = random.choice(categories)
        location = random.choice(locations)
        priority = random.choice(['Low', 'Medium', 'High'])
        author = random.choice([citizen1, citizen2])
        status = random.choice(['Pending', 'In Progress', 'Resolved'])
        
        # Simulate different dates (from 1 to 10 days ago)
        days_ago = random.randint(1, 10)
        date_posted = datetime.utcnow() - timedelta(days=days_ago)

        complaint = Complaint(
            title=f'Issue with {category} in {location.split(",")[1].strip()}',
            category=category,
            priority=priority,
            location=location,
            description=f'This is a sample complaint regarding {category.lower()}... please resolve it as soon as possible.',
            date_posted=date_posted,
            status=status,
            author=author
        )
        
        # Assign staff if in progress or resolved
        if status in ['In Progress', 'Resolved']:
            complaint.assigned_to = random.choice([staff1, staff2]).id
            
        if status == 'Resolved':
            complaint.resolved_at = date_posted + timedelta(days=random.randint(1, 4))

        db.session.add(complaint)
        db.session.commit()

        # Add history record
        history = ComplaintHistory(
            complaint_id=complaint.id,
            date_changed=date_posted,
            old_status='Created',
            new_status=status,
            changed_by=author.id
        )
        db.session.add(history)
        db.session.commit()

    print("Created 15 sample complaints with varied statuses and dates.")
    print("Database seeding completed successfully.")
