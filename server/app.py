from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://signage:signage@localhost/digital_signage')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
from database import db
db.init_app(app)

CORS(app)

# Import models and routes after db initialization
from models import User, Screen, Content, Playlist, PlaylistItem
from routes import api, admin

# Register blueprints
app.register_blueprint(api.bp)
app.register_blueprint(admin.bp)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('admin.login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create default admin user if none exists
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                email='admin@example.com'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created - username: admin, password: admin123")

    app.run(host='0.0.0.0', port=5000, debug=True)
