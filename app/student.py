import os
import secrets
from flask import Blueprint, render_template, url_for, flash, redirect, request, current_app, abort
from flask_login import current_user, login_required
from app import db
from app.models import Complaint, ComplaintHistory
from werkzeug.utils import secure_filename

student = Blueprint('student', __name__)

def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config.get('ALLOWED_EXTENSIONS', set())

def save_picture(form_picture):
    filename = secure_filename(form_picture.filename)
    if filename == '' or not _allowed_file(filename):
        return None
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(filename)
    picture_fn = random_hex + f_ext
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    picture_path = os.path.join(upload_folder, picture_fn)
    form_picture.save(picture_path)
    return picture_fn

@student.route("/")
@student.route("/dashboard")
@login_required
def dashboard():
    if current_user.role != 'student':
        return redirect(url_for('auth.login'))
    complaints = Complaint.query.filter(Complaint.user_id == current_user.id).order_by(Complaint.date_posted.desc()).all()
    return render_template('student/dashboard.html', title='My Complaints', complaints=complaints)

@student.route("/complaint/new", methods=['GET', 'POST'])
@login_required
def new_complaint():
    if current_user.role != 'student':
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        priority = request.form.get('priority')
        location = request.form.get('location')
        description = request.form.get('description')
        
        picture_file = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                picture_file = save_picture(file)

        complaint = Complaint(title=title, category=category, priority=priority, 
                              location=location, description=description, 
                              image_file=picture_file, author=current_user)
        db.session.add(complaint)
        db.session.commit()
        
        # Add initial history
        history = ComplaintHistory(complaint_id=complaint.id, old_status='Created', new_status='Pending', changed_by=current_user.id)
        db.session.add(history)
        db.session.commit()

        flash('Your complaint has been registered!', 'success')
        return redirect(url_for('student.dashboard'))
        
    return render_template('student/new_complaint.html', title='Register Complaint')

@student.route("/complaint/<int:complaint_id>/edit", methods=['GET', 'POST'])
@login_required
def edit_complaint(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    if complaint.author != current_user:
        abort(403)
    if complaint.status != 'Pending':
        flash('Only pending complaints can be edited.', 'danger')
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        complaint.title = request.form.get('title')
        complaint.category = request.form.get('category')
        complaint.priority = request.form.get('priority')
        complaint.location = request.form.get('location')
        complaint.description = request.form.get('description')
        
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
@login_required
def view_complaint(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    if complaint.author != current_user and current_user.role == 'student':
        abort(403)
    return render_template('student/view_complaint.html', title=complaint.title, complaint=complaint)
