from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='citizen') # 'citizen', 'admin', 'staff'
    complaints = db.relationship('Complaint', backref='author', lazy=True, foreign_keys='Complaint.user_id')
    assigned_complaints = db.relationship('Complaint', backref='assignee', lazy=True, foreign_keys='Complaint.assigned_to')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.role}')"

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True) # e.g. Roads, Water, Electricity, Sanitation
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), nullable=False, default='Low') # Low, Medium, High
    location = db.Column(db.String(100), nullable=False)
    image_file = db.Column(db.String(100), nullable=True) # Assuming file path is stored here
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    status = db.Column(db.String(20), nullable=False, default='Pending', index=True) # Pending, Assigned, In Progress, Resolved, Escalated
    resolved_at = db.Column(db.DateTime, nullable=True) # Track when resolved
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Staff ID
    history = db.relationship('ComplaintHistory', backref='complaint', lazy=True, cascade='all, delete-orphan')

    @property
    def resolution_time_days(self):
        if self.resolved_at and self.date_posted:
            delta = self.resolved_at - self.date_posted
            return delta.days
        return None

    def __repr__(self):
        return f"Complaint('{self.title}', '{self.date_posted}', '{self.status}')"

class ComplaintHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=False)
    date_changed = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    old_status = db.Column(db.String(20), nullable=False)
    new_status = db.Column(db.String(20), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    changed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # User ID who made the change

    def __repr__(self):
        return f"History(Complaint='{self.complaint_id}', Status changed to '{self.new_status}')"
