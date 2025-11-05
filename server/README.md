# Digital Signage Server

Central management server for the digital signage system.

## Features

- Web-based admin dashboard
- Content management (images, videos, webpages)
- Playlist creation and scheduling
- Screen management and monitoring
- User authentication
- RESTful API for client communication

## Quick Start

### Option 1: Docker (Recommended)

1. Install Docker and Docker Compose
2. Start the server:

```bash
docker-compose up -d
```

The server will be available at `http://localhost:5000`

### Option 2: Manual Installation

1. Install PostgreSQL:

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

2. Create database:

```bash
sudo -u postgres psql
CREATE DATABASE digital_signage;
CREATE USER signage WITH PASSWORD 'signage';
GRANT ALL PRIVILEGES ON DATABASE digital_signage TO signage;
\q
```

3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the server:

```bash
python app.py
```

## Default Credentials

- **Username**: admin
- **Password**: admin123

**Important**: Change the default password after first login!

## API Endpoints

### Client Registration

**POST** `/api/screen/register`
```json
{
  "identifier": "unique-machine-id",
  "name": "Display 1",
  "location": "Main Lobby"
}
```

### Get Screen Content

**GET** `/api/screen/{identifier}/content`

Returns the playlist and content items assigned to the screen.

### Heartbeat

**POST** `/api/screen/{identifier}/heartbeat`

Updates the screen's last seen timestamp.

### Upload Content

**POST** `/api/upload`

Form data:
- `file`: The file to upload
- `name`: Content name
- `duration`: Display duration in seconds

## Configuration

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Flask secret key for sessions
- `FLASK_ENV`: development or production

### Upload Limits

Maximum file size: 500MB (configurable in app.py)

Supported formats:
- Images: PNG, JPG, JPEG, GIF, BMP
- Videos: MP4, AVI, MOV, WebM, MKV

## Administration

### Dashboard

Access the web dashboard at `http://your-server:5000/admin/dashboard`

Features:
- View registered screens and their status
- Upload and manage content
- Create and manage playlists
- Assign playlists to screens

### Managing Screens

Screens automatically register when they first connect. You can:
- Assign playlists to screens
- Monitor screen status (online/offline)
- View last seen timestamps

### Content Management

Upload content through the web interface. Content can be:
- Images (displayed for specified duration)
- Videos (duration determined by video length)
- Webpages (URLs, displayed for specified duration)

### Playlists

Create playlists and add content in any order. Playlists can be assigned to one or more screens.

## Troubleshooting

### Database Connection Issues

Check that PostgreSQL is running:
```bash
sudo systemctl status postgresql
```

Verify connection string in `.env` or environment variables.

### Upload Failures

Check disk space and file permissions:
```bash
df -h
ls -la static/uploads
```

Ensure the uploads directory is writable by the application user.

### Screen Not Appearing

- Verify the client can reach the server (check firewall rules)
- Check server logs for connection attempts
- Ensure the client has the correct server URL configured

## Development

### Database Migrations

When modifying models, the database will be automatically updated when the app starts. For production, consider using Flask-Migrate for proper migrations.

### Adding New Features

The application follows a standard Flask structure:
- `app.py`: Main application and initialization
- `models.py`: Database models
- `routes/`: API and admin route blueprints
- `templates/`: HTML templates for the web interface

## Security Notes

- Change default admin password immediately
- Use strong SECRET_KEY in production
- Enable HTTPS in production
- Consider implementing rate limiting for API endpoints
- Regularly update dependencies

## License

MIT License
