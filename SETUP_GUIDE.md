# Complete Setup Guide for 2 Ubuntu VMs

This guide will walk you through setting up the digital signage system with 2 Ubuntu VMs for testing.

## Prerequisites

- 2 Ubuntu VMs (20.04 or newer)
- Both VMs on the same network
- Git installed on both VMs
- Internet connection

## VM Setup

### VM1: Management Server
- Hostname: signage-server
- Recommended RAM: 2GB
- Disk: 20GB

### VM2: Display Client
- Hostname: signage-client
- Recommended RAM: 2GB
- Disk: 20GB

## Step-by-Step Setup

### Part 1: Server Setup (VM1)

#### 1. Install Git and Clone Repository

```bash
sudo apt update
sudo apt install -y git
cd ~
git clone <your-github-repo-url> digital-signage
cd digital-signage/server
```

#### 2. Option A: Quick Setup with Docker

```bash
# Install Docker
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER
newgrp docker

# Start services
docker-compose up -d

# Wait for services to start (about 30 seconds)
sleep 30

# Check status
docker-compose ps
```

#### 2. Option B: Manual Setup

```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib python3-pip

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql <<EOF
CREATE DATABASE digital_signage;
CREATE USER signage WITH PASSWORD 'signage';
GRANT ALL PRIVILEGES ON DATABASE digital_signage TO signage;
\q
EOF

# Install Python dependencies
pip3 install -r requirements.txt

# Run server
python3 app.py
```

#### 3. Verify Server is Running

```bash
# Check if server is responding
curl http://localhost:5000

# You should see a redirect to login page
```

#### 4. Get Server IP Address

```bash
# Note this IP - you'll need it for the client
ip addr show | grep "inet " | grep -v 127.0.0.1
```

Example output: `192.168.1.100`

#### 5. Configure Firewall (if enabled)

```bash
sudo ufw allow 5000/tcp
sudo ufw status
```

#### 6. Access Admin Dashboard

Open a web browser on VM1 or your host machine:
```
http://<server-ip>:5000
```

Login with:
- Username: `admin`
- Password: `admin123`

**Important:** Change this password after first login!

---

### Part 2: Client Setup (VM2)

#### 1. Install Git and Clone Repository

```bash
sudo apt update
sudo apt install -y git
cd ~
git clone <your-github-repo-url> digital-signage
cd digital-signage/client
```

#### 2. Run Installation Script

```bash
chmod +x install.sh
./install.sh
```

This will:
- Install system dependencies
- Install Python packages
- Create virtual environment
- Set up systemd service

#### 3. Configure Client

```bash
# Copy example config
cp config.json.example config.json

# Edit config with your server IP
nano config.json
```

Update the configuration:
```json
{
  "server_url": "http://192.168.1.100:5000",
  "name": "Test Display 1",
  "location": "Test Lab VM2",
  "poll_interval": 30,
  "heartbeat_interval": 60
}
```

Save and exit (Ctrl+X, Y, Enter)

#### 4. Test Client Manually

```bash
source venv/bin/activate
python player.py
```

You should see:
- Player window opens fullscreen
- Shows "No content assigned" message
- Console shows registration with server

Press ESC to exit.

#### 5. Verify Registration on Server

Back on VM1, check the admin dashboard:
1. Go to http://<server-ip>:5000/admin/screens
2. You should see "Test Display 1" registered
3. Note the status should be "Online"

#### 6. Enable Autostart

```bash
sudo systemctl enable signage-player
sudo systemctl start signage-player
```

#### 7. Check Service Status

```bash
sudo systemctl status signage-player
sudo journalctl -u signage-player -f
```

---

### Part 3: Test the System

Now let's test the complete workflow!

#### 1. Upload Content (on Server VM1)

1. In the admin dashboard, go to **Content** page
2. Click "Upload Content"
3. Fill in:
   - Name: "Test Image 1"
   - Duration: 10 seconds
   - File: Upload any image (JPG/PNG)
4. Click Upload

Repeat for 2-3 more images.

#### 2. Create Playlist

