# Digital Signage System

A complete digital signage solution with central management server and display clients. Perfect for managing multiple screens showing images, videos, and web content.

## System Overview

This system consists of two main components:

1. **Server** - Central management server with web dashboard
2. **Client** - Display player for Ubuntu machines

```
┌─────────────────────────────────────┐
│     Management Server               │
│  - Web Admin Dashboard              │
│  - Content Management               │
│  - Playlist Creation                │
│  - Screen Management                │
└─────────────────┬───────────────────┘
                  │
                  │ API Communication
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼──────┐   ┌───────▼──────┐
│  Client 1    │   │  Client 2    │
│  (Screen)    │   │  (Screen)    │
│              │   │              │
│ - Display    │   │ - Display    │
│ - Content    │   │ - Content    │
└──────────────┘   └──────────────┘
```

## Features

### Server Features
- Web-based admin dashboard
- User authentication
- Content upload and management (images, videos)
- Webpage URL support
- Playlist creation and management
- Screen registration and monitoring
- Real-time status tracking
- Content scheduling

### Client Features
- Automatic server registration
- Fullscreen content display
- Image display with configurable duration
- Video playback
- Webpage rendering (planned)
- Content caching for offline operation
- Automatic content updates
- Heartbeat monitoring
- Auto-restart capability
- Playlist rotation

## Quick Start

### For Testing with 2 Ubuntu VMs

#### Server Setup (VM1)

1. Clone the repository:
```bash
git clone <your-repo-url> digital-signage
cd digital-signage/server
```

2. Start with Docker (recommended):
```bash
docker-compose up -d
```

Or install manually:
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres psql -c "CREATE DATABASE digital_signage;"
sudo -u postgres psql -c "CREATE USER signage WITH PASSWORD 'signage';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE digital_signage TO signage;"

# Install dependencies
pip install -r requirements.txt

# Run server
python app.py
```

3. Access admin dashboard:
```
http://localhost:5000
Username: admin
Password: admin123
```

#### Client Setup (VM2)

1. Clone the repository:
```bash
cd ~
git clone <your-repo-url> digital-signage
cd digital-signage/client
```

2. Run installation script:
```bash
chmod +x install.sh
./install.sh
```

3. Configure server URL:
```bash
nano config.json
```

Update to point to your server:
```json
{
  "server_url": "http://<server-ip>:5000",
  "name": "Test Display 1",
  "location": "Test Lab"
}
```

4. Test the player:
```bash
source venv/bin/activate
python player.py
```

5. Enable autostart:
```bash
sudo systemctl enable signage-player
sudo systemctl start signage-player
```

## Usage Workflow

### 1. Upload Content

1. Login to admin dashboard
2. Go to **Content** page
3. Upload images or videos
4. Set display duration for each item

### 2. Create Playlist

1. Go to **Playlists** page
2. Click "Create Playlist"
3. Add content items to playlist
4. Content will play in order

### 3. Assign to Screens

1. Go to **Screens** page
2. Find your registered screen
3. Select playlist from dropdown
4. Click "Assign"

The screen will automatically update and start playing the content!

## Repository Structure

```
digital-signage/
├── server/                    # Management Server
│   ├── app.py                # Main Flask application
│   ├── models.py             # Database models
│   ├── routes/               # API and admin routes
│   │   ├── api.py           # Client API endpoints
│   │   └── admin.py         # Admin web interface
│   ├── templates/            # HTML templates
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── content.html
│   │   ├── screens.html
│   │   └── playlists.html
│   ├── static/               # Static files and uploads
│   ├── requirements.txt      # Python dependencies
│   ├── docker-compose.yml    # Docker setup
│   ├── Dockerfile
│   └── README.md
│
├── client/                    # Display Client
│   ├── player.py             # Main player application
│   ├── config.json.example   # Configuration template
│   ├── requirements.txt      # Python dependencies
│   ├── install.sh            # Installation script
│   └── README.md
│
└── README.md                  # This file
```

## Network Requirements

### Firewall Rules

**Server:**
- Open port 5000 (or your configured port)
- Allow incoming connections from client network

**Clients:**
- Outgoing connections to server on port 5000

### Testing Connectivity

From client, test server connection:
```bash
curl http://server-ip:5000/api/screens
```

## System Requirements

### Server
- Ubuntu 20.04+ (or any Linux with Docker)
- 2GB RAM minimum
- 10GB+ disk space (depends on content)
- PostgreSQL 12+
- Python 3.8+

### Client
- Ubuntu 20.04+
- 2GB RAM minimum
- 5GB+ disk space for content cache
- Python 3.8+
- Display/monitor

## Configuration

### Server Configuration

Edit [server/.env](server/.env) or environment variables:

```bash
DATABASE_URL=postgresql://signage:signage@localhost/digital_signage
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
```

### Client Configuration

Edit [client/config.json](client/config.json):

```json
{
  "server_url": "http://server-ip:5000",
  "name": "Display Name",
  "location": "Physical Location",
  "poll_interval": 30,
  "heartbeat_interval": 60,
  "cache_dir": "/home/user/.signage_cache"
}
```

## API Documentation

### Client API Endpoints

**Register Screen**
```
POST /api/screen/register
{
  "identifier": "unique-id",
  "name": "Screen Name",
  "location": "Location"
}
```

**Get Content**
```
GET /api/screen/{identifier}/content
```

**Heartbeat**
```
POST /api/screen/{identifier}/heartbeat
```

**Upload Content**
```
POST /api/upload
Form data: file, name, duration
```

See [server/README.md](server/README.md) for complete API documentation.

## Troubleshooting

### Server Issues

**Database connection failed:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Verify connection string in .env
```

