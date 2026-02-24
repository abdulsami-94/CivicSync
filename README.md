# CampusSync - College Complaint Management System

A Flask-based web application for managing student complaints in educational institutions, specifically designed for ASM CSIT college viva presentation.

## Features

- **Role-based Access Control**: Three user roles - Admin, Staff, and Student
- **Complaint Workflow**: Submit → Assign → Resolve complaint lifecycle
- **Email Domain Restriction**: Only @asmedu.org emails allowed for ASM CSIT branding
- **Soft Delete**: Admin can delete complaints without permanent data loss
- **File Uploads**: Support for complaint evidence attachments
- **Responsive UI**: Bootstrap-based modern interface
- **Production Ready**: Includes gunicorn for deployment

## Technology Stack

- **Backend**: Flask 3.0, SQLAlchemy, SQLite
- **Authentication**: Flask-Login, Flask-Bcrypt
- **Forms**: Flask-WTF with CSRF protection
- **Frontend**: Bootstrap 5, HTML5
- **File Handling**: UUID-based secure uploads
- **WSGI Server**: Gunicorn 22.0.0 (production)

## Installation & Setup

### Prerequisites
- Python 3.9+
- pip package manager

### Quick Start

1. **Clone and navigate to the project**:
   ```bash
   cd CampusSync
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**:
   ```bash
   python seed_db.py
   ```

4. **Run the application**:
   ```bash
   python run.py
   ```

5. **Access the application**:
   - Open http://localhost:8000 in your browser
   - Login with demo credentials (see below)

## Deployment

### Local Development
```bash
python run.py
```
The app runs on http://localhost:8000

### Production Deployment (Gunicorn)
```bash
gunicorn run:app
```
Or with specific settings:
```bash
gunicorn --workers 4 --bind 0.0.0.0:8000 run:app
```

### Environment Variables for Production
```bash
export SECRET_KEY="your-production-secret-key"
export FLASK_ENV="production"
```

## Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@asmedu.org | admin123 |
| Staff | it.support@asmedu.org | staff123 |
| Student | alice.cs@asmedu.org | student123 |

## User Roles & Permissions

### Student
- Register new complaints with category, priority, location, and description
- Upload evidence files
- View and edit pending complaints
- Track complaint status

### Staff
- View assigned complaints
- Update complaint status (In Progress → Resolved)
- Access complaint details and evidence

### Admin
- View all complaints with filtering
- Assign complaints to staff members
- Soft delete complaints
- Manage user roles (view-only in demo)

## Complaint Categories

- Roads & Streets
- Water Supply
- Electricity
- Sanitation & Garbage
- Public Transport
- Other

## Complaint Status Workflow

1. **Pending**: New complaint submitted by student
2. **In Progress**: Assigned to staff member
3. **Resolved**: Completed by staff

## Project Structure

```
CampusSync/
├── app/
│   ├── __init__.py          # Flask application factory
│   ├── models.py            # Database models (User, Complaint)
│   ├── auth.py              # Authentication blueprint
│   ├── student.py           # Student dashboard blueprint
│   ├── admin.py             # Admin dashboard blueprint
│   ├── staff.py             # Staff dashboard blueprint
│   ├── static/              # CSS, JS, uploaded files
│   └── templates/           # Jinja2 templates
├── config.py                # Application configuration
├── run.py                   # Development server entry point
├── seed_db.py               # Database initialization script
└── requirements.txt         # Python dependencies
```

## Key Features Demonstrated

- **Flask Application Factory Pattern**: Modular, scalable architecture
- **SQLAlchemy ORM**: Database abstraction and relationships
- **Blueprint Organization**: Clean separation of concerns
- **Form Validation**: WTForms with CSRF protection
- **File Upload Security**: UUID naming, type validation
- **Role-based Permissions**: Flask-Login integration
- **Responsive Design**: Bootstrap framework
- **Soft Delete Pattern**: Data integrity preservation

## Development Notes

- Uses SQLite for simplicity (easily replaceable with PostgreSQL for production)
- Email domain validation ensures ASM CSIT branding
- CSRF protection on all forms
- Session-based authentication
- Error handling with custom 403/404/500 pages

## For Viva Presentation

This application demonstrates:
- Full-stack web development with Flask
- Database design and ORM usage
- User authentication and authorization
- File handling and security
- Modern web development practices
- Clean, maintainable code architecture

## License

This project is developed for educational purposes as part of ASM CSIT college curriculum.
   * Links to the `User` model via `author_id` and an optional `assigned_to` key.

3. **ComplaintHistory Model:**
   * Acts as an immutable ledger.
   * Records every state change against a `complaint_id`, detailing the `old_status`, `new_status`, timestamp, and the actor responsible, ensuring compliance and analytical capability.

## 7. Installation Steps (Local Environment)

### Prerequisites
* Python 3.11 or higher
* `pip` (Python package installer)

### Setup Instructions
1. **Clone the Repository:**
   ```bash
   git clone <repository_url>
   cd CampusSync
   ```

2. **Initialise Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration:**
   Create a `.env` file in the root directory and populate it with local testing variables:
   ```env
   SECRET_KEY=local_development_key
   MAIL_SERVER=smtp.example.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your_email@example.com
   MAIL_PASSWORD=your_app_password
   ```

5. **Initialise Database & Seed Default Data:**
   ```bash
   python seed_db.py
   ```

6. **Execute Application:**
   ```bash
   export FLASK_APP=run.py
   export FLASK_DEBUG=1
   flask run --port=5000
   ```

## 8. Deployment Steps (Render Platform)
1. Ensure the repository contains a valid `requirements.txt` and `runtime.txt` (specifying e.g., `python-3.11.6`).
2. Verify the `Procfile` exists or configure Render's Start Command precisely as `gunicorn run:app`.
3. Connect the GitHub repository to a new Render Web Service instance.
4. Define Environment Variables within the Render dashboard:
   * `SECRET_KEY` (Cryptographically secure random string)
   * `DATABASE_URL` (Internal PostgreSQL connection string provided by Render)
   * `MAIL_*` configurations for SMTP access.
5. Deploy the application.

## 9. How Role-Based Access Works
The system implements strict access controls using `Flask-Login` decorators combined with custom role verification functions. When a resource is requested (e.g., the Admin Dashboard), the routing controller verifies the authenticated session via `@login_required` and subsequently evaluates the `current_user.role` attribute. Attempting lateral privilege escalation (e.g., a student requesting the staff dashboard) results in an HTTP 403 Forbidden abort or an immediate redirection to the authentication gateway.

## 10. How Duplicate Filtering Works
To mitigate database bloat and redundant maintenance requests, the submission controller executes a pre-insertion validation query. Upon receiving a POST request for a new issue, the ORM queries the `Complaint` table for existing records matching the exact structural combination of the incoming `title` and `location` parameters, filtered further to exclude records where the status is currently 'Resolved'. If a match is flagged, the transaction is halted, and the user receives a warning notification.

## 11. How Email Notification Works
When a staff member or administrator updates a complaint's status to 'Resolved', the controller invokes `Flask-Mail` modules. The application dynamically constructs an email payload referencing the original `Complaint.author.email`, the `Complaint.title`, and the time of resolution. This packet is transferred securely over TLS via the SMTP credentials provided securely defined in the host's environment variables.

## 12. Folder Structure Explanation
```text
CampusSync/
├── app/
│   ├── templates/          # Jinja2 HTML View templates separated by role
│   ├── static/             # Static assets (CSS, JS, Uploaded context images)
│   ├── __init__.py         # Application factory pattern and extension initialisation
│   ├── models.py           # SQLAlchemy database schema declarations
│   ├── auth.py             # User registration and session controllers
│   ├── student.py          # Student interface routing
│   ├── staff.py            # Maintenance staff interface routing
│   └── admin.py            # Administrative oversight routing
├── instance/               # Local SQLite database housing
├── config.py               # Centralised configuration parsing
├── run.py                  # WSGI entry point execution script
├── seed_db.py              # Automated database population script
├── requirements.txt        # Verified production and development dependencies
└── runtime.txt             # PaaS Python version specification
```

## 13. Future Enhancements
* **Machine Learning Categorisation:** Implement NLP models to auto-categorise issue descriptions, reducing human filing errors.
* **Geospatial Mapping:** Integrate a campus map API to allow precise pin-drop reporting of external infrastructure faults.
* **Service Level Agreement (SLA) Tracking:** Introduce timers that trigger automatic escalations to the Dean/Administration if high-priority infrastructure remains unresolved within 48 hours.
* **Mobile Application Deployment:** Encapsulate the web views into a reactive native container for iOS and Android platforms via progressive web application (PWA) standards.

## 14. Conclusion
CampusSync demonstrates a practical application of modern web development frameworks to solve real-world institutional logistics. By enforcing strict data integrity, securing session states, and structuring code maintainability through the MVC pattern, this application serves as a robust proof-of-concept for enterprise-grade campus management software.
