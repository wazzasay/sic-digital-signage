from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

from database import db
from models import User, Screen, Content, Playlist, PlaylistItem

bp = Blueprint('admin', __name__, url_prefix='/admin')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json if request.is_json else request.form
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username

            if request.is_json:
                return jsonify({'success': True, 'redirect': url_for('admin.dashboard')})
            return redirect(url_for('admin.dashboard'))

        if request.is_json:
            return jsonify({'error': 'Invalid credentials'}), 401
        return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin.login'))

@bp.route('/dashboard')
@login_required
def dashboard():
    screens = Screen.query.all()
    content_count = Content.query.count()
    playlist_count = Playlist.query.count()

    return render_template('dashboard.html',
                         screens=screens,
                         content_count=content_count,
                         playlist_count=playlist_count)

@bp.route('/content')
@login_required
def content_page():
    content_list = Content.query.order_by(Content.created_at.desc()).all()
    return render_template('content.html', content_list=content_list)

@bp.route('/content/<int:content_id>/edit', methods=['POST'])
@login_required
def edit_content(content_id):
    content = Content.query.get(content_id)
    if not content:
        return jsonify({'error': 'Content not found'}), 404

    data = request.json
    name = data.get('name')
    duration = data.get('duration')
    display_mode = data.get('display_mode')

    if name:
        content.name = name
    if duration:
        content.duration = int(duration)
    if display_mode and display_mode in ['fit', 'fill']:
        content.display_mode = display_mode

    db.session.commit()
    return jsonify({'success': True})

@bp.route('/content/<int:content_id>/delete', methods=['POST'])
@login_required
def delete_content(content_id):
    content = Content.query.get(content_id)
    if content:
        # Remove from playlists
        PlaylistItem.query.filter_by(content_id=content_id).delete()
        db.session.delete(content)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'Content not found'}), 404

@bp.route('/screens')
@login_required
def screens_page():
    screens = Screen.query.order_by(Screen.created_at.desc()).all()
    playlists = Playlist.query.all()
    return render_template('screens.html', screens=screens, playlists=playlists)

@bp.route('/screen/<int:screen_id>/assign', methods=['POST'])
@login_required
def assign_playlist(screen_id):
    data = request.json
    playlist_id = data.get('playlist_id')

    screen = Screen.query.get(screen_id)
    if not screen:
        return jsonify({'error': 'Screen not found'}), 404

    screen.current_playlist_id = playlist_id
    db.session.commit()

    return jsonify({'success': True})

@bp.route('/playlists')
@login_required
def playlists_page():
    playlists = Playlist.query.order_by(Playlist.created_at.desc()).all()
    content_list = Content.query.all()
    return render_template('playlists.html', playlists=playlists, content_list=content_list)

@bp.route('/playlist/create', methods=['POST'])
@login_required
def create_playlist():
    data = request.json
    name = data.get('name')
    description = data.get('description', '')

    if not name:
        return jsonify({'error': 'Name required'}), 400

    playlist = Playlist(
        name=name,
        description=description
    )

    db.session.add(playlist)
    db.session.commit()

    return jsonify({'success': True, 'playlist': playlist.to_dict()})

@bp.route('/playlist/<int:playlist_id>/add_content', methods=['POST'])
@login_required
def add_content_to_playlist(playlist_id):
    data = request.json
    content_id = data.get('content_id')
    duration = data.get('duration')  # Optional duration override
    order = data.get('order')  # Optional explicit order

    playlist = Playlist.query.get(playlist_id)
    if not playlist:
        return jsonify({'error': 'Playlist not found'}), 404

    content = Content.query.get(content_id)
    if not content:
        return jsonify({'error': 'Content not found'}), 404

    # Use provided order or get next order number
    if order is None:
        max_order = db.session.query(db.func.max(PlaylistItem.order)).filter_by(playlist_id=playlist_id).scalar() or 0
        order = max_order + 1

    item = PlaylistItem(
        playlist_id=playlist_id,
        content_id=content_id,
        order=order,
        duration_override=duration  # Set duration override if provided
    )

    db.session.add(item)
    db.session.commit()

    return jsonify({'success': True, 'item': item.to_dict()})

@bp.route('/playlist/<int:playlist_id>/item/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_playlist_item(playlist_id, item_id):
    """Delete a specific item from a playlist"""
    item = PlaylistItem.query.filter_by(id=item_id, playlist_id=playlist_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'Playlist item not found'}), 404

@bp.route('/playlist/<int:playlist_id>/delete', methods=['POST'])
@login_required
def delete_playlist(playlist_id):
    playlist = Playlist.query.get(playlist_id)
    if playlist:
        # Remove items
        PlaylistItem.query.filter_by(playlist_id=playlist_id).delete()
        # Unassign from screens
        Screen.query.filter_by(current_playlist_id=playlist_id).update({'current_playlist_id': None})
        db.session.delete(playlist)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'Playlist not found'}), 404