**Can't access admin dashboard:**
```bash
# Check server is running
ps aux | grep python

# Check firewall
sudo ufw status
sudo ufw allow 5000
```

### Client Issues

**Player won't start:**
```bash
# Check logs
sudo journalctl -u signage-player -f

# Test manually
source venv/bin/activate
python player.py
```

**Screen not appearing in dashboard:**
- Verify server URL in config.json
- Check network connectivity
- Verify firewall rules

**No content displaying:**
- Check if playlist is assigned in admin dashboard
- Verify content is in the playlist
- Check client logs for download errors

## Development

### Running in Development Mode

**Server:**
```bash
cd server
export FLASK_ENV=development
python app.py
```

**Client:**
```bash
cd client
source venv/bin/activate
python player.py
```

### Adding New Features

The codebase is structured for easy extension:
- Add new content types in [server/models.py](server/models.py)
- Add API endpoints in [server/routes/api.py](server/routes/api.py)
- Customize player in [client/player.py](client/player.py)

## Deployment

### Production Deployment

**Server:**
1. Use Docker Compose for easy deployment
2. Set strong SECRET_KEY
3. Enable HTTPS (use nginx as reverse proxy)
4. Set up automated backups
5. Configure firewall properly

**Client:**
1. Use systemd for auto-start
2. Configure auto-login for kiosk mode
3. Disable screen blanking
4. Set up remote monitoring

See individual README files for detailed deployment guides.

## Security Considerations

- Change default admin password immediately
- Use strong SECRET_KEY in production
- Enable HTTPS for production deployments
- Restrict database access
- Implement rate limiting on API endpoints
- Regular security updates
- Network isolation for clients

## Backup and Recovery

### Server Backup

```bash
# Backup database
pg_dump digital_signage > backup.sql

# Backup uploaded content
tar -czf content_backup.tar.gz server/static/uploads
```

### Restore

```bash
# Restore database
psql digital_signage < backup.sql

# Restore content
tar -xzf content_backup.tar.gz -C server/static/
```

## Performance Tips

1. **Server:**
   - Use SSD for content storage
   - Configure PostgreSQL for your hardware
   - Use CDN for large deployments
   - Enable caching

2. **Client:**
   - Use wired network connection
   - SSD for content cache
   - Disable unnecessary services
   - Lightweight desktop environment

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues or questions:
1. Check the troubleshooting sections
2. Review the logs
3. Check network connectivity
4. Verify configurations

## Roadmap

### Phase 2 (Current)
- ✅ Basic image display
- ✅ Video playback
- ✅ Playlist management
- ✅ Web dashboard
- 🔄 Webpage rendering (in progress)
- 🔄 Real-time updates via WebSocket

### Phase 3 (Planned)
- Multi-zone layouts
- Advanced scheduling (time-based, date-based)
- Content approval workflow
- User roles and permissions
- Advanced transitions and effects
- Mobile app for management
- Analytics and reporting

## License

MIT License - See LICENSE file for details

## Credits

Built with:
- Flask (Python web framework)
- PostgreSQL (Database)
- PyQt5 (GUI framework)
- Docker (Containerization)

---

**Getting Started:** Follow the Quick Start guide above to set up your test environment with 2 Ubuntu VMs!
