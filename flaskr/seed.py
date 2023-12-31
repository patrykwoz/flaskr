from flaskr import create_app
from flaskr.models import db, Post, User

# Create an application instance
app = create_app()

# Initialize the database
with app.app_context():
    # Drop all tables (if they exist)
    db.drop_all()
    # Create all tables
    db.create_all()

print("Database tables have been dropped and created.")
