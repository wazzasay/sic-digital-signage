from datetime import datetime
from database import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

class Screen(db.Model):
    __tablename__ = 'screens'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    identifier = db.Column(db.String(100), unique=True, nullable=False)  # Unique machine ID
    location = db.Column(db.String(200))
    status = db.Column(db.String(20), default='offline')  # online, offline
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    current_playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    current_playlist = db.relationship('Playlist', foreign_keys=[current_playlist_id])

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'identifier': self.identifier,
            'location': self.location,
            'status': self.status,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'current_playlist_id': self.current_playlist_id,
            'created_at': self.created_at.isoformat()
        }

class Content(db.Model):
    __tablename__ = 'content'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    content_type = db.Column(db.String(20), nullable=False)  # image, video, webpage
    file_path = db.Column(db.String(500))  # Path for images/videos, URL for webpages
    duration = db.Column(db.Integer, default=10)  # Display duration in seconds
    file_size = db.Column(db.Integer)  # Size in bytes
    mime_type = db.Column(db.String(100))
    display_mode = db.Column(db.String(20), default='fit')  # 'fit' (letterbox) or 'fill' (crop)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'content_type': self.content_type,
            'file_path': self.file_path,
            'duration': self.duration,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'display_mode': self.display_mode,
            'created_at': self.created_at.isoformat()
        }

class Playlist(db.Model):
    __tablename__ = 'playlists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    transition_effect = db.Column(db.String(50), default='fade')  # fade, slide, none
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    items = db.relationship('PlaylistItem', backref='playlist', lazy=True, order_by='PlaylistItem.order')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'transition_effect': self.transition_effect,
            'items': [item.to_dict() for item in self.items],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class PlaylistItem(db.Model):
    __tablename__ = 'playlist_items'

    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id'), nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id'), nullable=False)
    order = db.Column(db.Integer, nullable=False)
    duration_override = db.Column(db.Integer)  # Override content's default duration (seconds)
    schedule_start = db.Column(db.Time)  # Optional: only show during certain times
    schedule_end = db.Column(db.Time)

    content = db.relationship('Content')

    def to_dict(self):
        # Use duration_override if set, otherwise use content's default duration
        duration = self.duration_override if self.duration_override is not None else self.content.duration

        return {
            'id': self.id,
            'playlist_id': self.playlist_id,
            'content_id': self.content_id,
            'content': self.content.to_dict(),
            'order': self.order,
            'duration': duration,
            'duration_override': self.duration_override,
            'schedule_start': self.schedule_start.isoformat() if self.schedule_start else None,
            'schedule_end': self.schedule_end.isoformat() if self.schedule_end else None
        }
