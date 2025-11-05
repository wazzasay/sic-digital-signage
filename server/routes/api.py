from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import uuid

from database import db
from models import Screen, Content, Playlist, PlaylistItem

bp = Blueprint('api', __name__, url_prefix='/api')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'mp4', 'avi', 'mov', 'webm', 'mkv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/screen/register', methods=['POST'])
def register_screen():
    """Register or update a screen client"""
    data = request.json
    identifier = data.get('identifier')
    name = data.get('name', f'Screen-{identifier[:8]}')
    location = data.get('location', '')

    if not identifier:
        return jsonify({'error': 'Identifier required'}), 400

    screen = Screen.query.filter_by(identifier=identifier).first()

    if screen:
        # Update existing screen
        screen.status = 'online'
        screen.last_seen = datetime.utcnow()
        if name:
            screen.name = name
        if location:
            screen.location = location
    else:
        # Create new screen
        screen = Screen(
            identifier=identifier,
            name=name,
            location=location,
            status='online',
            last_seen=datetime.utcnow()
        )
        db.session.add(screen)

    db.session.commit()

    return jsonify({
        'success': True,
        'screen': screen.to_dict()
    })

@bp.route('/screen/<identifier>/heartbeat', methods=['POST'])
def screen_heartbeat(identifier):
    """Update screen last seen timestamp"""
    screen = Screen.query.filter_by(identifier=identifier).first()

    if not screen:
        return jsonify({'error': 'Screen not found'}), 404

    screen.status = 'online'
    screen.last_seen = datetime.utcnow()
    db.session.commit()

    return jsonify({'success': True})

@bp.route('/screen/<identifier>/content', methods=['GET'])
def get_screen_content(identifier):
    """Get content assigned to a screen"""
    screen = Screen.query.filter_by(identifier=identifier).first()

    if not screen:
        return jsonify({'error': 'Screen not found'}), 404

    # Update last seen
    screen.last_seen = datetime.utcnow()
    screen.status = 'online'
    db.session.commit()

    if not screen.current_playlist_id:
        return jsonify({
            'playlist': None,
            'items': []
        })

    playlist = Playlist.query.get(screen.current_playlist_id)

    if not playlist:
        return jsonify({
            'playlist': None,
            'items': []
        })

    return jsonify({
        'playlist': playlist.to_dict(),
        'items': [item.to_dict() for item in playlist.items]
    })

@bp.route('/content/<int:content_id>/download', methods=['GET'])
def download_content(content_id):
    """Download content file"""
    content = Content.query.get(content_id)

    if not content:
        return jsonify({'error': 'Content not found'}), 404

    if content.content_type == 'webpage':
        return jsonify({'error': 'Webpages cannot be downloaded'}), 400

    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], content.file_path)

    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    return send_file(file_path, as_attachment=True)

@bp.route('/content/<int:content_id>/thumbnail', methods=['GET'])
def get_content_thumbnail(content_id):
    """Get content thumbnail/preview"""
    content = Content.query.get(content_id)

    if not content:
        return jsonify({'error': 'Content not found'}), 404

    if content.content_type == 'webpage':
        return jsonify({'error': 'Webpages have no thumbnail'}), 400

    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], content.file_path)

    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    # For images, serve directly (browser will resize via CSS)
    # For videos, we'd need thumbnail generation (future enhancement)
    if content.content_type == 'image':
        return send_file(file_path, mimetype=content.mime_type)
    else:
        # For videos, return placeholder for now
        return jsonify({'error': 'Video thumbnails not yet supported'}), 400

@bp.route('/upload', methods=['POST'])
def upload_content():
    """Upload content file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    # Generate unique filename
    original_filename = secure_filename(file.filename)
    extension = original_filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{extension}"

    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)

    # Save file with error handling
    try:
        file.save(file_path)
    except Exception as e:
        return jsonify({'error': f'Failed to save file: {str(e)}'}), 500

    try:
        # Determine content type
        if extension in {'png', 'jpg', 'jpeg', 'gif', 'bmp'}:
            content_type = 'image'
        elif extension in {'mp4', 'avi', 'mov', 'webm', 'mkv'}:
            content_type = 'video'
        else:
            content_type = 'unknown'

        # Get file size
        file_size = os.path.getsize(file_path)

        # Get content name and duration from form data
        # If no name provided, use filename without extension
        name_from_form = request.form.get('name', '').strip()
        if not name_from_form:
            # Remove extension from filename for default name
            name = original_filename.rsplit('.', 1)[0]
        else:
            name = name_from_form

        duration = int(request.form.get('duration', 10))

        # Create content entry
        content = Content(
            name=name,
            content_type=content_type,
            file_path=unique_filename,
            duration=duration,
            file_size=file_size,
            mime_type=file.content_type
        )

        db.session.add(content)
        db.session.commit()

        return jsonify({
            'success': True,
            'content': content.to_dict()
        })

    except Exception as e:
        # Rollback database and cleanup file on error
        db.session.rollback()
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        return jsonify({'error': f'Failed to create content: {str(e)}'}), 500

@bp.route('/content', methods=['GET'])
def list_content():
    """List all content"""
    content_list = Content.query.order_by(Content.created_at.desc()).all()
    return jsonify({
        'content': [c.to_dict() for c in content_list]
    })

@bp.route('/screens', methods=['GET'])
def list_screens():
    """List all screens"""
    screens = Screen.query.order_by(Screen.created_at.desc()).all()
    return jsonify({
        'screens': [s.to_dict() for s in screens]
    })

@bp.route('/playlist/<int:playlist_id>', methods=['GET'])
def get_playlist(playlist_id):
    """Get playlist details with items"""
    playlist = Playlist.query.get(playlist_id)

    if not playlist:
        return jsonify({'error': 'Playlist not found'}), 404

    return jsonify(playlist.to_dict())
