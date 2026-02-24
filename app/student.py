import os
import uuid
from flask import Blueprint, render_template, url_for, flash, redirect, request, current_app, abort, send_from_directory
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app import db
from app.models import Complaint
from flask_paginate import Pagination, get_page_parameter
from functools import wraps

student = Blueprint('student', __name__)

def student_required(f):
    """Decorator to ensure only student users can access the route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def _allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config.get('ALLOWED_EXTENSIONS', set())

def save_picture(form_picture):
    """Save uploaded image with unique filename."""
    filename = secure_filename(form_picture.filename)
    if filename == '' or not _allowed_file(filename):
        return None
    _, f_ext = os.path.splitext(filename)
    unique_filename = str(uuid.uuid4()) + f_ext
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    picture_path = os.path.join(upload_folder, unique_filename)
    form_picture.save(picture_path)
    return unique_filename

@student.route("/")
@student.route("/dashboard")
@student_required
def dashboard():

    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10

    # Search functionality
    search = request.args.get('search', '')
    category_filter = request.args.get('category', '')

    query = Complaint.query.filter(Complaint.user_id == current_user.id, Complaint.is_deleted == False)

    if search:
        query = query.filter(Complaint.title.contains(search))
    if category_filter:
        query = query.filter(Complaint.category == category_filter)

    complaints = query.order_by(Complaint.date_posted.desc()).paginate(page=page, per_page=per_page, error_out=False)
    pagination = Pagination(page=page, total=complaints.total, per_page=per_page, css_framework='bootstrap5')

    return render_template('student/dashboard.html', title='My Complaints', complaints=complaints, pagination=pagination)

@student.route("/complaint/new", methods=['GET', 'POST'])
@student_required
def new_complaint():
    """Create a new complaint."""

    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        priority = request.form.get('priority')
        location = request.form.get('location')
        description = request.form.get('description')

        # Handle file upload
        picture_file = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                picture_file = save_picture(file)

        # Create complaint
        complaint = Complaint(title=title, category=category, priority=priority,
                              location=location, description=description,
                              image_file=picture_file, user_id=current_user.id)
        db.session.add(complaint)
        db.session.commit()

        flash('Your complaint has been registered!', 'success')
        return redirect(url_for('student.dashboard'))

    return render_template('student/new_complaint.html', title='Register Complaint')

@student.route("/complaint/<int:complaint_id>/edit", methods=['GET', 'POST'])
@student_required
def edit_complaint(complaint_id):
    """Edit complaint - only if status is Pending."""
    complaint = Complaint.query.get_or_404(complaint_id)

    if complaint.user_id != current_user.id or complaint.status != 'Pending' or complaint.is_deleted:
        abort(403)

    if request.method == 'POST':
        complaint.title = request.form.get('title')
        complaint.category = request.form.get('category')
        complaint.priority = request.form.get('priority')
        complaint.location = request.form.get('location')
        complaint.description = request.form.get('description')

        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                picture_file = save_picture(file)
                complaint.image_file = picture_file

        db.session.commit()
        flash('Your complaint has been updated!', 'success')
        return redirect(url_for('student.dashboard'))

    return render_template('student/edit_complaint.html', title='Edit Complaint', complaint=complaint)

@student.route("/complaint/<int:complaint_id>")
@student_required
def view_complaint(complaint_id):
    """View complaint details."""
    complaint = Complaint.query.get_or_404(complaint_id)

    if complaint.user_id != current_user.id or complaint.is_deleted:
        abort(403)

    return render_template('student/view_complaint.html', title=complaint.title, complaint=complaint)

@student.route("/uploads/<filename>")
@login_required
def uploaded_file(filename):
    """Serve uploaded files."""
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
