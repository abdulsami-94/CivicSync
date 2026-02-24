# CampusSync Deployment Guide

## Quick Summary of Fix

The deployment error was: **gunicorn: command not found**

### Solution
Added `gunicorn==22.0.0` to `requirements.txt`

## Deployment Instructions

### Prerequisites
- Python 3.9+
- pip package manager

### Step-by-Step Deployment

#### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd CampusSync
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 3. Set Environment Variables
```bash
export SECRET_KEY="your-production-secret-key"
export FLASK_ENV="production"
```

#### 4. Initialize Database
```bash
python seed_db.py
```

#### 5. Run with Gunicorn (Production)
```bash
gunicorn --workers 1 --bind 0.0.0.0:8000 run:app
```

Or with multiple workers:
```bash
gunicorn --workers 4 --bind 0.0.0.0:8000 run:app
```

### For Render.com Deployment

The deployment command in Render should be:
```
gunicorn run:app
```

This will work now that `gunicorn` is in `requirements.txt`.

### Environment Variables to Set in Render
- `SECRET_KEY`: Your production secret key
- `FLASK_ENV`: `production`

### Database

The application uses SQLite by default. In production:
- Database file: `instance/campussync.db` (created automatically)
- Tables are created on app startup
- Demo users are seeded if needed

### Files Changed

1. **requirements.txt** - Added `gunicorn==22.0.0`
2. **run.py** - Modified to create app instance at module level (required for Gunicorn)
3. **README.md** - Added deployment instructions

### Troubleshooting

If you still see "gunicorn: command not found":
1. Ensure you're using the correct Python environment
2. Try: `python3 -m pip install gunicorn==22.0.0`
3. Verify: `python3 -c "import gunicorn; print(gunicorn.__version__)"`

### Testing Locally

Test with Gunicorn before deploying:
```bash
gunicorn --workers 1 --bind 0.0.0.0:5000 run:app
```
Then visit http://localhost:5000

### Production Security Recommendations

1. **SECRET_KEY**: Use a strong, random value
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Email Configuration**: Update `config.py` for production email
3. **HTTPS**: Enable SSL/TLS at the reverse proxy level
4. **Database**: Consider PostgreSQL for production instead of SQLite
5. **File Uploads**: Ensure `uploads/` directory has proper permissions

### Next Steps

1. Push the updated code to your repository
2. Redeploy on Render.com
3. The deployment should succeed with `gunicorn run:app`
