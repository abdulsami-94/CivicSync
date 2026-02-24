import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Basic security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database: Simple SQLite setup
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'campussync.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File uploads
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # No time limit on CSRF token
    WTF_CSRF_CHECK_DEFAULT = True

    # Session Configuration - Required for CSRF token validation
    SESSION_COOKIE_SECURE = False  # Set to True only in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours

    # Email domain restriction for ASM CSIT
    ALLOWED_EMAIL_DOMAIN = 'asmedu.org'

