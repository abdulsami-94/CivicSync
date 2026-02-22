from datetime import datetime, timedelta
from flask import Blueprint, render_template, url_for, flash, redirect, request
from app import db, bcrypt
from app.models import User, Complaint, ComplaintHistory
from flask_login import login_user, current_user, logout_user, login_required

auth = Blueprint('auth', __name__)

def check_escalations():
    """Utility function to auto-escalate complaints older than 3 days that are not resolved."""
    three_days_ago = datetime.utcnow() - timedelta(days=3)
    
    # Exclude Resolved and already Escalated
    pending_complaints = Complaint.query.filter(
        Complaint.status.not_in(['Resolved', 'Escalated']),
        Complaint.date_posted <= three_days_ago
    ).all()
    
    if not pending_complaints:
        return

    for c in pending_complaints:
        old_status = c.status
        c.status = 'Escalated'
        history = ComplaintHistory(complaint_id=c.id, old_status=old_status, 
                                   new_status='Escalated', notes='System auto-escalation (> 3 days).', 
                                   changed_by=None) # System change
        db.session.add(history)
    db.session.commit()

@auth.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('citizen.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'citizen') # Allow selecting role for demo purposes, normally restricted

        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Email already registered. Please login.', 'danger')
            return redirect(url_for('auth.register'))
            
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password, role=role)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register')

@auth.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'staff':
            return redirect(url_for('staff.dashboard'))
        else:
            return redirect(url_for('citizen.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=request.form.get('remember'))
            check_escalations() # Run escalation logic on every login
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'staff':
                return redirect(url_for('staff.dashboard'))
            else:
                return redirect(url_for('citizen.dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('auth/login.html', title='Login')

@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
