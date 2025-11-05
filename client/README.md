# Digital Signage Player Client

Display client for the digital signage system. Runs on Ubuntu machines to display content from the central server.

## Features

- Automatic registration with server
- Fullscreen content display (images, videos, webpages)
- Automatic content downloading and caching
- Playlist support with transitions
- Heartbeat monitoring
- Auto-restart on failure
- Offline operation with cached content

## System Requirements

- Ubuntu 20.04 or newer
- Python 3.8+
- Network connection to server
- Display/monitor connected

## Installation

### Quick Install

1. Clone the repository:

```bash
cd ~
git clone <your-repo-url> signage-client
cd signage-client/client
```

2. Run the installation script:

```bash
chmod +x install.sh
./install.sh
```

3. Configure the player:

```bash
nano config.json
```

Update the `server_url` to point to your server:

```json
{
  "server_url": "http://192.168.1.100:5000",
  "name": "Display 1",
  "location": "Main Lobby"
}
```

4. Test the player:

```bash
source venv/bin/activate
python player.py
```

Press ESC or Q to exit fullscreen mode.

5. Enable autostart:

```bash
sudo systemctl enable signage-player
sudo systemctl start signage-player
```

## Configuration

### config.json

```json
{
  "server_url": "http://192.168.1.100:5000",
  "name": "Display 1",
  "location": "Main Lobby",
  "poll_interval": 30,
  "heartbeat_interval": 60,
  "cache_dir": "/home/signage/.signage_cache"
}
```

**Options:**

- `server_url`: URL of the management server
- `name`: Display name (shown in admin interface)
- `location`: Physical location of the display
- `poll_interval`: How often to check for new content (seconds)
- `heartbeat_interval`: How often to send heartbeat (seconds)
- `cache_dir`: Directory for cached content

The `identifier` is automatically generated and saved on first run.

## Usage

### Manual Start

```bash
source venv/bin/activate
python player.py
```

### Keyboard Controls

- **ESC** or **Q**: Exit fullscreen/quit
- **F**: Toggle fullscreen mode

### Service Management

Start the service:
```bash
sudo systemctl start signage-player
```

Stop the service:
```bash
sudo systemctl stop signage-player
```

Restart the service:
```bash
sudo systemctl restart signage-player
```

Check status:
```bash
sudo systemctl status signage-player
```

View logs:
```bash
sudo journalctl -u signage-player -f
```

## Autostart on Boot

### Enable Service

```bash
sudo systemctl enable signage-player
```

### Configure Auto-Login (Optional)

For dedicated signage displays, you may want to auto-login and start the player:

1. Edit lightdm config:

```bash
sudo nano /etc/lightdm/lightdm.conf
```

2. Add under `[Seat:*]`:

```ini
autologin-user=your-username
autologin-user-timeout=0
```

3. Restart:

```bash
sudo systemctl restart lightdm
```

### Disable Screen Blanking

To prevent the screen from turning off:

```bash
# Add to ~/.xsessionrc
xset s off
xset -dpms
xset s noblank
```

## Troubleshooting

### Player Won't Start

Check the service logs:
```bash
sudo journalctl -u signage-player -f
```

Common issues:
- Wrong server URL in config.json
- Server not reachable (check firewall, network)
- Missing Python dependencies

### Display Issues

Check if PyQt5 is installed correctly:
```bash
python3 -c "from PyQt5 import QtWidgets"
```

If this fails, reinstall PyQt5:
```bash
sudo apt install python3-pyqt5
```

### No Content Showing

1. Check if the screen is registered:
   - Go to server admin interface
   - Check Screens page
   - Look for your screen (by name or identifier)

2. Verify a playlist is assigned:
   - In the Screens page, assign a playlist to your screen

3. Check content cache:
```bash
ls -la ~/.signage_cache/
```

### Network Issues

Test server connectivity:
```bash
curl http://your-server:5000/api/screens
```

Check firewall rules on both client and server.

## Updating

To update the player:

```bash
cd ~/signage-client/client
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart signage-player
```

## Uninstallation

```bash
# Stop and disable service
sudo systemctl stop signage-player
sudo systemctl disable signage-player
sudo rm /etc/systemd/system/signage-player.service
sudo systemctl daemon-reload

# Remove files
cd ~
rm -rf signage-client
rm -rf ~/.signage_cache
```

## Development

### Running Without GUI

If you want to test without a display:

```bash
# Uninstall PyQt5 temporarily
pip uninstall PyQt5

# Run in fallback mode
python player.py
```

The player will run in text-only mode, showing status updates in the terminal.

### Custom Display Logic

Modify `player.py` to customize:
- Content display duration
- Transition effects
- Error handling
- Status reporting

## Performance Tips

1. **Use SSD for cache**: Faster content loading
2. **Wired network**: More reliable than Wi-Fi
3. **Disable unnecessary services**: Frees up resources
4. **Use lightweight desktop**: XFCE or LXDE instead of GNOME

## Security Notes

- Player runs as regular user (not root)
- No SSH access required after setup
- Content is cached locally (ensure adequate disk space)
- Consider VPN for remote displays

## Support

For issues or questions:
1. Check the logs: `sudo journalctl -u signage-player -f`
2. Verify server connection
3. Check server-side logs
4. Review configuration files

## License

MIT License