1. Go to **Playlists** page
2. Fill in:
   - Name: "Test Playlist"
   - Description: "Testing playlist rotation"
3. Click "Create Playlist"
4. In the playlist section:
   - Select content from dropdown
   - Click "Add Content" for each image
5. Repeat to add all images to the playlist

#### 3. Assign Playlist to Screen

1. Go to **Screens** page
2. Find "Test Display 1"
3. In the dropdown, select "Test Playlist"
4. Click "Assign"

#### 4. Watch the Magic!

On VM2, the display should:
- Automatically detect the new playlist (within 30 seconds)
- Download all content
- Start displaying images in order
- Rotate through the playlist continuously

---

## Testing Checklist

- [ ] Server is accessible at http://server-ip:5000
- [ ] Can login to admin dashboard
- [ ] Client VM is registered and shows "Online" status
- [ ] Content uploads successfully
- [ ] Playlist created with multiple items
- [ ] Playlist assigned to screen
- [ ] Client displays content automatically
- [ ] Content rotates through playlist
- [ ] Client service starts on boot

---

## Common Issues and Solutions

### Issue: Client can't reach server

**Solution:**
```bash
# On client, test connectivity
curl http://<server-ip>:5000/api/screens

# On server, check firewall
sudo ufw status
sudo ufw allow 5000/tcp

# Check server is listening
sudo netstat -tlnp | grep 5000
```

### Issue: Client shows as Offline

**Solution:**
```bash
# Check client service
sudo systemctl status signage-player

# Check logs
sudo journalctl -u signage-player -f

# Verify config.json has correct server URL
cat ~/digital-signage/client/config.json
```

### Issue: Content not displaying

**Solution:**
1. Check if playlist is assigned in admin dashboard
2. Check client logs: `sudo journalctl -u signage-player -f`
3. Verify content was uploaded successfully
4. Check cache directory: `ls -la ~/.signage_cache/`

### Issue: Database errors on server

**Solution:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check database connection
sudo -u postgres psql -c "\l" | grep digital_signage

# Recreate database if needed
sudo -u postgres psql <<EOF
DROP DATABASE IF EXISTS digital_signage;
CREATE DATABASE digital_signage;
GRANT ALL PRIVILEGES ON DATABASE digital_signage TO signage;
EOF
```

---

## Next Steps

Once you have the basic system working:

1. **Add More Clients**: Clone VM2 or repeat client setup on additional machines
2. **Test Video**: Upload MP4 video files and add to playlists
3. **Scheduling**: Add time-based scheduling to playlists
4. **Create Multiple Playlists**: Different content for different screens
5. **Monitor Performance**: Check logs and system resources

---

## Production Deployment Tips

When moving beyond testing:

1. **Server:**
   - Use proper domain name with SSL/HTTPS
   - Set up automated backups
   - Use stronger database password
   - Implement rate limiting
   - Set up monitoring (Prometheus, Grafana)

2. **Clients:**
   - Configure auto-login for kiosk mode
   - Disable screen blanking
   - Set up remote access (VPN)
   - Use wired network connections
   - Implement remote monitoring

3. **Network:**
   - Use VLANs for client isolation
   - Implement QoS for content delivery
   - Set up VPN for remote sites
   - Configure proper firewall rules

---

## Support

If you encounter issues:

1. Check the logs (both server and client)
2. Verify network connectivity
3. Check configuration files
4. Review firewall settings
5. Consult the main README.md and component READMEs

---

## Quick Reference

### Server URLs
- Admin Dashboard: `http://<server-ip>:5000`
- API Base: `http://<server-ip>:5000/api`

### Default Credentials
- Username: `admin`
- Password: `admin123`

### Important Directories
- Server uploads: `~/digital-signage/server/static/uploads/`
- Client cache: `~/.signage_cache/`
- Config: `~/digital-signage/client/config.json`

### Service Commands
```bash
# Client
sudo systemctl start|stop|restart|status signage-player
sudo journalctl -u signage-player -f

# Server (Docker)
docker-compose up -d
docker-compose down
docker-compose logs -f
```

---

Happy signage displaying!
