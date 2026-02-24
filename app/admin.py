from flask import Blueprint, render_template, url_for, flash, redirect, request, abort, jsonify
from flask_login import current_user, login_required
from app import db
from app.models import Complaint, User
from functools import wraps
from sqlalchemy import func
from flask_paginate import Pagination, get_page_parameter
from datetime import datetime
import json

admin = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to ensure only admin users can access the route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route("/")
@admin.route("/dashboard")
@admin_required
def dashboard():
    """Admin dashboard - view all complaints with filtering and assignment."""
    # Filtering
    status_filter = request.args.get('status')
    category_filter = request.args.get('category')
    search = request.args.get('search', '')

    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10

    query = Complaint.query.filter(Complaint.is_deleted == False)

    if status_filter:
        query = query.filter_by(status=status_filter)
    if category_filter:
        query = query.filter_by(category=category_filter)
    if search:
        query = query.filter(Complaint.title.contains(search))

    complaints = query.order_by(Complaint.date_posted.desc()).paginate(page=page, per_page=per_page, error_out=False)
    pagination = Pagination(page=page, total=complaints.total, per_page=per_page, css_framework='bootstrap5')

    # Get staff members for assignment dropdown
    staff_members = User.query.filter_by(role='staff').all()

    # Analytics - Status breakdown
    total_complaints = Complaint.query.filter(Complaint.is_deleted == False).count()
    pending_count = Complaint.query.filter(Complaint.status == 'Pending', Complaint.is_deleted == False).count()
    in_progress_count = Complaint.query.filter(Complaint.status == 'In Progress', Complaint.is_deleted == False).count()
    resolved_count = Complaint.query.filter(Complaint.status == 'Resolved', Complaint.is_deleted == False).count()

    # Analytics - Category breakdown
    category_data = db.session.query(
        Complaint.category,
        func.count(Complaint.id).label('count')
    ).filter(Complaint.is_deleted == False).group_by(Complaint.category).all()

    # Convert to JSON-safe dict for Chart.js
    status_counts = {
        "Pending": pending_count,
        "In Progress": in_progress_count,
        "Resolved": resolved_count
    }

    category_counts = {item[0]: item[1] for item in category_data}

    # Convert to JSON strings for template
    status_counts_json = json.dumps(status_counts)
    category_counts_json = json.dumps(category_counts)

    return render_template('admin/dashboard.html', title='Admin Dashboard',
                           complaints=complaints, staff_members=staff_members,
                           pagination=pagination, total_complaints=total_complaints,
                           pending_count=pending_count, in_progress_count=in_progress_count,
                           resolved_count=resolved_count,
                           status_counts_json=status_counts_json,
                           category_counts_json=category_counts_json)

@admin.route("/assign/<int:complaint_id>", methods=['POST'])
@admin_required
def assign_staff(complaint_id):
    """Assign complaint to a staff member."""
    complaint = Complaint.query.get_or_404(complaint_id)

    if complaint.is_deleted:
        abort(404)

    staff_id = request.form.get('staff_id')

    if staff_id:
        staff_user = User.query.get(int(staff_id))
        if not staff_user or staff_user.role != 'staff':
            flash('Invalid staff selected.', 'danger')
            return redirect(url_for('admin.dashboard'))

        if complaint.assigned_to:
            flash('Complaint is already assigned.', 'danger')
            return redirect(url_for('admin.dashboard'))

        complaint.assigned_to = staff_user.id
        complaint.status = 'In Progress'
        db.session.commit()

        flash(f'Complaint assigned to {staff_user.username} successfully!', 'success')

    return redirect(url_for('admin.dashboard'))

@admin.route("/delete/<int:complaint_id>", methods=['POST'])
@admin_required
def delete_complaint(complaint_id):
    """Soft delete a complaint."""
    complaint = Complaint.query.get_or_404(complaint_id)

    if complaint.is_deleted:
        abort(404)

    confirm = request.form.get('confirm', 'no')
    if confirm != 'yes':
        flash('Deletion not confirmed.', 'warning')
        return redirect(url_for('admin.dashboard'))

    complaint.is_deleted = True
    db.session.commit()

    flash('Complaint deleted successfully!', 'success')
    return redirect(url_for('admin.dashboard'))
