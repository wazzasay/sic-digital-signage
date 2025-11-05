#!/usr/bin/env python3
"""
Digital Signage Player Client
Displays content from the central management server
"""

import os
import sys
import time
import json
import uuid
import requests
import subprocess
from pathlib import Path
from datetime import datetime
import threading

# Try to import PyQt5 for GUI
try:
    from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
    from PyQt5.QtGui import QPixmap, QMovie
    from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
    from PyQt5.QtMultimediaWidgets import QVideoWidget
    from PyQt5.QtCore import QUrl
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("PyQt5 not available, using fallback display mode")

class Config:
    """Configuration management"""

    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        """Load configuration from file"""
        default_config = {
            'server_url': 'http://localhost:5000',
            'identifier': str(uuid.uuid4()),
            'name': f'Player-{os.uname().nodename}',
            'location': '',
            'poll_interval': 30,  # seconds
            'heartbeat_interval': 60,  # seconds
            'cache_dir': str(Path.home() / '.signage_cache')
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                print(f"Error loading config: {e}")

        # Save config (creates file if it doesn't exist)
        self.save_config(default_config)

        return default_config

    def save_config(self, config=None):
        """Save configuration to file"""
        if config:
            self.config = config

        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key, default=None):
        """Get configuration value"""
        return self.config.get(key, default)

    def set(self, key, value):
        """Set configuration value"""
        self.config[key] = value
        self.save_config()


class ContentManager:
    """Manages content downloading and caching"""

    def __init__(self, config):
        self.config = config
        self.cache_dir = Path(config.get('cache_dir'))
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_content_path(self, content_id, filename):
        """Get local path for cached content"""
        return self.cache_dir / f"{content_id}_{filename}"

    def download_content(self, content):
        """Download content if not cached"""
        content_id = content['id']
        filename = content['file_path']

        local_path = self.get_content_path(content_id, filename)

        # Check if already cached
        if local_path.exists():
            return str(local_path)

        # Download from server
        try:
            server_url = self.config.get('server_url')
            download_url = f"{server_url}/api/content/{content_id}/download"

            print(f"Downloading content: {content['name']}")

            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()

            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"Downloaded: {local_path}")
            return str(local_path)

        except Exception as e:
            print(f"Error downloading content: {e}")
            return None


