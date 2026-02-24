from app import create_app, db

app = create_app()

# Create database tables on startup
with app.app_context():
    db.create_all()
    print('Database tables created.')

if __name__ == '__main__':
    # Development server
    app.run(debug=True, port=8000)
