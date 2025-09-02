import os
import sys
from pathlib import Path
from flask import Flask
from flask_cors import CORS

# Add project root to Python path (needed for imports to work)
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

from src.models.user import db
from src.routes.user import user_bp
from src.routes.events import events_bp
from src.routes.bookings import bookings_bp
from src.routes.memberships import memberships_bp

# Import models to ensure they are registered with SQLAlchemy
from src.models.event import Event
from src.models.booking import Booking
from src.models.lounge import Lounge
from src.models.membership import MembershipTier, Membership

app = Flask(__name__)

# Configure a secret key from environment variables for production
# Fallback to a development key if not available
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-development-secret-key')

# Enable CORS for all routes
CORS(app, origins='*')

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(events_bp, url_prefix='/api')
app.register_blueprint(bookings_bp, url_prefix='/api')
app.register_blueprint(memberships_bp, url_prefix='/api')

# Database configuration
# For local development, use SQLite database
# For production (Vercel), use environment variable
if os.environ.get('SQLALCHEMY_DATABASE_URI'):
    # Production database (from environment)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
else:
    # Local development database
    db_path = project_root / 'src' / 'database' / 'app.db'
    db_path.parent.mkdir(parents=True, exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create tables
with app.app_context():
    try:
        db.create_all()
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {e}")

# Add a simple health check route
@app.route('/api/health')
def health_check():
    return {'status': 'healthy', 'message': 'API is running'}, 200

@app.route('/')
def home():
    return {'message': 'Elevate Events Backend API', 'status': 'running'}, 200

# For local development only
# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5001)