class ServerCommunicator:
    """Handles communication with the server"""

    def __init__(self, config):
        self.config = config
        self.server_url = config.get('server_url')
        self.identifier = config.get('identifier')

    def register(self):
        """Register this screen with the server"""
        try:
            url = f"{self.server_url}/api/screen/register"
            data = {
                'identifier': self.identifier,
                'name': self.config.get('name'),
                'location': self.config.get('location')
            }

            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()

            print(f"Registered with server: {self.config.get('name')}")
            return True

        except Exception as e:
            print(f"Error registering with server: {e}")
            return False

    def send_heartbeat(self):
        """Send heartbeat to server"""
        try:
            url = f"{self.server_url}/api/screen/{self.identifier}/heartbeat"
            response = requests.post(url, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error sending heartbeat: {e}")
            return False

    def get_content(self):
        """Get assigned content from server"""
        try:
            url = f"{self.server_url}/api/screen/{self.identifier}/content"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            return data

        except Exception as e:
            print(f"Error getting content: {e}")
            return None


class SignalEmitter(QObject):
    """Signal emitter for thread-safe GUI updates"""
    content_updated = pyqtSignal(list)


class SignagePlayer(QMainWindow):
    """Main signage player application with PyQt5 GUI"""

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.content_manager = ContentManager(config)
        self.server_comm = ServerCommunicator(config)
        self.current_playlist = []
        self.current_index = 0

        # Signal emitter for thread-safe updates
        self.signal_emitter = SignalEmitter()
        self.signal_emitter.content_updated.connect(self.update_playlist)

        self.init_ui()
        self.start_background_tasks()

        # Register with server
        self.server_comm.register()

        # Initial content fetch
        self.fetch_content()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle('Digital Signage Player')
        self.showFullScreen()
        self.setCursor(Qt.BlankCursor)  # Hide cursor

        # Main label for images
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: black;")
        self.image_label.setScaledContents(True)
        self.setCentralWidget(self.image_label)

        # Video player (hidden by default)
        self.video_widget = QVideoWidget(self)
        self.video_widget.hide()
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.mediaStatusChanged.connect(self.on_video_finished)

        # Content display timer
        self.display_timer = QTimer()
        self.display_timer.timeout.connect(self.show_next_content)

    def start_background_tasks(self):
        """Start background threads for server communication"""
        # Heartbeat thread
        def heartbeat_loop():
            while True:
                time.sleep(self.config.get('heartbeat_interval', 60))
                self.server_comm.send_heartbeat()

        heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
        heartbeat_thread.start()

        # Content polling thread
        def content_poll_loop():
            while True:
                time.sleep(self.config.get('poll_interval', 30))
                self.fetch_content()

        poll_thread = threading.Thread(target=content_poll_loop, daemon=True)
        poll_thread.start()

    def fetch_content(self):
        """Fetch content from server in background"""
        def fetch():
            data = self.server_comm.get_content()
            if data and data.get('items'):
                items = data['items']
                # Download all content
                playlist = []
                for item in items:
                    content = item['content']
                    if content['content_type'] in ['image', 'video']:
                        local_path = self.content_manager.download_content(content)
                        if local_path:
                            content['local_path'] = local_path
                            playlist.append(content)
                    elif content['content_type'] == 'webpage':
                        playlist.append(content)

                if playlist:
                    self.signal_emitter.content_updated.emit(playlist)

        fetch_thread = threading.Thread(target=fetch, daemon=True)
        fetch_thread.start()

    def update_playlist(self, playlist):
        """Update the current playlist (called from main thread)"""
        print(f"Playlist updated with {len(playlist)} items")
        self.current_playlist = playlist
        self.current_index = 0

        # Stop current playback and start new playlist
        self.display_timer.stop()
        self.media_player.stop()

        if self.current_playlist:
            self.show_next_content()

    def show_next_content(self):
        """Display the next content item"""
        if not self.current_playlist:
            # Show default "No content" message
            self.show_no_content_message()
            return

        content = self.current_playlist[self.current_index]

        print(f"Displaying: {content['name']} ({content['content_type']})")

        if content['content_type'] == 'image':
            self.show_image(content)
        elif content['content_type'] == 'video':
            self.show_video(content)
        elif content['content_type'] == 'webpage':
            self.show_webpage(content)

        # Move to next item
        self.current_index = (self.current_index + 1) % len(self.current_playlist)

    def show_image(self, content):
        """Display an image"""
        self.video_widget.hide()
        self.image_label.show()

        pixmap = QPixmap(content['local_path'])
        scaled_pixmap = pixmap.scaled(
            self.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)

        # Set timer for next content
        duration = content.get('duration', 10) * 1000  # Convert to milliseconds
        self.display_timer.start(duration)

    def show_video(self, content):
        """Display a video"""
        self.image_label.hide()
        self.video_widget.show()
        self.video_widget.setGeometry(self.rect())

        media = QMediaContent(QUrl.fromLocalFile(content['local_path']))
        self.media_player.setMedia(media)
        self.media_player.play()

    def on_video_finished(self, status):
        """Handle video playback completion"""
        if status == QMediaPlayer.EndOfMedia:
            self.video_widget.hide()
            self.show_next_content()

    def show_webpage(self, content):
        """Display a webpage (placeholder - would need QWebEngineView)"""
        # For now, show URL as text
        self.video_widget.hide()
        self.image_label.show()
        self.image_label.setText(f"Webpage:\n{content['file_path']}")

        duration = content.get('duration', 10) * 1000
        self.display_timer.start(duration)

    def show_no_content_message(self):
        """Show message when no content is assigned"""
        self.video_widget.hide()
        self.image_label.show()
        self.image_label.setText(
            f"Digital Signage Player\n\n"
            f"Screen: {self.config.get('name')}\n"
            f"ID: {self.config.get('identifier')[:16]}...\n\n"
            f"No content assigned\n"
            f"Waiting for content from server..."
        )
        self.image_label.setStyleSheet(
            "background-color: black; color: white; font-size: 24px;"
        )

        # Check again in 30 seconds
        self.display_timer.start(30000)

    def keyPressEvent(self, event):
        """Handle key presses"""
        if event.key() == Qt.Key_Escape or event.key() == Qt.Key_Q:
            self.close()
        elif event.key() == Qt.Key_F:
            # Toggle fullscreen
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()


class FallbackPlayer:
    """Simple fallback player when PyQt5 is not available"""

    def __init__(self, config):
        self.config = config
        self.content_manager = ContentManager(config)
        self.server_comm = ServerCommunicator(config)

        print("Starting in fallback mode (text only)")
        print("Install PyQt5 for full GUI support: pip install PyQt5")

        # Register with server
        self.server_comm.register()

        self.run()

    def run(self):
        """Main loop for fallback mode"""
        while True:
            try:
                # Get content
                data = self.server_comm.get_content()

                if data and data.get('items'):
                    print(f"\n=== Playlist: {len(data['items'])} items ===")
                    for item in data['items']:
                        content = item['content']
                        print(f"  - {content['name']} ({content['content_type']})")
                else:
                    print("\nNo content assigned")

                # Send heartbeat
                self.server_comm.send_heartbeat()

                # Wait before next check
                time.sleep(self.config.get('poll_interval', 30))

            except KeyboardInterrupt:
                print("\nShutting down...")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(10)


def main():
    """Main entry point"""
    # Load configuration
    config = Config()

    print("=" * 50)
    print("Digital Signage Player")
    print("=" * 50)
    print(f"Screen: {config.get('name')}")
    print(f"ID: {config.get('identifier')}")
    print(f"Server: {config.get('server_url')}")
    print("=" * 50)

    if PYQT_AVAILABLE:
        # Run with GUI
        app = QApplication(sys.argv)
        player = SignagePlayer(config)
        player.show()
        sys.exit(app.exec_())
    else:
        # Run in fallback mode
        player = FallbackPlayer(config)


if __name__ == '__main__':
    main()
