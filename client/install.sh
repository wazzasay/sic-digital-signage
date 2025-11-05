#!/bin/bash
# Digital Signage Player Installation Script for Ubuntu

set -e

echo "=================================="
echo "Digital Signage Player Installer"
echo "=================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Please do not run as root. Run as the user that will run the player."
    exit 1
fi

# Update system
echo "Updating system packages..."
sudo apt update

# Install system dependencies
echo "Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-venv git

# Install PyQt5 dependencies
echo "Installing PyQt5 dependencies..."
sudo apt install -y python3-pyqt5 python3-pyqt5.qtmultimedia libqt5multimedia5-plugins

# Create virtual environment (optional but recommended)
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "Installing Python packages..."
pip install -r requirements.txt

# Create config file if it doesn't exist
if [ ! -f config.json ]; then
    echo "Creating default config file..."
    cp config.json.example config.json
    echo "Please edit config.json with your server URL and screen details"
fi

# Create systemd service
echo "Creating systemd service..."
SERVICE_FILE="/etc/systemd/system/signage-player.service"
CURRENT_DIR=$(pwd)
USER=$(whoami)

sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Digital Signage Player
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$CURRENT_DIR
Environment="DISPLAY=:0"
Environment="XAUTHORITY=/home/$USER/.Xauthority"
ExecStart=$CURRENT_DIR/venv/bin/python $CURRENT_DIR/player.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

echo ""
echo "=================================="
echo "Installation complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit config.json with your server URL"
echo "   nano config.json"
echo ""
echo "2. Test the player:"
echo "   source venv/bin/activate"
echo "   python player.py"
echo ""
echo "3. Enable autostart:"
echo "   sudo systemctl enable signage-player"
echo "   sudo systemctl start signage-player"
echo ""
echo "4. Check status:"
echo "   sudo systemctl status signage-player"
echo ""
echo "5. View logs:"
echo "   sudo journalctl -u signage-player -f"
echo ""
