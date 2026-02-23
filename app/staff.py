from datetime import datetime, timedelta
from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import current_user, login_required
from app import db
from app.models import Complaint, ComplaintHistory
from functools import wraps

staff = Blueprint('staff', __name__)

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'staff':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@staff.route("/")
@staff.route("/dashboard")
@staff_required
def dashboard():
    # View assigned complaints
    complaints = Complaint.query.filter(Complaint.assigned_to == current_user.id).order_by(Complaint.date_posted.desc()).all()
    return render_template('staff/dashboard.html', title='Staff Tasks', complaints=complaints)

@staff.route("/update/<int:complaint_id>", methods=['GET', 'POST'])
@staff_required
def update_complaint(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    if complaint.assigned_to != current_user.id:
        flash('You can only update complaints assigned to you.', 'danger')
        return redirect(url_for('staff.dashboard'))

    if request.method == 'POST':
        new_status = request.form.get('status')
        notes = request.form.get('notes')
        
        if new_status and new_status != complaint.status:
            old_status = complaint.status
            complaint.status = new_status
            
            # Automatically set resolved_at timestamp when status becomes Resolved
            if new_status == 'Resolved':
                complaint.resolved_at = datetime.utcnow()
            
            history = ComplaintHistory(complaint_id=complaint.id, old_status=old_status, 
                                       new_status=new_status, notes=notes, 
                                       changed_by=current_user.id)
            db.session.add(history)
            db.session.commit()
            
            flash('Complaint updated successfully!', 'success')
            return redirect(url_for('staff.dashboard'))

    return render_template('staff/update_complaint.html', title='Update Task', complaint=complaint)
