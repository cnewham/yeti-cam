#!/usr/bin/env bash

# Install python components

sudo apt-get update
sudo apt-get install build-essential python-dev

# Install 3rd party python packages

sudo pip install pickledb socketIO-client adafruit_python_dht picamera

# Set permissions

chmod +x /home/yeti/cam.py

# Install service

sudo cp yeticam.service /lib/systemd/system/
sudo chmod 644 /lib/systemd/system/yeticam.service
sudo systemctl daemon-reload
sudo systemctl enable yeticam.service
sudo systemctl start yeticam.service

# Add crontab to reboot daily at 2:09am (minutes staggered so multiple cams aren't sending on the same cadence)

sudo crontab -l | { cat; echo "9 2 0 0 0 reboot"; } | crontab -