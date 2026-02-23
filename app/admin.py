import csv
from io import StringIO
from flask import Blueprint, render_template, url_for, flash, redirect, request, Response
from flask_login import current_user, login_required
from app import db
from app.models import Complaint, User, ComplaintHistory
from functools import wraps
from sqlalchemy import func

admin = Blueprint('admin', __name__)

def admin_required(f):
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
    # Filtering Logic
    status_filter = request.args.get('status')
    category_filter = request.args.get('category')
    
    query = Complaint.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if category_filter:
        query = query.filter_by(category=category_filter)
        
    complaints = query.order_by(Complaint.date_posted.desc()).all()
    
    # Staff members for assignment
    staff_members = User.query.filter_by(role='staff').all()

    # Analytics Data
    # 1. Category Breakdown (Pie Chart)
    category_counts = db.session.query(Complaint.category, func.count(Complaint.id)).group_by(Complaint.category).all()
    categories = [row[0] for row in category_counts]
    cat_counts = [row[1] for row in category_counts]

    # 2. Status Breakdown (Bar Chart)
    status_counts = db.session.query(Complaint.status, func.count(Complaint.id)).group_by(Complaint.status).all()
    statuses = [row[0] for row in status_counts]
    stat_counts = [row[1] for row in status_counts]
    
    # 3. Staff Performance Report
    # Query: For complaints with a resolved_at timestamp, calculate count and avg difference
    # We use SQLite compatible timestamp difference: (julianday(resolved_at) - julianday(date_posted))
    performance_data = db.session.query(
        User.username,
        func.count(Complaint.id).label('resolved_count'),
        func.avg(
            db.cast(
                func.julianday(Complaint.resolved_at) - func.julianday(Complaint.date_posted),
                db.Float
            )
        ).label('avg_days')
    ).join(Complaint, User.id == Complaint.assigned_to)\
     .filter(Complaint.status == 'Resolved', Complaint.resolved_at.isnot(None))\
     .group_by(User.id).all()

    return render_template('admin/dashboard.html', title='Admin Dashboard', 
                           complaints=complaints, staff_members=staff_members,
                           categories=categories, cat_counts=cat_counts,
                           statuses=statuses, stat_counts=stat_counts,
                           performance_data=performance_data)

@admin.route("/assign/<int:complaint_id>", methods=['POST'])
@admin_required
def assign_staff(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    staff_id = request.form.get('staff_id')
    
    if staff_id:
        staff_user = User.query.get(int(staff_id))
        if not staff_user or staff_user.role != 'staff':
            flash('Invalid staff selected.', 'danger')
            return redirect(url_for('admin.dashboard'))

        complaint.assigned_to = staff_user.id
        old_status = complaint.status
        complaint.status = 'In Progress' # Usually assignment means it's now in progress

        history = ComplaintHistory(complaint_id=complaint.id, old_status=old_status, 
                                   new_status='In Progress', notes=f'Assigned to staff {staff_user.username}', 
                                   changed_by=current_user.id)

        db.session.add(history)
        db.session.commit()
        flash('Complaint assigned successfully!', 'success')
        
    return redirect(url_for('admin.dashboard'))

@admin.route("/export")
@admin_required
def export_csv():
    complaints = Complaint.query.order_by(Complaint.date_posted.desc()).all()
    
    def generate():
        data = StringIO()
        writer = csv.writer(data)
        
        # Write header
        writer.writerow(['ID', 'Title', 'Category', 'Priority', 'Status', 'Location', 'Date Posted', 'Registered By', 'Assigned Staff'])
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)

        # Write data rows
        for c in complaints:
            staff_name = c.assignee.username if c.assignee else 'Unassigned'
            writer.writerow([c.id, c.title, c.category, c.priority, c.status, c.location, 
                             c.date_posted.strftime('%Y-%m-%d %H:%M'), c.author.username, staff_name])
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)

    return Response(generate(), mimetype='text/csv', headers={"Content-Disposition": "attachment; filename=complaints_report.csv"})
